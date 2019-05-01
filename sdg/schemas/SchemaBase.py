# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 14:24:13 2019

@author: dashton
"""

import json
import os
from sdg.json import write_json

# %% SchemaBase Class


class SchemaBase:
    """
    The SchemaBase includes base functionality for loading in info about the
    metadata fields. We can check for information about the fields, as well as
    writing out to the data service
    """


    def __init__(self):
        """Create a new Schema object"""

        self.load_schema()
        self.load_defaults({
            "reporting_status": {
                "options": [
                    {
                        "name": "complete",
                        "value": "complete",
                        "translation_key": "status.reported_online"
                    },
                    {
                        "name": "inprogress",
                        "value": "inprogress",
                        "translation_key": "status.statistics_in_progress"
                    },
                    {
                        "name": "notstarted",
                        "value": "notstarted",
                        "translation_key": "status.exploring_data_sources"
                    },
                    {
                        "name": "notapplicable",
                        "value": "notapplicable",
                        "translation_key": "status.not_applicable"
                    }
                ]
            }
        })
        self.merge_default_translations()


    def load_schema(self):
        """Load the schema. This should be overridden by a subclass."""
        raise NotImplementedError


    def load_defaults(self, defaults):
        """Add some default schema values"""
        if not hasattr(self, 'schema_defaults'):
            self.schema_defaults = {}
        self.schema_defaults.update(defaults)


    def get_defaults(self):
        return self.schema_defaults


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


    def merge_default_translations(self):
        """
        Merge the default translations with the schema

        These defaults are intended for backwards compatibility, and not to
        merge every field. They merge what we need to keep things moving
        but aim to respect configuration choices.
        """

        default_options = (self.schema_defaults
                           .get('reporting_status')
                           .get('options'))
        new_options = self.get('reporting_status').get('options')

        #  Join by value, not name, as it's more constant
        #  (name is used for display)
        for i, opt in enumerate(new_options):
            if opt.get('translation_key') is None:
                def_opt = [x for x in default_options
                           if x['value']==opt['value']]
                if len(def_opt) == 1:
                    def_opt = def_opt[0]
                else:
                    continue
                opt['translation_key'] = def_opt['translation_key']
                new_options[i] = opt

        self.schema['reporting_status']['options'] = new_options



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
        schema = list()
        for key, value in self.schema.items():
            schema.append({
                'name': key,
                'field': value
            })

        status = write_json(inid=prefix,
                            obj=schema,
                            ftype=ftype,
                            gz=gz,
                            site_dir=site_dir)
        return status
