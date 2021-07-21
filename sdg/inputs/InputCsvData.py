import pandas as pd
import sdg
from sdg.inputs import InputFiles
from sdg.Indicator import Indicator

class InputCsvData(InputFiles):
    """Sources of SDG data that are local CSV files."""

    def __init__(self, path_pattern='', logging=None,
                 column_map=None, code_map=None,
                 dtype=None):
        """Constructor for InputCsvData.

        Keyword arguments:
        dtype: dict showing the datatypes of certain columns.
        """
        InputFiles.__init__(self, path_pattern=path_pattern,
                            logging=logging, column_map=column_map,
                            code_map=code_map)
        self.dtype = {} if dtype is None else dtype

    def convert_filename_to_indicator_id(self, filename):
        """Assume the file naming convention: 'indicator_1-1-1'."""
        inid = filename.replace('indicator_', '')
        return inid

    def execute(self, indicator_options):
        InputFiles.execute(self, indicator_options)
        """Get the data, edges, and headline from CSV, returning a list of indicators."""
        indicator_map = self.get_indicator_map()
        for inid in indicator_map:
            data = pd.read_csv(indicator_map[inid], dtype=self.dtype)
            self.add_indicator(inid, data=data, options=indicator_options)
