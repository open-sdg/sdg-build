import pandas as pd
import sdg
import requests
from sdg.inputs import InputBase

class InputSdmxJsonApi(InputBase):
    """Sources of SDG data that are remote SDMX JSON endpoint."""

    def __init__(self,
                 endpoint='',
                 drop_dimensions=[],
                 drop_singleton_dimensions=True,
                 dimension_map={},
                 indicator_map={}):
        """Constructor for InputSdmxJsonApi.

        Parameters
        ----------
        endpoint : string
            Remote URL of the SDMX API endpoint
        drop_dimensions : list
            List of SDMX dimensions/attributes to ignore
        drop_singleton_dimensions : boolean
            If True, drop dimensions/attributes with only 1 variation
        dimension_map : dict
            A dict for mapping SDMX ids to human-readable names. For dimension
            names, the key is simply the dimension id. For dimension value names,
            the key is the dimension id and value id, separated by a pipe (|).
            This also includes attributes.
        indicator_map : dict
            A dict for mapping SDMX ids to indicator ids, dash-delimited.
        """
        self.endpoint = endpoint
        self.drop_dimensions = drop_dimensions
        self.drop_singleton_dimensions = drop_singleton_dimensions
        self.dimension_map = dimension_map
        self.indicator_map = indicator_map
        InputBase.__init__(self)


    def get_dimension_name(self, dimension):
        """Determine the human-readable name of a dimension.

        Parameters
        ----------
        dimension : Dict
            Information about an SDMX dimension pulled from an SDMX-JSON response

        Returns
        -------
        string
            The human-readable name for the dimension
        """
        map_key = dimension['id']
        # First see if this is in our dimension map.
        if map_key in self.dimension_map:
            return self.dimension_map[map_key]
        # Otherwise default to whatever is in the JSON.
        return dimension['name']


    def get_dimension_value_name(self, dimension, dimension_value):
        """Determine the human-readable name of a dimension value.

        Parameters
        ----------
        dimension : Dict
            Information about an SDMX dimension pulled from an SDMX-JSON response
        dimension_value: Dict
            Information about an SDMX dimenstion value, also from SDMX-JSON

        Returns
        -------
        string
            The human-readable name for the dimension_value
        """
        map_key = dimension['id'] + '|' + dimension_value['id']
        # First see if this is in our dimension map.
        if map_key in self.dimension_map:
            return self.dimension_map[map_key]
        # Aggregate values are always "_T", these can be empty strings.
        if dimension_value['id'] == '_T':
            return None
        # Otherwise default to whatever is in the JSON.
        return dimension_value['name']


    def fix_indicator_name(self, name, indicator_id):
        """Clean/trim the indicator name by trying to remove the id.

        Parameters
        ----------
        name : string
            A raw indicator name
        indicator_id : string
            The id for this indicator.
        """
        name = name.replace(indicator_id, '')
        indicator_id = indicator_id.replace('-', '.')
        name = name.replace(indicator_id, '')
        return name.strip()


    def execute(self):
        """Fetch the data from the SDMX endpoint. Overrides parent."""

        headers = { 'Accept': 'application/json' }
        r = requests.get(self.endpoint, headers=headers)
        data = r.json()

        series_dimensions = data['structure']['dimensions']['series']
        series_attributes = data['structure']['attributes']['series']
        time_periods = data['structure']['dimensions']['observation'][0]['values']

        indicators = {}
        indicator_names = {}

        for series_key in data['dataSets'][0]['series']:
            observations = data['dataSets'][0]['series'][series_key]['observations']
            attributes = data['dataSets'][0]['series'][series_key]['attributes']
            for observation_key in observations:
                observation = observations[observation_key]
                year = time_periods[int(observation_key)]['name']
                value = observation[0]
                indicator_id = None
                disaggregations = {}
                for dimension_index, dimension_value_index in enumerate(series_key.split(':')):
                    dimension_index = int(dimension_index)
                    dimension_value_index = int(dimension_value_index)
                    dimension = series_dimensions[dimension_index]
                    dimension_value = dimension['values'][dimension_value_index]

                    # If this is the "SERIES" dimension, figure out the indicator ID.
                    if dimension['id'] == 'SERIES':
                        indicator_id = self.indicator_map[dimension_value['id']]
                        indicator_id = indicator_id.replace('.', '-')
                        indicator_names[indicator_id] = self.fix_indicator_name(dimension_value['name'], indicator_id)
                    elif dimension['id'] in self.drop_dimensions:
                        # Ignore dimensions specifically set to drop.
                        continue
                    elif self.drop_singleton_dimensions and len(dimension['values']) < 2:
                        # Ignore dimensions with only 1 variation.
                        continue
                    else:
                        # Otherwise we will use this dimension as a disaggregation.
                        dimension_name = self.get_dimension_name(dimension)
                        value_name = self.get_dimension_value_name(dimension, dimension_value)
                        disaggregations[dimension_name] = value_name

                # Did we not find the indicator ID?
                if indicator_id is None:
                    continue

                # Also use attributes as disaggregations.
                for attribute_index, attribute_value_index in enumerate(attributes):
                    if attribute_value_index is None:
                        continue
                    attribute = series_attributes[attribute_index]
                    attribute_value = attribute['values'][attribute_value_index]

                    if attribute['id'] in self.drop_dimensions:
                        # Ignore attributes specifically set to drop.
                        continue
                    elif self.drop_singleton_dimensions and len(attribute['values']) < 2:
                        # Ignore attributes with only 1 variation.
                        continue
                    else:
                        # Otherwise we will use this attribute as a disaggregation.
                        attribute_name = self.get_dimension_name(attribute)
                        value_name = self.get_dimension_value_name(attribute, attribute_value)
                        disaggregations[attribute_name] = value_name

                if indicator_id not in indicators:
                    indicators[indicator_id] = []

                row = self.get_row(year, value, disaggregations)
                indicators[indicator_id].append(row)

        # Convert the lists of dicts into dataframes.
        for indicator_id in indicators:
            data = pd.DataFrame(indicators[indicator_id])
            # Enforce position of "Year" and "Value".
            data = self.fix_dataframe_columns(data)
            # Remove empty columns, because they are not necessary.
            data = data.dropna(axis='columns', how='all')
            # Create the Indicator object.
            name = indicator_names[indicator_id]
            self.indicators[indicator_id] = sdg.Indicator(indicator_id, data=data, name=name)
