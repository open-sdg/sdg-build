# -*- coding: utf-8 -*-

from xml.etree import ElementTree as ET
from io import StringIO
from sdg.translations import TranslationInputSdmx
from sdg import helpers

class TranslationInputSdmxMsd(TranslationInputSdmx):
    """A class for importing translations from an SDMX MSD."""

    def execute(self):
        msd = helpers.sdmx.parse_xml(self.source, self.request_params)
        for concept in msd.findall('.//Concept'):
            key = concept.attrib['id']
            parent = concept.find('./Parent/Ref')
            group = key if parent is None else parent.attrib['id']
            for translation in concept.findall('./Name'):
                if 'lang' not in translation.attrib:
                    continue
                language = translation.attrib['lang']
                value = translation.text
                self.add_translation(language, group, key, value)
