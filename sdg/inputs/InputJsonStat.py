from pyjstat import pyjstat
from sdg.inputs import InputApi
import collections

class InputJsonStat(InputApi):
    """Sources of SDG data that are in a JSON-Stat format in a remote API.
    """

    def indicator_data_from_json(self, json_response):
        """Convert a an JSON-Stat response into a DataFrame for indicator data."""
        ordered_json = collections.OrderedDict(json_response)
        dataset = pyjstat.Dataset.read(ordered_json)
        df = dataset.write('dataframe')
        return df


    def get_indicator_name(self, indicator_id, resource_id, json_response):
        try:
            return json_response['dataset']['label']
        except:
            return indicator_id
