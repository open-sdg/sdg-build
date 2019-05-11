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


    def get_special_properties(self):
        """A list of special properties which should always be imported/exported."""
        return ['translation_key']


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
