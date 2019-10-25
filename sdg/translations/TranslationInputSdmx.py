# -*- coding: utf-8 -*-

import os
from urllib.request import urlopen
import pandas as pd
import numpy as np
from xml.etree import ElementTree as ET
from io import StringIO
from sdg.translations import TranslationInputBase

class TranslationInputSdmx(TranslationInputBase):
    """A class for outputing translations in JSON format."""

    def __init__(self, dsd=''):
        self.dsd = dsd
        self.translations = {}


    def add_language(self, language):
        if language not in self.translations:
            self.translations[language] = {}


    def add_group(self, language, group):
        self.add_language(language)
        if group not in self.translations[language]:
            self.translations[language][group] = {}


    def add_translation(self, language, group, key, value):
        self.add_group(language, group)
        if key not in self.translations[language][group]:
            self.translations[language][group][key] = value


    def fetch_file(self, location):
        """Fetch a file, either on disk, or on the Internet.

        Parameters
        ----------
        location : String
            Either an http address, or a path on disk
        """
        file = None
        data = None
        if location.startswith('http'):
            file = urlopen(location)
            data = file.read().decode('utf-8')
        else:
            file = open(location)
            data = file.read()
        file.close()
        return data


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
        dsd = self.parse_xml(self.dsd)
        groups = {
            'category': {
                'xpath': './/Category',
                'translations': './/Name'
            },
            'codelist': {
                'xpath': './/Codelist',
                'translations': './/Name'
            },
            'code': {
                'xpath': './/Code',
                'translations': './/Name'
            },
            'concept': {
                'xpath': './/Concept',
                'translations': './/Name'
            }
        }
        for group in groups:
            tags = dsd.findall(groups[group]['xpath'])
            for tag in tags:
                key = tag.attrib['id']
                translations = tag.findall(groups[group]['translations'])
                for translation in translations:
                    if 'lang' not in translation.attrib:
                        continue
                    language = translation.attrib['lang']
                    self.add_translation(language, group, key, translation.text)

        print(self.translations)

