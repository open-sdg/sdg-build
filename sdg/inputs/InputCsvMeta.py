import pandas as pd
from sdg.inputs import InputMetaFiles

class InputCsvMeta(InputMetaFiles):
    """Sources of SDG metadata that are local CSV files."""

    def read_meta_at_path(self, filepath):
        meta_df = pd.read_csv(filepath, header=None, index_col=0).squeeze('columns')
        meta_df = meta_df.dropna()
        return meta_df.to_dict()
