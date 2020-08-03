import os
import sdg
from sdg.inputs import InputFiles
from sdg.Indicator import Indicator

class InputYamlMdMeta(InputFiles):
    """Sources of SDG metadata that are local .md files containing Yaml."""

    def __init__(self, path_pattern='', git=True, git_data_dir=None):
        """Constructor for InputYamlMdMeta.

        Keyword arguments:
        path_pattern -- path (glob) pattern describing where the files are
        git -- whether to use git information for dates in the metadata
        git_data_dir -- location of folder containing git data for dates
        """
        self.git = git
        self.git_data_dir = git_data_dir
        InputFiles.__init__(self, path_pattern)

    def execute(self, indicator_options):
        """Get the metadata from the YAML/Markdown, returning a list of indicators."""
        indicator_map = self.get_indicator_map()
        print("!!! indicator_map !!!/n")
        print(indicator_map)
        for inid in indicator_map:
            # Need to get the folder of the folder of the indicator file.
            src_dir = os.path.dirname(indicator_map[inid])
            src_dir = os.path.dirname(src_dir)
            meta = sdg.meta.read_meta(inid, git=self.git, src_dir=src_dir,
                git_data_dir=self.git_data_dir)
            name = meta['indicator_name'] if 'indicator_name' in meta else None
            self.add_indicator(inid, name=name, meta=meta, options=indicator_options)
