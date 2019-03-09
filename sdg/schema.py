# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 14:24:13 2019

@author: dashton
"""

import yaml
import json
import os
from sdg.json import write_json


def load_prose_schema(prose_file='_prose.yml', src_dir=''):
    """Read the prose config and output as a JSON object

    Args:
        src_dir: str. Project root location
        prose_file: str. The file name where the prose config lives.

    Returns:
        The information about metadata fields as required by the web code.
        This is quite likely to evolve as the use of prose changes.
    """

    prose_path = os.path.join(src_dir, prose_file)

    with open(prose_path, encoding="UTF-8") as stream:
        config = next(yaml.safe_load_all(stream))

    schema = dict()
    for field in config['prose']['metadata']['meta']:
        schema[field['name']] = field['field']

    return schema

# %% Schema Class


class Schema:
    """
    The Schema class loads in everything we know about the metadata. We can
    check for information about the fields, as well as writing out to the
    data service
    """

    schema = dict()
    schema_defaults = dict()

    def __init__(self, schema_file='_prose.yml',
                 schema_type='prose', src_dir=''):
        """Create a new Schema object

        Args:
            schema_file: location relative to src_dir of the schema file
            schema_type: what type of schema. Currently excepts only 'prose'
                         but if different formats appear they will be added
        """
        if schema_type == 'prose':
            self.schema = load_prose_schema(schema_file, src_dir)
        else:
            raise ValueError("Unknown schema type: " + schema_type)
        
        self.load_defaults()
            
    def load_defaults(self):
        """Get default schema values from built in JSON"""
        file_dir = os.path.dirname(os.path.realpath(__file__))
        json_path = os.path.join(file_dir, 'schema_defaults.json')
 
        with open(json_path, "r") as json_file:
            self.schema_defaults = json.load(json_file)       
        

    def get(self, field, default=None, must_exist=False):
        """Slightly safer get method for schema items"""
        f = self.schema.get(field, default)
        if must_exist and f is None:
            raise ValueError(field + " doesn't exist in schema")
        return f

    def get_values(self, field):
        """
        Get the allowed values for a select element

        Args:
            field: The name of the metadata field you want

        Returns:
            A list of values for that field.
        """
        f = self.get(field, must_exist=True)
        if 'options' not in f:
            raise ValueError(field + " does not have options element")

        values = [x.get('value') for x in f['options']]

        return values

    def get_value_translation(self, field):
        """
        For select elements we can retrieve the allowed values and their
        translation_key. Use this if you want to replace values with
        translations via a lookup

        Args:
            field: The name of the metadata field you want

        Returns:
            A value: translation_key dictionary
        """
        f = self.get(field, must_exist=True)
        if 'options' not in f:
            raise ValueError(field + " field does not have options element")

        value_translations = {x['value']: x['translation_key'] for x in f['options']}

        return value_translations

    def write_schema(self,
                     prefix='schema',
                     ftype='meta',
                     gz=False,
                     site_dir=''):
        """
        Transform back to the prose style format and write out to json. Most
        arguments are passed straight to sdg.json.write_json

        Args:
            prefix: filename (without extension) for the output file
            ftype: Which output directory to go in (schema usually in meta)
            gz: Compress the json? False by default
            site_dir: root location for output

        Returns:
            boolean status from write_json
        """
        prose_schema = list()
        for key, value in self.schema.items():
            prose_schema.append({
                    'name': key,
                    'field': value
                    })

        status = write_json(inid=prefix,
                            obj=prose_schema,
                            ftype=ftype,
                            gz=gz,
                            site_dir=site_dir)
        return status

