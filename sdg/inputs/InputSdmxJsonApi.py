import pandas as pd
import sdg
import requests
from sdg.inputs import InputSdmx

class InputSdmxJsonApi(InputSdmx):
    """Sources of SDG data that are remote SDMX JSON endpoint."""

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


    def get_dimensions(self):
        """Get the full list of "dimensions" from the SDMX-JSON.

        Returns
        -------
        list
            List of dimension dicts
        """
        return self.data['structure']['dimensions']['series']


    def get_attributes(self):
        """Get the full list of "attributes" from SDMX-JSON.

        Returns
        -------
        list
            List of attribute dicts
        """
        return self.data['structure']['attributes']['series']


    def get_years(self):
        """Get the full "time period" structure from the SDMX-JSON.

        Returns
        -------
        dict
            Time period structure from SDMX-JSON
        """
        return self.data['structure']['dimensions']['observation'][0]['values']


    def get_all_series(self):
        """Get the full series structure from the SDMX-JSON.

        Returns
        -------
        dict
            Series structure from SDMX-JSON
        """
        return self.data['dataSets'][0]['series']


    def get_series(self, series_key):
        """Get a particular series, by key.

        Parameters
        ----------
        series_key : string
            The colon-delimited series key

        Returns
        -------
        dict
            A particular series dict
        """
        return self.get_all_series()[series_key]


    def get_observations(self, series_key):
        """Get the list of observations for a particular series.

        Parameters
        ----------
        series_key : string
            The colon-delimited series key

        Returns
        -------
        list
            A list of observations dicts for a series
        """
        return self.get_series(series_key)['observations']


    def get_dimension_values(self, value_list, dimension_list):
        """Return a dict of dimension/values, keyed by the dimension id.

        Parameters
        ----------
        value_list : list
            A list with a corresponding value for each item in dimension_list
        dimension_list : list
            A list of dimension dicts

        Returns
        -------
        dict
            A custom dict structure, keyed by dimension id, containing the
            full dimension dict and its full value dict
        """
        dimensions = {}
        for dimension_index, dimension_value_index in enumerate(value_list):
            if dimension_index is None or dimension_value_index is None:
                continue
            dimension_index = int(dimension_index)
            dimension_value_index = int(dimension_value_index)
            dimension = dimension_list[dimension_index]
            dimension_value = dimension['values'][dimension_value_index]
            dimensions[dimension['id']] = {
                'dimension': dimension,
                'value': dimension_value
            }
        return dimensions


    def get_series_dimensions(self, series_key):
        """Parse the dimensions/attributes/values for a particular series.

        Parameters
        ----------
        series_key : string
            The colon-delimited series key

        Returns
        -------
        dict
            A custom dict structure, keyed by dimension id, containing the
            full dimension/attribute dict and its full value dict.
        """
        # Use a previously-calculated version if available.
        if series_key in self.series_dimensions:
            return self.series_dimensions[series_key]
        # Gather the dimension values for this series key.
        value_list = series_key.split(':')
        dimension_list = self.get_dimensions()
        dimension_values = self.get_dimension_values(value_list, dimension_list)
        # Also gether the attribute values for this series key.
        value_list = self.get_series(series_key)['attributes']
        dimension_list = self.get_attributes()
        attribute_values = self.get_dimension_values(value_list, dimension_list)
        # Combine and save the results.
        dimension_values.update(attribute_values)
        self.series_dimensions[series_key] = dimension_values
        return dimension_values


    def get_series_name(self, series_key):
        """Get the name for a series.

        Parameters
        ----------
        series_key : string
            The colon-delimited series key

        Returns
        -------
        string
            Name for this series
        """
        dimensions = self.get_series_dimensions(series_key)
        series_name = dimensions['SERIES']['value']['name']
        series_id = dimensions['SERIES']['value']['id']
        indicator_ids = self.indicator_id_map[series_id]
        for indicator_id in indicator_ids:
            series_name = self.normalize_indicator_name(series_name, indicator_id)
        return series_name


    def get_series_id(self, series_key):
        """Get the id for a series ("indicator id").

        Parameters
        ----------
        series_key : string
            The colon-delimited series key

        Returns
        -------
        string
            Indicator id for this series
        """
        dimensions = self.get_series_dimensions(series_key)
        series_id = dimensions['SERIES']['value']['id']
        indicator_id_map = self.get_indicator_id_map()
        if series_id not in indicator_id_map:
            return None
        indicator_ids = indicator_id_map[series_id]

        return indicator_ids


    def get_series_disaggregations(self, series_key):
        """Get the disaggregation categories/values for a series.

        Parameters
        ----------
        series_key : string
            The colon-delimited series key

        Returns
        -------
        dict
            Disaggregation values, keyed by category, for this series
        """
        disaggregations = {}
        dimensions = self.get_series_dimensions(series_key)
        for key in dimensions:
            dimension = dimensions[key]
            series_id = dimension['dimension']['id']
            if series_id == 'SERIES' or series_id in self.drop_dimensions:
                # Skip "SERIES" and anything set to be dropped.
                continue
            elif self.drop_singleton_dimensions and len(dimension['dimension']['values']) < 2:
                # Ignore dimensions with only 1 variation.
                continue
            else:
                # Otherwise we will use this dimension as a disaggregation.
                dimension_name = self.get_dimension_name(dimension['dimension'])
                value_name = self.get_dimension_value_name(dimension['dimension'], dimension['value'])
                disaggregations[dimension_name] = value_name
        return disaggregations


    def get_series_data(self, series_key):
        """Convert a set of observations into a list of rows.

        Parameters
        ----------
        series_key : string
            The colon-delimited series key

        Returns
        -------
        List
            The rows of data for this series.
        """
        disaggregations = self.get_series_disaggregations(series_key)
        observations = self.get_observations(series_key)
        rows = []
        for observation_key in observations:
            year = self.get_years()[int(observation_key)]['name']
            value = observations[observation_key][0]
            row = self.get_row(year, value, disaggregations)
            rows.append(row)
        return rows


    def create_dataframe(self, rows):
        """Convert a list of rows into a dataframe.

        Parameters
        ----------
        rows : List
            A list of row dicts

        Returns
        -------
        Dataframe
            The dataframe of rows of data for this indicator.
        """
        df = pd.DataFrame(rows)
        # Enforce position of "Year" and "Value".
        df = self.fix_dataframe_columns(df)
        # Remove empty columns, because they are not necessary.
        df = df.dropna(axis='columns', how='all')
        return df


    def fetch_data(self):
        """Fetch the data from the endpoint."""
        headers = { 'Accept': 'application/json' }
        r = requests.get(self.source, headers=headers)
        self.data = r.json()


    def execute(self):
        """Fetch the data from the SDMX endpoint. Overrides parent."""

        # Fetch the response from the SDMX endpoint.
        self.fetch_data()

        # SDMX-JSON divides the data into series, but we want to divide
        # the data into indicators. Indicators contain multiple series,
        # so we need to loop through the series and build up indicators.
        indicator_data = {}
        indicator_names = {}

        # Loop through each "series" in the SDMX-JSON.
        for series_key in self.get_all_series():

            # Get the indicator ids (some series apply to multiple indicators).
            indicator_ids = self.get_series_id(series_key)

            # Skip any series if we cannot figure out the indicator id.
            if indicator_ids is None:
                continue

            for indicator_id in indicator_ids:
                # Get the indicator name if needed.
                if indicator_id not in indicator_names:
                    indicator_names[indicator_id] = self.get_series_name(series_key)
                    # Also start off an empty list of rows.
                    indicator_data[indicator_id] = []

                # Get the rows of data for this series.
                indicator_data[indicator_id].extend(self.get_series_data(series_key))

        # Create the Indicator objects.
        for indicator_id in indicator_data:
            data = self.create_dataframe(indicator_data[indicator_id])
            name = indicator_names[indicator_id] if self.import_names else None
            indicator = sdg.Indicator(indicator_id, data=data, name=name)
            self.indicators[indicator_id] = indicator
