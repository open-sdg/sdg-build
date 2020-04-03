import os
import yaml

from sdg.schemas import SchemaInputBase

class SchemaInputOpenSdg(SchemaInputBase):
    """Input schema from Open SDG format and validate metadata."""


    def load_schema(self):
        """Import a _prose.yml schema into JSON Schema. Overrides parent."""

        with open(self.schema_path, encoding="UTF-8") as stream:
            config = next(yaml.safe_load_all(stream))

        schema = {
            "type": "object",
            "properties": {}
        }

        # For Open SDG, certain fields are required. We have to hardcode these
        # here, because _prose.yml has no mechanism for requiring fields.
        # TODO: Should we just add "required" properties in _prose.yml, purely
        # for this purpose?
        schema['required'] = ['reporting_status']

        # Convert the Prose.io metadata into JSON Schema.
        for field in config['prose']['metadata']['meta']:
            is_required = field['name'] in schema['required']
            jsonschema_field = self.prose_field_to_jsonschema(field['field'], is_required)
            schema['properties'][field['name']] = jsonschema_field
            self.add_item_to_field_order(field['name'])

        # And similarly, there are certain conditional validation checks.
        schema['allOf'] = [
            # If reporting_status is 'complete', require data_non_statistical.
            {
                'if': {
                    'properties': { 'reporting_status': { 'enum': ['complete'] } }
                },
                'then': {
                    'required': ['data_non_statistical']
                }
            },
            # If graphs will display, require graph_title and graph_type.
            {
                'if': {
                    'properties': {
                        'reporting_status': { 'enum': ['complete'] },
                        'data_non_statistical': { 'const': False }
                    }
                },
                'then': {
                    'required': ['graph_title', 'graph_type']
                }
            }
        ]

        self.schema = schema


    def prose_field_to_jsonschema(self, prose_field, is_required):
        """Convert a Prose.io field to a JSON Schema property.

        Parameters
        ----------
        prose_field : Dict
            A dict of information about a field, pulled from Prose.io schema

        Returns
        -------
        Dict
            A JSON Schema version of the field information
        """

        jsonschema_field = {}
        direct_mapping = {
            'help': 'description',
            'label': 'title',
            'value': 'default',
            'translation_key': 'translation_key',
            'scope': 'scope',
        }
        for prose_key in direct_mapping:
            if prose_key in prose_field:
                jsonschema_key = direct_mapping[prose_key]
                jsonschema_field[jsonschema_key] = prose_field[prose_key]

        # Most Prose.io fields are general text, numbers, or true/false.
        jsonschema_field['type'] = ['string', 'integer', 'number', 'boolean']

        # Everything else depends on what kind of element it is.
        el = prose_field['element']

        # Checkboxes can be boolean.
        if el == 'checkbox':
            jsonschema_field['type'] = 'boolean'

        # For non-required fields, also allow 'null'.
        if not is_required:
            # Make sure it is a list.
            if not isinstance(jsonschema_field['type'], list):
                jsonschema_field['type'] = [jsonschema_field['type']]
            # Add 'null' to the list.
            jsonschema_field['type'].append('null')

        # Selects and multiselects are a little complex.
        if el == 'select' or el == 'multiselect':
            any_of = []
            for prose_option in prose_field['options']:
                if 'translation_key' not in prose_option:
                    prose_option['translation_key'] = prose_option['name']
                jsonschema_option = {
                    'type': 'string',
                    'title': prose_option['name'],
                    'enum': [prose_option['value']],
                    'translation_key': prose_option['translation_key']
                }
                any_of.append(jsonschema_option)
            # Allow null if not required.
            if not is_required:
                any_of.append({
                    'type': 'null',
                    'title': 'Null',
                    'enum': [None]
                })
            if el == 'select':
                jsonschema_field['anyOf'] = any_of
            elif el == 'multiselect':
                jsonschema_field['type'] = 'array'
                jsonschema_field['items'] = {
                    'type': 'string',
                    'anyOf': any_of
                }

        return jsonschema_field
