"""
This output assumes the following:
1. A DSD is already created and available
2. All columns in the data correspond exactly
   to dimension IDs.
3. All values in the columns correspond exactly
   to codes in those dimensions.
"""

import os
import json
import copy
import sdg
import pandas as pd
from urllib.request import urlopen
from xml.etree import ElementTree as ET
from io import StringIO
from sdg.outputs import OutputBase

class OutputSdmxMl(OutputBase):
    """Output SDG data/metadata in SDMX-ML."""


    def __init__(self, inputs, schema, output_folder='_site', translations=None,
                 indicator_options=None, dsd='https://unstats.un.org/sdgs/files/SDG_DSD.xml'):
        """Constructor for OutputSdmxMl.

        Parameters
        ----------

        Inherits all the parameters from OutputBase, plus the following optional
        arguments (see above for the default values):

        dsd : string
            Remote URL of the SDMX DSD (data structure definition) or path to
            local file.
        """
        if translations is None:
            translations = []

        OutputBase.__init__(self, inputs, schema, output_folder, translations, indicator_options)
        self.dsd = self.parse_xml(dsd)


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


    def build(self, language=None):
        """Write the SDMX output. Overrides parent."""
        status = True



        return status


    def get_documentation_title(self):
        return 'SDMX output'


    def get_documentation_content(self, languages=None):
        if languages is None:
            languages = ['']

        indicator_ids = self.get_documentation_indicator_ids()

        endpoint = '{language}/sdmx/{indicator_id}.xml'
        output = '<p>' + self.get_documentation_description() + ' Examples are below:<p>'
        output += '<ul>'
        for language in languages:
            path = endpoint.format(language=language, indicator_id='all')
            output += '<li><a href="' + path + '">' + path + '</a></li>'
            for indicator_id in indicator_ids:
                path = endpoint.format(language=language, indicator_id=indicator_id)
                output += '<li><a href="' + path + '">' + path + '</a></li>'
        output += '<li>etc...</li>'
        output += '</ul>'

        return output


    def get_documentation_description(self):
        description = (
            "This output has an SDMX file for each indicator's data, "
            "plus one SDMX file with all indicator data. In addition, "
            "it has an SDMX file for each indicator's metadata, plus "
            "one SDMX file with all indicator metadata."
        )
        return description
