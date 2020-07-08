import os
import pandas as pd
import numpy as np
import sdg
from sdg.inputs import InputFiles
from sdg.Indicator import Indicator

class InputCsvMeta(InputFiles):
    """Sources of SDG metadata that are local CSV files."""

    def __init__(self, path_pattern='', git=True, metadata_mapping=None):
        """Constructor for InputYamlMdMeta.
        Keyword arguments:
        path_pattern -- path (glob) pattern describing where the files are
        git -- whether to use git information for dates in the metadata
        """
        self.git = git
        self.metadata_mapping = metadata_mapping
        InputFiles.__init__(self, path_pattern)

    def execute(self, indicator_options):
        """Get the metadata from the CSV, returning a list of indicators."""
        metadata_mapping=self.metadata_mapping
        indicator_map = self.get_indicator_map()
        if metadata_mapping != None:
            meta_mapping = pd.read_csv(os.path.join(metadata_mapping), header=None, names=["Field name", "Field value"])
        for inid in indicator_map:
            # Need to get the folder of the folder of the indicator file.
            src_dir = os.path.dirname(indicator_map[inid])
            src_dir = os.path.dirname(src_dir)
            path = os.path.join(src_dir, 'meta')
            if inid is not None:
                fr = os.path.join(path, inid + '.csv')
            else:
                fr = path
            # Read in CSV file as dataframe
            meta_csv = pd.read_csv(fr, header=None, names=["Field name", "Field key"])
            # Drop rows with any empty columns
            meta_df=meta_df.dropna()
            meta=dict()
            # If metadata_mapping exists, merge the mapping and metadata dataframe
            if metadata_mapping != None:
                meta_mapping_df=pd.merge(meta_mapping, meta_csv, on="Field name")
                # Loop through dataframe rows, assigning second column item to dictionary key
                # and third column item to dictionary value (first column is human-readable labels)
                for row in meta_mapping_df.iterrows():
                    meta[row[1][1]]=row[1][2]
            # If metadata_mapping doesn't exist, use metadata dataframe as it is
            else:
                # Loop through dataframe rows, assigning first column item to dictionary key
                # and second column item to dictionary value
                for row in meta_csv.iterrows():
                    meta[row[1][0]]=row[1][1]

            name = meta['indicator_name'] if 'indicator_name' in meta else None
            self.add_indicator(inid, name=name, meta=meta, options=indicator_options)
