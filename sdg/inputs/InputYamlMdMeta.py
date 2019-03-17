from sdg.inputs import InputFiles

class InputYamlMdMeta(InputFiles):
    """Sources of SDG metadata that are local .md files containing Yaml."""

    def __init__(self, path_pattern='', git=False):
        """Constructor for InputYamlMdMeta.

        Keyword arguments:
        path_pattern -- path (glob) pattern describing where the files are
        git -- whether to use git information for dates in the metadata
        """
        self.git = git
        InputFiles.__init__(self, path_pattern)