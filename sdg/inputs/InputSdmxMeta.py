import pandas as pd
from sdg.inputs import InputSdmx

class InputSdmxMeta(InputSdmx):
    """Sources of SDG metadata that are SDMX messages."""

    def execute(self, indicator_options):
        """Fetch all data/metadata from source, fetching a list of indicators."""
        if self.source is None or self.source == '':
            # Default to global metadata from the UN SDG Metadata API, querying "G.ALL.1", which
            # means global (G), all series (ALL), and World (1).
            self.source = 'https://unstats.un.org/SDGMetadataAPI/api/Metadata/SDMXReport/G.ALL.1'
        self.data = self.parse_xml(self.source)
        indicator_map = self.get_indicator_map()
        for metadata_set in self.get_metadata_sets():
            series_id = self.get_series_for_metadata_set(metadata_set)
            indicator_ids = indicator_map[series_id]
            metadata = self.get_metadata_set_concepts(metadata_set)
            for indicator_id in indicator_ids:
                name = indicator_ids[indicator_id]
                self.add_indicator(indicator_id, name=name, meta=metadata, options=indicator_options)


    def get_metadata_sets(self):
        return self.data.findall('.//MetadataSet')


    def get_series_for_metadata_set(self, metadata_set):
        return metadata_set.find(".//ReferenceValue[@id='DIMENSION_DESCRIPTOR_VALUES_TARGET']/DataKey/KeyValue[@id='SERIES']/Value").text


    def get_metadata_set_concepts(self, metadata_set):
        concepts = metadata_set.findall('.//ReportedAttribute')
        metadata = {}
        for concept in concepts:
            concept_id = concept.attrib['id']
            concept_value = concept.find('./Text').text
            if concept_value is not None:
                metadata[concept_id] = concept_value
        return metadata
