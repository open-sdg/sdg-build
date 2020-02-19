# -*- coding: utf-8 -*-

from xml.etree import ElementTree as ET
from io import StringIO
from sdg.translations import TranslationInputBase

class TranslationInputSdmx(TranslationInputBase):
    """A class for importing translations from an SDMX DSD.

    This assumes that the "keys" of the translations will be the SDMX ids. So,
    if this is to be used with this library's SDMX import functionality, the
    import needs to import SDMX ids rather than text values. This is not yet
    implemented, so this is only a preliminary example class.
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
                for attrib in el.attrib:
                    if '}' in attrib:
                        val = el.attrib[attrib]
                        del el.attrib[attrib]
                        attrib = attrib.split('}', 1)[1]
                        el.attrib[attrib] = val

        return it.root


    def execute(self):
        dsd = self.parse_xml(self.source)
        groups = {
            'category': './/Category',
            'codelist': './/Codelist',
            'concept': './/Concept',
        }
        for group in groups:
            tags = dsd.findall(groups[group])
            for tag in tags:
                key = tag.attrib['id']
                translations = tag.findall('.//Name')
                for translation in translations:
                    if 'lang' not in translation.attrib:
                        continue
                    language = translation.attrib['lang']
                    value = translation.text
                    self.add_translation(language, group, key, value)

        # We treat Code elements differently. Because there can be duplicates,
        # we use the Codelist ids are the "group".
        codelists = dsd.findall('.//Codelist')
        for codelist in codelists:
            group = codelist.attrib['id']
            codes = codelist.findall('Code')
            for code in codes:
                translations = code.findall('Name')
                key = code.attrib['id']
                for translation in translations:
                    if 'lang' not in translation.attrib:
                        continue
                    language = translation.attrib['lang']
                    value = translation.text
                    self.add_translation(language, group, key, value)
