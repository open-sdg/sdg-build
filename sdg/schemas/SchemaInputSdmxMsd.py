import os
from urllib.request import urlopen
from xml.etree import ElementTree as ET
from io import StringIO
from sdg.schemas import SchemaInputBase
from sdg import helpers

class SchemaInputSdmxMsd(SchemaInputBase):
    """Input schema from SDMX MSD."""


    def load_schema(self):
        """Import the SDMX MSD into JSON Schema. Overrides parent."""

        schema = {
            "type": "object",
            "properties": {}
        }

        msd = self.parse_xml(self.schema_path)
        for concept in msd.findall('.//Concept'):
            concept_id = concept.attrib['id']
            self.add_item_to_field_order(concept_id)
            concept_name = concept.find('./Name').text
            concept_description = concept.find('./Description').text
            parent = concept.find('./Parent/Ref')
            key_parts = [concept_id, concept_id] if parent is None else [parent.attrib['id'], concept_id]
            translation_key = '.'.join(key_parts)
            jsonschema_field = {
                'type': ['string', 'null'],
                'title': concept_name,
                'description': concept_description,
                'translation_key': translation_key,
            }
            if self.scope is not None:
                jsonschema_field['scope'] = self.scope
            schema['properties'][concept_id] = jsonschema_field

        self.schema = schema

    def parse_xml(self, location, strip_namespaces=True):
        return helpers.sdmx.parse_xml(location, request_params=self.request_params)


    def fetch_file(self, location):
        return helpers.files.read_file(location, request_params=self.request_params)
