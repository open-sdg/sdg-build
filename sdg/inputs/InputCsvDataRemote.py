import pandas as pd
from sdg.inputs import InputBase
import yaml

class InputCsvDataRemote(InputBase):
    """Sources of SDG data that are remote CSV files."""

    def __init__(self,
        indicator_id_map=None,
        logging=None,
        column_map=None,
        code_map=None,
        dtype=None,
        request_params=None,
    ):
        """Constructor for InputCsvDataRemote.

        Keyword arguments:
        indicator_id_map: A dict mapping sources (remote URLs) to
        lists of indicator ids.
        """
        InputBase.__init__(self,
            logging=logging,
            column_map=column_map,
            code_map=code_map,
            request_params=request_params,
        )
        self.indicator_id_map = self.get_indicator_id_map(indicator_id_map)
        self.dtype = {} if dtype is None else dtype


    def execute(self, indicator_options):
        for source, indicator_ids in self.indicator_id_map.items():
            data = pd.read_csv(source, dtype=self.dtype)
            if not isinstance(indicator_ids, list):
                indicator_ids = [indicator_ids]
            for inid in indicator_ids:
                self.add_indicator(self.normalize_indicator_id(inid), data=data, options=indicator_options)


    def get_indicator_id_map(self, source):
        if isinstance(source, dict):
            return source
        elif isinstance(source, str):
            with open(source) as file:
                return yaml.load(file, Loader=yaml.FullLoader)
        else:
            raise Exception("The indicator_id_map parameter is not configured correctly.")
        return {}
