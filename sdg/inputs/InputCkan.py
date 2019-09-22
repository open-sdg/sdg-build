import sdg
import pandas as pd
from sdg.inputs import InputApi

class InputCkan(InputApi):
    """Sources of SDG data that are in a CKAN service."""


    def generate_api_call(self, resource_id):
        """Given a resource id, generate the URL for the API call."""
        return self.endpoint + '?resource_id=' + resource_id


    def get_indicator_name(self, indicator_id, resource_id):
        # TODO: Figure out how to get actual indicator names here.
        return 'Indicator ' + indicator_id.replace('-', '.')


    def indicator_data_from_json(self, json):
        """Convert a CKAN response into a DataFrame for an indicator."""
        df = pd.DataFrame(json['result']['records'])
        # Drop the "_id" column.
        df = df.drop('_id', axis='columns')
        return df
