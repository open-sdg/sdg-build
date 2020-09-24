import pandas as pd
from sdg.inputs import InputMetaFiles

class InputExcelMeta(InputMetaFiles):
    """Sources of SDG metadata that are local CSV files."""

    def __init__(self, path_pattern='', git=True, git_data_dir='data',
                 git_data_filemask='indicator_*.csv', metadata_mapping=None,
                 sheet_number=0):
        """Constructor for InputExcelMeta.

        Keyword arguments:
        sheet_number -- The sheet number of the Excel file to use
        """
        self.sheet_number = sheet_number
        InputMetaFiles.__init__(self, path_pattern=path_pattern, git=git,
                            git_data_dir=git_data_dir,
                            git_data_filemask=git_data_filemask,
                            metadata_mapping=metadata_mapping)


    def read_meta_at_path(self, filepath):
        meta_excel = pd.ExcelFile(filepath)
        meta_df = meta_excel.parse(meta_excel.sheet_names[self.sheet_number], header=None, index_col=0, squeeze=True)
        meta_df = meta_df.dropna()
        return meta_df.to_dict()
