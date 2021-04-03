# -*- coding: utf-8 -*-

from xml.etree import ElementTree as ET
from io import StringIO
from sdg.translations import TranslationInputBase
from sdg import helpers

class TranslationInputSdmx(TranslationInputBase):
    """A class for importing translations from an SDMX DSD.

    This assumes that the "keys" of the translations will be the SDMX codes. So,
    if this is to be used with this library's SDMX import functionality, the
    import needs to import SDMX codes rather than text values.

    This imports only the codes in the "codelists" attached to all SDMX dimensions
    and attributes. In addition it imports the names of the dimensions and
    attributes themselves, as the 'CONCEPT_NAME' key.

    Each translation is put into a group according to the dimension/attribute id.

    Note that if you are using "dimension_map" in an SDMX input to rename columns,
    you will need to use the same "dimension_map" here.
    """

    def __init__(self, source='', dimension_map=None, **kwargs):
        """Constructor for the TranslationInputSdmx class.

        Parameters
        ----------
        source : string
            Inherits from TranslationInputBase.
        dimension_map : dict
            Meant to correspond with dimension_map from SdmxInputSdmx.
        """
        if dimension_map is None:
            dimension_map = {}
        self.dimension_map = dimension_map
        TranslationInputBase.__init__(self, source=source, **kwargs)


    def execute(self):
        TranslationInputBase.execute(self)
        dsd = helpers.sdmx.parse_xml(self.source, self.request_params)

        dimension_tags = dsd.findall('.//Dimension')
        self.add_translations_for_tags(dimension_tags, dsd)

        attribute_tags = dsd.findall('.//Attribute')
        self.add_translations_for_tags(attribute_tags, dsd)


    def add_translations_for_tags(self, tags, dsd):
        for tag in tags:
            if 'id' not in tag.attrib:
                # Not sure why this happens - possibly the "TimeDimension"?
                continue
            tag_id = tag.attrib['id']
            if tag_id in self.dimension_map:
                tag_id = self.dimension_map[tag_id]
                if tag_id == '':
                    continue
            concept_id = tag.find('.//ConceptIdentity/Ref').attrib['id']
            concept_xpath = ".//Concept[@id='{}']"
            concept = dsd.find(concept_xpath.format(concept_id))
            translations = concept.findall('.//Name')
            for translation in translations:
                if 'lang' not in translation.attrib:
                    continue
                language = translation.attrib['lang']
                value = translation.text
                self.add_translation(language, tag_id, tag_id, value)

            codelist_ref = tag.find('.//LocalRepresentation/Enumeration/Ref')
            if codelist_ref is None:
                # Some attributes don't have codelists.
                continue
            codelist_id = codelist_ref.attrib['id']
            codelist_xpath = ".//Codelist[@id='{}']"
            codelist = dsd.find(codelist_xpath.format(codelist_id))
            codes = codelist.findall('Code')
            for code in codes:
                translations = code.findall('Name')
                code_key = code.attrib['id']
                combined_for_dimension_map = tag_id + '|' + code_key
                if combined_for_dimension_map in self.dimension_map:
                    code_key = self.dimension_map[combined_for_dimension_map]
                    if code_key == '':
                        continue
                for translation in translations:
                    if 'lang' not in translation.attrib:
                        continue
                    language = translation.attrib['lang']
                    value = translation.text
                    self.add_translation(language, tag_id, code_key, value)
