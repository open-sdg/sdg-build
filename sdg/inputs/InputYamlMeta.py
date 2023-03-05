from sdg.inputs import InputMetaFiles
import yaml
import sys


class InputYamlMeta(InputMetaFiles):
    """Sources of SDG metadata that are local YAML files."""

    def read_meta_at_path(self, filepath):

        meta = {}

        try:
            with open(filepath, 'r', encoding='utf-8') as stream:
                meta = yaml.load(stream, Loader=yaml.FullLoader)
        except yaml.parser.ParserError as e:
            print('------')
            print('The file at ' + filepath + ' could not be parsed because of a syntax error.')
            print('Syntax errors often involve single/double quotes and/or colons (:).')
            print('Sometimes you can find the problem by looking at the lines/columns mentioned in the following raw error message:')
            print('------')
            raise
        return meta
