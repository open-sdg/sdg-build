from sdg.inputs import InputMetaFiles
import yaml


class InputYamlMeta(InputMetaFiles):
    """Sources of SDG metadata that are local YAML files."""

    def read_meta_at_path(self, filepath):

        meta = {}

        with open(filepath, 'r', encoding='utf-8') as stream:
            meta = yaml.load(stream, Loader=yaml.FullLoader)

        return meta
