import glob
import os
from sdg.inputs import InputBase

class InputFiles(InputBase):
    """Sources of SDG data/metadata that are local files on disk."""

    def __init__(self, path_pattern=''):
        """Constructor for InputYamlMdMeta.

        Keyword arguments:
        path_pattern -- path (glob) pattern describing where the files are
        """
        self.path_pattern = path_pattern
        InputBase.__init__(self)

    def convert_filename_to_indicator_id(self, filename):
        """Allow subclasses to tweak the way filenames are interpreted."""
        return filename

    def convert_path_to_indicator_id(self, path):
        """Return the indicator ID from the path. Assumes it is the filename."""
        filename = os.path.basename(path)
        without_extension = os.path.splitext(filename)[0]
        inid = self.convert_filename_to_indicator_id(without_extension)
        return inid

    def get_file_paths(self):
        """Return a list of all the paths for the local data/metadata files."""
        paths = glob.glob(os.path.join(self.path_pattern))
        return paths

    def get_indicator_map(self):
        """Return a dict of indicator ids to file paths."""
        indicator_map = {}
        for path in self.get_file_paths():
            inid = self.convert_path_to_indicator_id(path)
            indicator_map[inid] = path
        return indicator_map
