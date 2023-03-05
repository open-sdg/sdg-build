from sdg.inputs import InputMetaFiles
from ruamel.yaml.parser import ParserError
import yamlmd
import sys

class InputYamlMdMeta(InputMetaFiles):
    """Sources of SDG metadata that are local .md files containing Yaml."""

    def read_meta_at_path(self, filepath):
        meta = {}
        try:
            meta_md = yamlmd.read_yamlmd(filepath)
            meta = dict(meta_md[0])
            meta['page_content'] = ''.join(meta_md[1])
        except ParserError as e:
            print('-----')
            print('The file at ' + filepath + ' could not be parsed because of a syntax error.')
            print('Syntax errors often involve single/double quotes and/or colons (:).')
            print('Sometimes you can find the problem by looking at the lines/columns mentioned in the following raw error message:')
            print('------')
            raise
        return meta
