import sdg
import pandas as pd
import requests
from sdg.inputs import InputBase
from sdg.Indicator import Indicator

class InputApi(InputBase):
    """Sources of SDG data that are in a remote API.

    Note that this class expects input data of the format described here:
    https://open-sdg.readthedocs.io/en/latest/data-format/

    If the input data is not in the required format, please use the method
    "add_data_alteration" to add a callback function that corrects the format.
    """

    def __init__(self, endpoint, indicator_id_map):
        """Constructor for InputApi input.

        Parameters
        ----------
        endpoint : string
            The remote URL of the endpoint for fetching indicators.
        indicator_id_map : dict
            Map of API ids (such as "resource ids) to indicator ids.
        """
        self.endpoint = endpoint
        self.indicator_id_map = indicator_id_map
        InputBase.__init__(self)


    def indicator_data_from_json(self, json):
        """Convert a an API response into a DataFrame for indicator data.

        Parameters
        ----------
        json : dict
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
        raise NotImplementedError


    def get_indicator_name(self, indicator_id, resource_id):
        """Decide on an indicator name, based on the indicator/resource ids.

        Parameters
        ----------
        indicator_id : string
            The indicator id.
        resource_id : string
            The resource id.
        """
        raise NotImplementedError


    def execute(self, indicator_options):
        """Fetch the resource data from the API for each indicator."""
        headers = { 'Accept': 'application/json' }
        for resource_id in self.indicator_id_map:
            # Fetch the data.
            url = self.generate_api_call(resource_id)
            r = requests.get(url, headers=headers)
            json = r.json()

            # Create the indicator.
            inid = self.indicator_id_map[resource_id]
            data = self.indicator_data_from_json(json)
            name = self.get_indicator_name(inid, resource_id)
            self.add_indicator(inid, data=data, name=name, options=indicator_options)
