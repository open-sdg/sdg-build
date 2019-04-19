import pandas as pd
import sdg
import requests
from sdg.Indicator import Indicator
from sdg.inputs import InputBase

class InputSdmxJsonApi(InputBase):
    """Sources of SDG data that are remote SDMX JSON endpoint."""

    def __init__(self, endpoint=''):
        """Constructor for InputSdmxJsonApi.

        Keyword arguments:
        endpoint -- remote URL of the SDMX API endpoint
        """
        self.endpoint = endpoint
        InputBase.__init__(self)

    def series_name_to_id(self, name):
        """Decipher from the series name what the indicator ID is."""

        # For now assume the indicator id is what is in parenthesis.
        try:
            id = name[name.find("(")+1:name.find(")")]
        except:
            id = None
        return id

    def execute(self):
        """Get the data, edges, and headline from SDMX, returning a list of indicators."""

        headers = { 'Accept': 'application/json' }
        r = requests.get(self.endpoint, headers=headers)
        data = r.json()

        series_dimensions = data['structure']['dimensions']['series']
        time_periods = data['structure']['dimensions']['observation'][0]['values']

        indicators = {}

        for series_key in data['dataSets'][0]['series']:
            observations = data['dataSets'][0]['series'][series_key]['observations']
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
                        indicator_id = self.series_name_to_id(dimension_value['name'])
                    elif len(dimension['values']) > 1:
                        # We only care about dimensions with more than 1 possible value.
                        disaggregations[dimension['name']] = dimension_value['name']

                # Did we not find the indicator ID?
                if indicator_id is None:
                    continue

                if indicator_id not in indicators:
                    indicators[indicator_id] = []

                # Construct the row for this series.
                row = {}
                row['Year'] = year
                for disaggregation in disaggregations:
                    row[disaggregation] = disaggregations[disaggregation]
                row['Value'] = value

                indicators[indicator_id].append(row)

        # Convert the lists of dicts into dataframes.
        for indicator_id in indicators:
            data = pd.DataFrame(indicators[indicator_id])
            # Enforce position of "Year" and "Value".
            cols = data.columns.tolist()
            cols.pop(cols.index('Year'))
            cols.pop(cols.index('Value'))
            cols = ['Year'] + cols + ['Value']
            data = data[cols]
            # Create the Indicator object.
            self.indicators[indicator_id] = Indicator(indicator_id, data=data)
