from sdg.inputs import InputMetaFiles
from sdg.helpers.files import get_yaml_syntax_help
import yaml

class InputYamlMeta(InputMetaFiles):
    """Sources of SDG metadata that are local YAML files."""

    def read_meta_at_path(self, filepath):

        meta = {}

        try:
            with open(filepath, 'r', encoding='utf-8') as stream:
                meta = yaml.load(stream, Loader=yaml.FullLoader)
        except yaml.parser.ParserError as e:
            raise Exception(get_yaml_syntax_help(filepath)) from e
        return meta
