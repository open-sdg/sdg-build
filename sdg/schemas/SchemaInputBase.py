# -*- coding: utf-8 -*-

import os
import json
import jsonschema

class SchemaInputBase:
    """
    These Schema classes serve 2 purposes:
    1. Perform the validation of an indicator's metadata.
    2. Output the full schema to JSON file for use by platforms.

    Subclasses are necessary to add the following functionality:
    1. Input from arbitrary schema formats into (internal) JSON Schema.
    2. Output from (internal) JSON Schema to arbitrary shema formats

    GOALS:
    1. This class outputs to simple (backwards-compatible with Open SDG) JSON.
    2. This class outputs to valid JSON Schema.
    3. This class requires subclasses to implement load_schema().
    4. This class expects the internal schema to be valid JSON Schema.
    5. This class can validate against an Indicator object.
    6. This class uses JSON Schema to validate against that object.
    7. THIS CLASS DOES NOT MENTION VALIDATION OF DATA.

    ISSUES:
    1. We need to insert "translation_key" properties into the output. Because
       platforms might need to translate stuff, and often use keys. This
       basically means that we treat "translation_key" as a special property
       that needs to be copied from the input schema, and included in the output.
       Whereas normally there would be no reason to copy "translation_key" into
       the jsonschema, we make sure to do this. And similarly we copy it into
       the backwards-compatible simple json output.
    2.
    """


    def __init__(self, schema_path=''):
        """Create a new SchemaBase object"""

        self.schema_path = schema_path
        self.load_schema()
        self.load_validator()


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
        f = self.schema['properties'].get(field, default)
        if must_exist and f is None:
            raise ValueError(field + " doesn't exist in schema")
        return f


    def get_values(self, field):
        """For backwards compatibility, call renamed method."""
        return self.get_allowed_values(field)


    def get_allowed_options(self, field):
        """Return a list of allowed options for a field from the schema."""

        field = self.get(field)
        field_type = field['type']
        options = []

        # Arrays should have options.
        if field_type == 'array':
            options = field['items']['anyOf']

        # If 'anyOf' is set, there should be options.
        elif 'anyOf' in field:
            options = field['anyOf']

        return options


    def get_allowed_values(self, field):
        """Return a list of allowed values for a field from the schema."""

        options = self.get_allowed_options(field)

        option_values = []
        for option in options:
            option_values.append(option['enum'][0])

        return option_values


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

        options = self.get_allowed_options(field)

        if len(options) == 0:
            raise ValueError(field + " field does not have options element")

        value_translations = {x['enum'][0]: x['translation_key'] for x in options}

        return value_translations
