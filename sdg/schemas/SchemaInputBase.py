# -*- coding: utf-8 -*-

import os
import json
import jsonschema

class SchemaInputBase:
    """A base class for importing a schema, querying it, and validating with it.

    This class assumes imported schema (self.schema) are valid JSON Schema."""


    def __init__(self, schema_path=''):
        """Create a new SchemaBase object"""

        self.schema_path = schema_path
        self.load_defaults()
        self.load_schema()
        self.load_validator()


    def load_defaults(self):
        """For backwards compatibility, load a minimum default schema."""
        self.schema = {
            'type': 'object',
            'properties': {
                'reporting_status': {
                    'type': 'string',
                    'anyOf': [
                        {
                            'title': 'complete',
                            'value': 'complete',
                            'translation_key': 'status.reported_online'
                        },
                        {
                            'title': 'notstarted',
                            'value': 'notstarted',
                            'translation_key': 'status.exploring_data_sources'
                        }
                    ]
                }
            }
        }

    def load_schema(self):
        """Load the schema. This should be overridden by a subclass."""
        raise NotImplementedError


    def load_validator(self):
        try:
            validator_class = jsonschema.validators.validator_for(self.schema)
            validator_class.check_schema(self.schema)
            self.validator = validator_class(self.schema)
        except Exception as e:
            print(e)


    def validate(self, indicator):
        """Validate the data and/or metadata for an Indicator object."""

        status = True
        if indicator.has_meta():
            try:
                self.validator.validate(indicator.meta)
            except:
                status = False
                print('Validation errors for indicator ' + indicator.inid)
                for error in self.validator.iter_errors(indicator.meta):
                    print(error.message)
                    print(error.schema)

        return status


    def get(self, field, default=None, must_exist=False):
        """Fetch a field from the schema by key."""
        f = self.schema['properties'].get(field, default)
        if must_exist and f is None:
            raise ValueError(field + " doesn't exist in schema")
        return f


    def get_values(self, field):
        """Get the allowed values for a select or multiselect field."""
        options = self.get_allowed_options(field)

        return [x['enum'][0] for x in options]


    def get_allowed_options(self, field):
        """Return a list of allowed options for a field from the schema."""

        field = self.get(field)

        # In JSON Schema the options are in "anyOf", which can be in 2 places.
        if 'anyOf' in field:
            return field['anyOf']
        elif 'items' in field and 'anyOf' in field['items']:
            return field['items']['anyOf']

        return []


    def get_value_translation(self, field):
        """Get a map of values to 'translation_key' for schema field options."""

        options = self.get_allowed_options(field)

        if len(options) == 0:
            raise ValueError(field + " field does not have options element")

        return {x['enum'][0]: x['translation_key'] for x in options}
