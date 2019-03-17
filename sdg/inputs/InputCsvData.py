from sdg.inputs import InputFiles

class InputCsvData(InputFiles):
    """Sources of SDG data that are local CSV files."""

    def convert_filename_to_indicator_id(self, filename):
        """Assume the file naming convention: 'indicator_1-1-1'."""
        inid = filename.replace('indicator_', '')
        return inid