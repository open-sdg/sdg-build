import os
import json
import copy
from urllib.request import urlopen
import sdg
import pandas as pd
from sdg.outputs import OutputBase

class OutputGeoJson(OutputBase):
    """Output SDG data/metadata in GeoJson disaggregated by region."""


    def __init__(self, inputs, schema, output_folder='_site', translations=None,
        geojson_file='regions.geojson', name_property='name', id_property='id',
        id_column='GeoCode', output_subfolder='regions', filename_prefix='indicator_',
        exclude_columns=None, id_replacements=None, indicator_options=None):
        """Constructor for OutputGeoJson.

        Parameters
        ----------

        Inherits all the parameters from OutputBase, plus the following optional
        arguments (see above for the default values):

        geojson_file : string
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
        output_subfolder : string
            A folder beneath 'geojson' to put the files. The full path will be:
            [output_folder]/geojson/[output_subfolder]/[indicator_id].geojson
        filename_prefix : string
            A prefix added before the indicator id to construct a filename for
            each geojson file.
        exclude_columns : list
            A list of strings, each a column name in the indicator data that
            should not be included in the disaggregation. This is typically
            for any columns that mirror the region referenced by the id column.
        id_replacements : dict
            An optional for with replacements to apply to the values in
            the id_column. This is typically used if another column exists which
            "mirrors" what would be in an id column, to avoid duplicate work.
            For example, maybe a "Region" column exists with the names of the
            regions as values. This can be used to "map" those region names to
            geocodes, and save you the work of maintaining a separate id column.
        """
        if translations is None:
            translations = []
        if exclude_columns is None:
            exclude_columns = []
        if id_replacements is None:
            id_replacements = {}

        OutputBase.__init__(self, inputs, schema, output_folder, translations, indicator_options)
        self.geojson_file = geojson_file
        self.name_property = name_property
        self.id_property = id_property
        self.id_column = id_column
        self.output_subfolder = output_subfolder
        self.filename_prefix = filename_prefix
        self.exclude_columns = exclude_columns
        self.id_replacements = id_replacements
        self.geometry_data = self.fetch_geometry_data()


    def fetch_geometry_data(self):
        """Grab the data referenced by the "geojson_file" parameter.

        Returns
        -------
        dict
            Parsed JSON as a Python dict.
        """
        file = None
        data = None
        if self.geojson_file.startswith('http'):
            file = urlopen(self.geojson_file)
            data = file.read().decode('utf-8')
        else:
            file = open(self.geojson_file)
            data = file.read()
        file.close()

        data = json.loads(data)
        return data


    def indicator_has_geocodes(self, indicator):
        """Determine if an indicator has geographical data.

        Parameters
        ----------
        indicator : Indicator object
            An Indicator object to examine.

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

        for indicator_id in self.get_indicator_ids():
            indicator = self.get_indicator_by_id(indicator_id)

            if not self.indicator_has_geocodes(indicator):
                continue

            series_by_geocodes = self.get_series_by_geocodes(indicator)
            geometry_data = copy.deepcopy(self.geometry_data)

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
                # Figure out a "headline" so we can move it to the front of the list.
                headline_index = self.get_headline_index(disaggregations)
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
            filename = self.filename_prefix + indicator_id + '.geojson'
            filepath = os.path.join(target_folder, filename)
            with open(filepath, 'w') as f:
                json.dump(geometry_data, f)

        return status


    def get_series_by_geocodes(self, indicator):
        """Get a dict of lists of Series objects, keyed by geocode ids.

        Parameters
        ----------
        indicator : Indicator
            An instance of the Indicator class.

        Returns
        -------
        dict
            Lists of instances of the Series class, keyed by geocode id.
        """
        series_by_geocodes = {}
        for series in indicator.get_all_series():
            if series.has_disaggregation(self.id_column):
                geocode = series.get_disaggregation(self.id_column)
                geocode = self.replace_geocode(geocode)
                if geocode not in series_by_geocodes:
                    series_by_geocodes[geocode] = []
                series_by_geocodes[geocode].append(series)
        return series_by_geocodes


    def clean_disaggregations(self, disaggregations):
        """Apply any modifications to disaggregations before saving them into
        the GeoJSON file.

        Parameters
        ----------
        disaggregations : dict
            A dict of disaggregations, with category keyed to subcategory.

        Returns
        -------
        dict
            A modified version of the disaggregations dict.
        """
        # We don't need the actual geocode column.
        del disaggregations[self.id_column]
        # Remove any others necessary.
        for column in self.exclude_columns:
            if column in disaggregations:
                del disaggregations[column]
        # Convert null/nan/etc into just null.
        for key in disaggregations:
            if pd.isna(disaggregations[key]):
                disaggregations[key] = None
        return disaggregations


    def get_headline_index(self, disaggregations):
        """Figure out a "headline" from a list of disaggregations.

        Parameters
        ----------
        disaggregations : list
            A list of disaggregations dicts (categories keyed to subcategory).

        Returns
        -------
        int
            The index of the disaggregation chosen to be the headline.
        """
        # We need to figure out which series to mark as the "headline". Try
        # to find one with the smallest amount of disaggregation.
        headline_scores = {}
        for disagg_index, disaggregation in enumerate(disaggregations):
            num_disaggregations = 0
            for key in disaggregation:
                if not pd.isna(disaggregation[key]):
                    num_disaggregations += 1
            headline_scores[disagg_index] = num_disaggregations
        return min(headline_scores, key=headline_scores.get)


    def replace_geocode(self, geocode):
        """Make any replaces of geocodes, according to the id_replacements.

        Parameters
        ----------
        geocode : string
            A geocode to look for a replacement for.

        Returns
        -------
        string
            The replaced geocode, or the original, if no replacement was found.
        """
        if geocode in self.id_replacements:
            return self.id_replacements[geocode]
        return geocode


    def validate(self):
        """Validate geojson-related source data. Overrides parent.

        This output does not currently test general data and metadata, as it is
        assumed that this is a supplemental output, and that another output will
        validate all of that.
        """

        status = True

        # Make sure the geojson_file has the required properties on each feature.
        for index, feature in enumerate(self.geometry_data['features']):
            feature_is_bad = False
            if self.name_property not in feature['properties']:
                print('Name property "' + self.name_property + '" not found in feature:')
                feature_is_bad = True
            if self.id_property not in feature['properties']:
                print('ID property "' + self.id_property + '" not found in feature:')
                feature_is_bad = True
            if feature_is_bad:
                print(feature['properties'])
                status = False

        # Make sure at least one indicator has geocodes.
        if not self.geocodes_exist():
            print('No indicators have data under "' + self.id_column + '".')
            status = False

        return status


    def geocodes_exist(self):
        """Check to see if at least one indicator in this output contains geocodes."""
        no_indicators_have_geocodes = True
        for indicator_id in self.get_indicator_ids():
            if self.indicator_has_geocodes(self.get_indicator_by_id(indicator_id)):
                no_indicators_have_geocodes = False
                break

        return False if no_indicators_have_geocodes else True


    def get_documentation_title(self):
        return 'GeoJSON output - ' + self.output_subfolder


    def get_documentation_content(self, languages=None, baseurl=''):
        if languages is None:
            languages = ['']

        indicator_ids = self.get_documentation_indicator_ids()

        endpoint = '{language}/geojson/{folder}/indicator_{indicator_id}.geojson'
        output = '<p>' + self.get_documentation_description() + ' Examples are below:<p>'
        output += '<ul>'
        for language in languages:
            for indicator_id in indicator_ids:
                path = endpoint.format(language=language, indicator_id=indicator_id, folder=self.output_subfolder)
                output += '<li><a href="' + baseurl + path + '">' + path + '</a></li>'
        output += '<li>etc...</li>'
        output += '</ul>'

        return output


    def get_documentation_indicator_ids(self):
        indicator_ids = []
        for indicator_id in self.get_indicator_ids():
            if len(indicator_ids) > 2:
                break
            indicator = self.get_indicator_by_id(indicator_id)
            if not self.indicator_has_geocodes(indicator):
                continue
            indicator_ids.append(indicator_id)
        return indicator_ids


    def get_documentation_description(self):
        return 'This output contains GeoJSON for those indicators that have geocoded data.'
