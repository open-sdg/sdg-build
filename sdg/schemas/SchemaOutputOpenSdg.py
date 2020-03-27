# -*- coding: utf-8 -*-

import os
import json
from sdg.schemas import SchemaOutputBase

class SchemaOutputOpenSdg(SchemaOutputBase):
    """A class for outputing a schema to the Open SDG Prose.io/JSON file."""


    def write_schema(self, output_folder='meta', filename='schema.json'):
        """Write the Open SDG schema file to disk. Overrides parent.

        Parameters
        ----------
        output_folder : string
            The folder to write the schema output in
        filename : string
            The filename for writing the schema output
        """

        # Make sure the folder exists.
        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, filename)

        output = list()
        jsonschema = self.schema.schema

        # Convert the JSON Schema into a list of Prose-style fields.
        for key in self.schema.get_field_order():
            if key in jsonschema['properties']:
                prose_field = self.jsonschema_field_to_prose(jsonschema['properties'][key])
                output.append({
                    'name': key,
                    'field': prose_field
                })

        output_json = json.dumps(output)
        with open(output_path, 'w', encoding='utf-8') as outfile:
            outfile.write(output_json)


    def jsonschema_field_to_prose(self, jsonschema_field):
        """Convert a JSON Schema field to a Prose.io field.

        Parameters
        ----------
        jsonschema_field : Dict
            A dict of information about a field, pulled from JSON Schema

        Returns
        -------
        Dict
            A Prose.io-style version of the field information
        """

        prose_field = {}
        direct_mapping = {
            'description': 'help',
            'title': 'label',
            'default': 'value',
            'translation_key': 'translation_key',
            'scope': 'scope',
        }

        for jsonschema_key in direct_mapping:
            if jsonschema_key in jsonschema_field:
                prose_key = direct_mapping[jsonschema_key]
                prose_field[prose_key] = jsonschema_field[jsonschema_key]

        # Default to the "text" element type.
        prose_field['element'] = 'text'

        # Everything else depends on what kind of element it is.
        jsonschema_type = jsonschema_field['type']

        # Booleans should be checkboxes.
        if jsonschema_type == 'boolean':
            prose_field['element'] = 'checkbox'

        # Track whether we'll need to parse options later.
        jsonschema_options = False

        # Arrays should be multiselect.
        if jsonschema_type == 'array':
            prose_field['element'] = 'multiselect'
            jsonschema_options = jsonschema_field['items']['anyOf']

        # If 'anyOf' is set, this is a select.
        if 'anyOf' in jsonschema_field:
            prose_field['element'] = 'select'
            jsonschema_options = jsonschema_field['anyOf']

        if jsonschema_options:
            prose_options = list()
            for jsonschema_option in jsonschema_options:
                prose_option = {
                    'name': jsonschema_option['title'],
                    'value': jsonschema_option['enum'][0],
                }
                if 'translation_key' in jsonschema_option:
                    prose_option['translation_key'] = jsonschema_option['translation_key']
                prose_options.append(prose_option)
            prose_field['options'] = prose_options

        return prose_field
