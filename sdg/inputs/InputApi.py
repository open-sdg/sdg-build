import sdg
import pandas as pd
import requests
import json
from sdg.inputs import InputBase
from sdg.Indicator import Indicator
import time

class InputApi(InputBase):
    """Sources of SDG data that are in a remote API.

    Note that this class expects input data of the format described here:
    https://open-sdg.readthedocs.io/en/latest/data-format/

    If the input data is not in the required format, please use the method
    "add_data_alteration" to add a callback function that corrects the format.
    """

    def __init__(self, endpoint, indicator_id_map=None, logging=None, post_data=None,
                 year_column=None, value_column=None, sleep=None):
        """Constructor for InputApi input.

        Parameters
        ----------
        endpoint : string
            The remote URL of the endpoint for fetching indicators. If this
            contains "[resource_id]", it will be replaced with the resource
            ID for each API call. Otherwise, the resource ID will be added
            to the end of each API call.
        indicator_id_map : dict
            Map of API ids (such as "resource ids) to indicator ids.
        post_data : dict
            If passed, the request will be a POST instead of GET with the
            dict as the request payload.
        year_column : string
            A column to change to "Year".
        value_column : string
            A column to change to "Value".
        sleep : int
            Number of seconds to wait in between each request.
        """
        self.endpoint = endpoint
        self.indicator_id_map = indicator_id_map
        self.post_data = post_data
        self.year_column = year_column
        self.value_column = value_column
        self.sleep = sleep
        InputBase.__init__(self, logging=logging)


    def indicator_data_from_json(self, json_response):
        """Convert a an API response into a DataFrame for indicator data.

        Parameters
        ----------
        json_response : dict
            JSON data as returned from the API call.

        Returns
        -------
        DataFrame
            DataFrame ready for inputting into sdg-build.
        """
        raise NotImplementedError


    def generate_api_call(self, resource_id):
        """Given a resource id, generate the URL for the API call.

        Parameters
        ----------
        resource_id : string
            The resource id for the indicator in the API.
        """
        if '[resource_id]' in self.endpoint:
            return self.endpoint.replace("[resource_id]", resource_id)
        else:
            return self.endpoint + resource_id


    def get_indicator_name(self, indicator_id, resource_id, json_response):
        """Decide on an indicator name, based on the indicator/resource ids.

        Parameters
        ----------
        indicator_id : string
            The indicator id.
        resource_id : string
            The resource id.
        json_response : dict
            The data that was returned from the endpoint.
        """
        raise NotImplementedError


    def get_indicator_id(self, resource_id, json_response):
        if isinstance(self.indicator_id_map, dict):
            return self.indicator_id_map[resource_id]
        else:
            return resource_id


    def fetch_json_response(self, url):
        headers = { 'Accept': 'application/json' }
        post_data = self.get_post_data()
        if post_data is not None:
            r = requests.post(url, headers=headers, data=json.dumps(post_data))
        else:
            r = requests.get(url, headers=headers)
        try:
            return r.json()
        except:
            return None


    def get_post_data(self):
        return self.post_data


    def fix_data(self, df):
        if self.year_column is not None:
            df = df.rename(columns={self.year_column: 'Year'})
        if self.value_column is not None:
            df = df.rename(columns={self.value_column: 'Value'})
        return self.fix_dataframe_columns(df)


    def execute(self, indicator_options):
        InputBase.execute(self, indicator_options)
        self.add_data_alteration(self.fix_data)
        for resource_id in self.get_indicator_id_map():
            # Fetch the data.
            url = self.generate_api_call(resource_id)
            json_response = self.fetch_json_response(url)

            # Create the indicator.
            inid = self.get_indicator_id(resource_id, json_response)
            data = self.indicator_data_from_json(json_response)
            if data is None:
                continue
            name = self.get_indicator_name(inid, resource_id, json_response)
            self.add_indicator(inid, data=data, name=name, options=indicator_options)

            self.wait_for_next_request()


    def get_indicator_id_map(self):
        return self.indicator_id_map if self.indicator_id_map is not None else {}


    def wait_for_next_request(self):
        if self.sleep is not None:
            time.sleep(self.sleep)
