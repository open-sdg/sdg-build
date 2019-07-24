import pandas as pd
import sdg
import requests
from sdg.inputs import InputSdmx

class InputSdmxJson(InputSdmx):
    """Sources of SDG data that are SDMX-JSON format."""


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
        dimension_list = self.data['structure']['dimensions']['series']
        dimension_values = self.get_dimension_values(value_list, dimension_list)
        # Also gether the attribute values for this series key.
        value_list = self.get_series(series_key)['attributes']
        dimension_list = self.data['structure']['attributes']['series']
        attribute_values = self.get_dimension_values(value_list, dimension_list)
        # Combine and save the results.
        dimension_values.update(attribute_values)
        self.series_dimensions[series_key] = dimension_values
        return dimension_values


    def get_series_id(self, series_key):
        """Get the id for the Series.

        Parameters
        ----------
        series_key : string
            The colon-delimited series key
        """
        dimensions = self.get_series_dimensions(series_key)
        return dimensions['SERIES']['value']['id']


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
            dimension_id = dimension['dimension']['id']
            if dimension_id == 'SERIES' or dimension_id in self.drop_dimensions:
                # Skip "SERIES" and anything set to be dropped.
                continue
            else:
                # Otherwise we will use this dimension as a disaggregation.
                dimension_name = self.get_dimension_name(dimension_id)
                dimension_value_id = dimension['value']['id']
                value_name = self.get_dimension_value_name(dimension_id, dimension_value_id)
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


    def fetch_data(self):
        """Fetch the data from the source."""
        if self.source.startswith('http'):
            # For remote sources, assume it is an API that requires a particular
            # "Accept" header in order to return JSON.
            headers = { 'Accept': 'application/json' }
            r = requests.get(self.source, headers=headers)
            self.data = r.json()
        else:
            # For local sources, just load the JSON file and parse it.
            with open(self.source) as json_file:
                self.data = json.load(json_file)
