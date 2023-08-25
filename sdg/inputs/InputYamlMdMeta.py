from sdg.inputs import InputMetaFiles
from sdg.helpers.files import get_yaml_syntax_help
from ruamel.yaml.parser import ParserError
import yamlmd

class InputYamlMdMeta(InputMetaFiles):
    """Sources of SDG metadata that are local .md files containing Yaml."""

    def read_meta_at_path(self, filepath):
        meta = {}
        try:
            meta_md = yamlmd.read_yamlmd(filepath)
            meta = dict(meta_md[0])
            meta['page_content'] = ''.join(meta_md[1])
        except ParserError as e:
            raise Exception(get_yaml_syntax_help(filepath)) from e
        return meta
