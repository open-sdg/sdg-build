import pandas as pd
from sdg.inputs import InputBase
import yaml

class InputYamlMetaRemote(InputBase):
    """Sources of SDG metadata that are remote YAML files."""

    def __init__(self,
        indicator_id_map=None,
        logging=None,
        metadata_mapping=None,
        request_params=None,
    ):
        """Constructor for InputCsvDataRemote.

        Keyword arguments:
        indicator_id_map: A dict mapping sources (remote URLs) to
        lists of indicator ids.
        metadata_mapping: A dict mapping human-readable labels to machine keys
          or a path to a CSV file
        """
        InputBase.__init__(self,
            logging=logging,
            request_params=request_params,
        )
        self.indicator_id_map = self.get_indicator_id_map(indicator_id_map)
        self.metadata_mapping = metadata_mapping


    def execute(self, indicator_options):
        for source, indicator_ids in self.indicator_id_map.items():
            file_contents = self.fetch_file(source)
            meta = yaml.safe_load(file_contents)
            if not isinstance(indicator_ids, list):
                indicator_ids = [indicator_ids]
            for inid in indicator_ids:
                self.add_indicator(inid, meta=meta, options=indicator_options)


    def get_indicator_id_map(self, source):
        if isinstance(source, dict):
            return source
        elif isinstance(source, str):
            with open(source) as file:
                return yaml.load(file, Loader=yaml.FullLoader)
        else:
            raise Exception("The indicator_id_map parameter is not configured correctly.")
        return {}
