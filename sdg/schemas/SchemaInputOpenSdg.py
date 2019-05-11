import os
import yaml

from sdg.schemas import SchemaInputBase

class SchemaInputOpenSdg(SchemaInputBase):
    """Input schema from Open SDG format and validate metadata."""


    def load_schema(self):
        """Import a _prose.yml schema into JSON Schema."""

        with open(self.schema_path, encoding="UTF-8") as stream:
            config = next(yaml.safe_load_all(stream))

        schema = {
            "type": "object",
            "properties": {}
        }

        # Convert the Prose.io metadata into JSON Schema.
        for field in config['prose']['metadata']['meta']:
            jsonschema_field = self.prose_field_to_jsonschema(field['field'])
            schema['properties'][field['name']] = jsonschema_field

        # For Open SDG, certain fields are required. We have to hardcode these
        # here, because _prose.yml has no mechanism for requiring fields.
        # TODO: Should we just add "required" properties in _prose.yml, purely
        # for this purpose?
        schema['required'] = ['published', 'reporting_status']

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
                        'published': { 'const': True },
                        'data_non_statistical': { 'const': False }
                    }
                },
                'then': {
                    'required': ['graph_title', 'graph_type']
                }
            }
        ]

        self.schema = schema


    def prose_field_to_jsonschema(self, prose_field):
        """Convert a Prose.io field to a JSON Schema property."""

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

        # Most Prose.io fields would be "string" or "integer" type in JSON Schema.
        jsonschema_field['type'] = ['string', 'integer']

        # Everything else depends on what kind of element it is.
        el = prose_field['element']

        # Checkboxes can be boolean.
        if el == 'checkbox':
            jsonschema_field['type'] = 'boolean'

        # Selects and multiselects are a little complex.
        elif el == 'select' or el == 'multiselect':
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
            if el == 'select':
                jsonschema_field['anyOf'] = any_of
            elif el == 'multiselect':
                jsonschema_field['type'] = 'array'
                jsonschema_field['items'] = {
                    'type': 'string',
                    'anyOf': any_of
                }

        return jsonschema_field