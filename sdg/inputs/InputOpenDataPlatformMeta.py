import json
import os
import pandas as pd
from sdg.inputs import InputBase

class InputOpenDataPlatformMeta(InputBase):


    def __init__(self, source=None, logging=None, indicator_key='SDG_INDICATOR',
                 metadata_mapping=None):
        InputBase.__init__(self, logging=logging)
        self.indicator_key = indicator_key
        self.metadata_mapping = metadata_mapping
        self.source = source


    def load_metadata_mapping(self):
        mapping = None
        if self.metadata_mapping is None:
            mapping = {}
        elif isinstance(self.metadata_mapping, dict):
            mapping = self.metadata_mapping
        # Otherwise assume it is a path to a file.
        else:
            extension = os.path.splitext(self.metadata_mapping)[1]
            if extension.lower() == '.csv':
                mapping = pd.read_csv(self.metadata_mapping, header=None, index_col=0, squeeze=True).to_dict()

        if mapping is None:
            raise Exception('Format of metadata_mapping should be a dict or a path to a CSV file.')

        self.metadata_mapping = mapping


    def apply_metadata_mapping(self, metadata):
        for human_key in self.metadata_mapping:
            machine_key = self.metadata_mapping[human_key]
            if human_key in metadata and human_key != machine_key:
                metadata[machine_key] = metadata[human_key]
                del metadata[human_key]


    def execute(self, indicator_options):
        self.load_metadata_mapping()
        payload = self.fetch_file(self.source)
        parsed = json.loads(payload)
        for item in parsed['data']:
            meta = item.copy()
            self.apply_metadata_mapping(meta)
            indicator_id = self.normalize_indicator_id(self.get_indicator_id(item))
            indicator_name = self.normalize_indicator_name(self.get_indicator_name(item), indicator_id)
            self.add_indicator(indicator_id, name=indicator_name, meta=meta, options=indicator_options)


    def get_indicator_id(self, row):
        if self.indicator_key not in row:
            print(row)
            raise Exception('The indicator_key was not found in the metadata shown above.')
        return row[self.indicator_key]


    def get_indicator_name(self, row):
        return self.get_indicator_id(row)
