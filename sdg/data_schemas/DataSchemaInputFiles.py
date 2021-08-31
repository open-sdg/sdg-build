# -*- coding: utf-8 -*-

import os
import glob
from sdg.data_schemas import DataSchemaInputBase

class DataSchemaInputFiles(DataSchemaInputBase):
    """A class for importing data schema from a folder of files."""


    def load_all_schema(self):
        """Load the indicator schema."""
        indicator_schema = {}
        for path in self.get_file_paths():
            inid = self.convert_path_to_indicator_id(path)
            indicator_schema[inid] = self.load_schema(path)
        return indicator_schema


    def load_schema(self, path):
        """Load a local schema. This should be overridden by a subclass."""
        raise NotImplementedError


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
        """Return a list of all the paths for the local data schema files."""
        paths = glob.glob(os.path.join(self.source))
        return paths
