# -*- coding: utf-8 -*-

from sdg.data_schemas import DataSchemaInputBase
import sdmx
from urllib.request import urlretrieve
from frictionless import Schema

class DataSchemaInputSdmxDsd(DataSchemaInputBase):
    """A class for importing a single schema from an SDMX DSD.
    The source parameter should be a path or URL to a SDMX DSD."""


    def load_all_schema(self):
        if self.source is None:
            self.source = 'https://registry.sdmx.org/ws/public/sdmxapi/rest/datastructure/IAEG-SDGs/SDG/latest/?format=sdmx-2.1&detail=full&references=children'
        dsd = self.retrieve_dsd(self.source)
        schema = {'fields': []}
        for dimension in dsd.dimensions:
            # Skip the TIME_PERIOD dimension because it is used as the "observation dimension".
            if dimension.id == 'TIME_PERIOD':
                continue
            field = {
                'name': dimension.id,
                'title': str(dimension.concept_identity.name),
            }
            if dimension.local_representation is not None and dimension.local_representation.enumerated is not None:
                field['constraints'] = {
                    'enum': [code.id for code in dimension.local_representation.enumerated]
                }
            schema['fields'].append(field)

        for attribute in dsd.attributes:
            field = {
                'name': attribute.id,
                'title': str(attribute.concept_identity.name),
            }
            if attribute.local_representation is not None and attribute.local_representation.enumerated is not None:
                field['constraints'] = {
                    'enum': [code.id for code in attribute.local_representation.enumerated]
                }
            schema['fields'].append(field)

        # For the SDMX DSD, we use a single schema for all indicators.
        self.schema_fallback = Schema(schema)
        # Return an empty dict for the indicator-specific schema.
        return {}


    def retrieve_dsd(self, dsd):
        if dsd.startswith('http'):
            urlretrieve(dsd, 'SDG_DSD.xml')
            dsd = 'SDG_DSD.xml'
        msg = sdmx.read_sdmx(dsd)
        return msg.structure[0]
