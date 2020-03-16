import os
import pandas as pd
import numpy as np
import sdg
from sdg.inputs import InputFiles
from sdg.Indicator import Indicator

class InputExcelMeta(InputFiles):
    """Sources of SDG metadata that are local CSV files."""

    def __init__(self, path_pattern='', git=True, metadata_mapping=None, sheet_number=0):
        """Constructor for InputYamlMdMeta.
        Keyword arguments:
        path_pattern -- path (glob) pattern describing where the files are
        git -- whether to use git information for dates in the metadata
        """
        self.git = git
        InputFiles.__init__(self, path_pattern)

    def execute(self):
        """Get the metadata from the CSV, returning a list of indicators."""
        metadata_mapping=self.metadata_mappung
        indicator_map=self.get_indicator_map()
        print(indicator_map)
        if metadata_mapping != None:
            meta_mapping = pd.read_csv(os.path.join(metadata-mapping), header=None, names=["Field name", "Field value"])
        for inid in indicator_map:
            # Need to get the folder of the folder of the indicator file.
            src_dir = os.path.dirname(indicator_map[inid])
            src_dir = os.path.dirname(src_dir)
            path = os.path.join(src_dir, 'meta')
            if inid is not None:
                fr = os.path.join(path, inid + '.xlsx')
            else:
                fr = path
            meta_excel=pd.ExcelFile(fr)
            meta_df=meta_excel.parse(meta_excel.sheet_names[sheet_number])
            for index, row in meta_df.iterrows():
                if type(row[0])==float:
                    if np.isnan(row[0]):
                        meta_df.iat[index-1,1]=row[1]
                        meta_df.iat[index, 1]=np.nan
            meta_df=meta_df.dropna()
            meta_df.columns=["Field name", "Field key"]
            if metadata_mapping != None:         
                meta_mapping_df=pd.merge(meta_mapping, meta_df, on="Field name")
                meta=dict()
                for row in meta_mapping_df.iterrows():
                    if type(row[1][2])==float:
                        if np.isnan(row[1][2])==False:
                            meta[row[1][1]]=row[1][2]
                    else:
                        meta[row[1][1]]=row[1][2]
            else:
                meta=dict()
                for row in meta_df.iterrows():
                    if type(row[1][1])==float:
                        if np.isnan(row[1][1])==False:
                            meta[row[1][0]]=row[1][1]
                    else:
                        meta[row[1][0]]=row[1][1]
            
            name = meta['indicator_name'] if 'indicator_name' in meta else None
            inid = inid.split()[1].replace(".","-")
            self.add_indicator(inid, name=name, meta=meta)
