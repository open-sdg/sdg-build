import os
import json
import copy
from urllib.request import urlopen
import sdg
import pandas as pd
from sdg.outputs import OutputBase

class OutputGeoJson(OutputBase):
    """Output SDG data/metadata in GeoJson disaggregated by region."""


    def __init__(self, inputs, schema, output_folder='_site', translations=[],
        geometry_file='regions.geojson', name_property='name', id_property='id',
        id_column='GeoCode', output_subfolder='regions'):
        """Constructor for OutputGeoJson.

        Parameters
        ----------

        Inherits all the parameters from OutputBase, plus the following:

        geometry_file : string
            A path to a GeoJSON file (remote or local) which contains all of the
            "geometries" for the regions to include. Each region should have an
            id and a name, in properties (see name_property and id_property).
        name_property : string
            The property in the geometry file which contains the region's name.
        id_property : string
            The property in the geometry file which contains the region's id.
        id_column : string
            The name of a column in the indicator data which corresponds to the
            id that is in the "id_property" of the geometry file. This serves to
            "join" the indicator data with the geometry file.
        """
        OutputBase.__init__(self, inputs, schema, output_folder, translations)
        self.geometry_file = geometry_file
        self.name_property = name_property
        self.id_property = id_property
        self.id_column = id_column
        self.geometry_data = self.fetch_geometry_data()


    def fetch_geometry_data(self):
        """Grab the data referenced by the "geometry_file" parameter.

        Returns
        -------
        dict
            Parsed JSON as a Python dict.
        """
        file = None
        data = None
        if self.geometry_file.startswith('http'):
            file = urlopen(self.geometry_file)
            data = file.read().decode('utf-8')
        else:
            file = open(self.geometry_file)
            data = file.read()
        file.close()

        data = json.loads(data)
        return data


    def indicator_has_geocodes(self, indicator):
        """Determine if an indicator has geographical data.

        Returns
        -------
        boolean
            True if the indicator has geographical data, False otherwise.
        """
        # Make sure the indicator has data at all.
        if not indicator.has_data():
            return False
        # Make sure the indicator has a geocode column.
        cols = indicator.data.columns
        if self.id_column not in cols:
            return False
        # Make sure that column has data in it.
        return indicator.data[self.id_column].any()


    def build(self, language=None):
        """Write the GeoJSON output. Overrides parent."""
        status = True

        target_folder = os.path.join(self.output_folder, 'geojson', self.output_subfolder)
        if not os.path.exists(target_folder):
            os.makedirs(target_folder, exist_ok=True)

        for inid in self.indicators:
            indicator = self.indicators[inid]
            if self.indicator_has_geocodes(indicator):
                series_by_geocodes = {}
                geometry_data = copy.deepcopy(self.geometry_data)
                for series in indicator.get_all_series():
                    if series.has_disaggregation(self.id_column):
                        geocode = series.get_disaggregation(self.id_column)
                        if geocode not in series_by_geocodes:
                            series_by_geocodes[geocode] = []
                        series_by_geocodes[geocode].append(series)

                # Loop through the features.
                for index, feature in enumerate(geometry_data['features']):
                    geocode = feature['properties'][self.id_property]
                    # If there are no series for this geocode, skip it.
                    if geocode not in series_by_geocodes:
                        continue
                    disaggregations = [series.get_disaggregations() for series in series_by_geocodes[geocode]]
                    values = [series.get_values() for series in series_by_geocodes[geocode]]
                    # Do some cleanup of the disaggregations.
                    disaggregations = [self.clean_disaggregations(disaggregation) for disaggregation in disaggregations]
                    # We need to figure out which series to mark as the "headline". Try
                    # to find one with the smallest amount of disaggregation.
                    headline_scores = {}
                    for disagg_index, disaggregation in enumerate(disaggregations):
                        num_disaggregations = 0
                        for key in disaggregation:
                            if not pd.isna(disaggregation[key]):
                                num_disaggregations += 1
                        headline_scores[disagg_index] = num_disaggregations
                    headline_index = min(headline_scores, key=headline_scores.get)
                    # Rather than introduce more complexity, just move the "headline"
                    # to the front of the lists.
                    disaggregations.insert(0, disaggregations.pop(headline_index))
                    values.insert(0, values.pop(headline_index))
                    # Set these lists on the GeoJSON data structure.
                    geometry_data['features'][index]['properties']['disaggregations'] = disaggregations
                    geometry_data['features'][index]['properties']['values'] = values
                    # Translate the name, if necessary using a 'data' group.
                    feature_name = feature['properties'][self.name_property]
                    feature_name = self.translation_helper.translate(feature_name, language, default_group='data')
                    # Normalize the id and name properties.
                    geometry_data['features'][index]['properties']['name'] = feature_name
                    geometry_data['features'][index]['properties']['geocode'] = feature['properties'][self.id_property]
                    del geometry_data['features'][index]['properties'][self.name_property]
                    del geometry_data['features'][index]['properties'][self.id_property]
                # Finally write the updated GeoJSON file.
                filename = inid + '.geojson'
                filepath = os.path.join(target_folder, filename)
                with open(filepath, 'w') as f:
                    json.dump(geometry_data, f)

        return status


    def clean_disaggregations(self, disaggregations):
        # We don't need the actual geocode column.
        del disaggregations[self.id_column]
        # Convert null/nan/etc into just null.
        for key in disaggregations:
            if pd.isna(disaggregations[key]):
                disaggregations[key] = None
        return disaggregations
