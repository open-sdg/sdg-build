import sdg
import pandas as pd
import requests
from sdg.inputs import InputBase
from sdg.Indicator import Indicator

class InputCkan(InputBase):
    """Sources of SDG data that are in a CKAN service.

    Note that this class expects input data of the format described here:
    https://open-sdg.readthedocs.io/en/latest/data-format/
    """

    def __init__(self, resource_map, resource_endpoint):
        """Constructor for InputCkan input.

        Parameters
        ----------
        resource_map : dict
            Map of CKAN resource ids to indicator ids.
        resource_endpoint : string
            The remote URL of the CKAN endpoint for fetching resources.

        """
        self.resource_map = resource_map
        self.resource_endpoint = resource_endpoint
        InputBase.__init__(self)


    def records_to_dataframe(self, records):
        """Convert a list of CKAN records into a DataFrame.

        Parameters
        ----------
        records : list
            List of record dicts as returned from the CKAN API call.

        Returns
        -------
        DataFrame
            DataFrame ready for inputting into sdg-build.
        """
        df = pd.DataFrame(records)
        # Drop the "_id" column.
        df = df.drop('_id', axis='columns')
        # Fix the order of the columns.
        return self.fix_dataframe_columns(df)


    def execute(self):
        """Fetch the resource data from the CKAN API for each indicator."""
        headers = { 'Accept': 'application/json' }
        for resource_id in self.resource_map:
            # Fetch the data.
            endpoint = self.resource_endpoint + '?resource_id=' + resource_id
            r = requests.get(endpoint, headers=headers)
            json = r.json()

            # Create the indicator.
            inid = self.resource_map[resource_id]
            data = self.records_to_dataframe(json['result']['records'])
            name = 'Indicator ' + inid.replace('-', '.')
            self.indicators[inid] = Indicator(inid, data=data, name=name)
