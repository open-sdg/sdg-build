import os
from xml.etree import ElementTree as ET
from io import StringIO
from sdg.schemas import SchemaInputBase

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
        """Fetch and parse an XML file.

        Parameters
        ----------
        location : string
            Remote URL of the XML file or path to local file.
        strip_namespaces : boolean
            Whether or not to strip namespaces. This is helpful in cases where
            different implementations may use different namespaces/prefixes.
        """
        xml = self.fetch_file(location)
        it = ET.iterparse(StringIO(xml))
        if strip_namespaces:
            for _, el in it:
                if '}' in el.tag:
                    el.tag = el.tag.split('}', 1)[1]
        return it.root
