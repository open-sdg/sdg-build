# -*- coding: utf-8 -*-

from xml.etree import ElementTree as ET
from io import StringIO
from sdg.translations import TranslationInputBase

class TranslationInputSdmx(TranslationInputBase):
    """A class for importing translations from an SDMX DSD.

    This assumes that the "keys" of the translations will be the SDMX codes. So,
    if this is to be used with this library's SDMX import functionality, the
    import needs to import SDMX codes rather than text values.

    This imports only the codes in the "codelists" attached to all SDMX dimensions
    and attributes. In addition it imports the names of the dimensions and
    attributes themselves, as the 'CONCEPT_NAME' key.

    Each translation is put into a group according to the dimension/attribute id.
    """


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
                for attrib in list(el.attrib.keys()):
                    if '}' in attrib:
                        val = el.attrib[attrib]
                        del el.attrib[attrib]
                        attrib = attrib.split('}', 1)[1]
                        el.attrib[attrib] = val

        return it.root


    def execute(self):
        dsd = self.parse_xml(self.source)

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
                for translation in translations:
                    if 'lang' not in translation.attrib:
                        continue
                    language = translation.attrib['lang']
                    value = translation.text
                    self.add_translation(language, tag_id, code_key, value)
