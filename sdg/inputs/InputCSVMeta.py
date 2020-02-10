import os
import pandas as pd
import numpy as np
import sdg
from sdg.inputs import InputFiles
from sdg.Indicator import Indicator

class InputCSVMeta(InputFiles):
    """Sources of SDG metadata that are local CSV files."""

    def __init__(self, path_pattern='', git=True):
        """Constructor for InputYamlMdMeta.
        Keyword arguments:
        path_pattern -- path (glob) pattern describing where the files are
        git -- whether to use git information for dates in the metadata
        """
        self.git = git
        InputFiles.__init__(self, path_pattern)

    def execute(self):
        """Get the metadata from the CSV, returning a list of indicators."""
        indicator_map = self.get_indicator_map()
        for inid in indicator_map:
            # Need to get the folder of the folder of the indicator file.
            src_dir = os.path.dirname(indicator_map[inid])
            src_dir = os.path.dirname(src_dir)                
            meta = read_csv_meta(inid, git=self.git, src_dir=src_dir)
            name = meta['indicator_name'] if 'indicator_name' in meta else None
            self.add_indicator(inid, name=name, meta=meta)
           
    def read_csv_meta(inid, git=True, src_dir='', git_data_dir=None):
        fr = input_path(inid, ftype='meta', src_dir=src_dir)

        metadata_mapping = pd.read_csv(os.path.join('metadata-mapping.csv'), header=None, names=["Field name", "Field value"])
        meta_csv = pd.read_csv(fr, header=None, names=["Field name", "Field key"])

        meta_df=pd.merge(meta_mapping, meta_csv, on="Field name")

        meta=dict()
        for row in meta_df.iterrows():
            if type(row[1][2])==float:
                if np.isnan(row[1][2])==False:
                    meta[row[1][1]]=row[1][2]
            else:
                meta[row[1][1]]=row[1][2]

        for i in range(1,7):
            if "source_organisation_"+str(i) in meta:
                meta["source_active_"+str(i)]="true"
            else:
                meta["source_active_"+str(i)]="false"

        return meta
