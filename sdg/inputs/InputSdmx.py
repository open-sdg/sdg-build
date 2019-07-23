from sdg.inputs import InputBase
from xml.etree import ElementTree as ET
from io import StringIO

class InputSdmx(InputBase):
    """Sources of SDG data that are SDMX format."""

    def __init__(self,
                 source='',
                 drop_dimensions=[],
                 drop_singleton_dimensions=True,
                 dimension_map={},
                 import_names=True,
                 dsd='https://unstats.un.org/sdgs/files/SDG_DSD.xml',
                 indicator_id_xpath=".//com:Annotation[com:AnnotationTitle='Indicator']/com:AnnotationText",
                 indicator_name_xpath=".//com:Annotation[com:AnnotationTitle='IndicatorTitle']/com:AnnotationText"):
        """Constructor for InputSdmx.

        Parameters
        ----------
        source : string
            Remote URL of the SDMX source, or path to local SDMX file.
        drop_dimensions : list
            List of SDMX dimensions/attributes to ignore
        drop_singleton_dimensions : boolean
            If True, drop dimensions/attributes with only 1 variation
        dimension_map : dict
            A dict for mapping SDMX ids to human-readable names. For dimension
            names, the key is simply the dimension id. For dimension value names,
            the key is the dimension id and value id, separated by a pipe (|).
            This also includes attributes.
        import_names : boolean
            Whether to import names. Set to False to rely on global names
        dsd : string
            Remote URL of the SDMX DSD (data structure definition) or path to
            local file.
        indicator_id_xpath : string
            An xpath query to find the indicator id within each Series code
        indicator_name_xpath : string
            An xpath query to find the indicator name within each Series code
        """
        self.source = source
        self.dsd = self.parse_xml(dsd)
        self.drop_dimensions = drop_dimensions
        self.drop_singleton_dimensions = drop_singleton_dimensions
        self.dimension_map = dimension_map
        self.import_names = import_names
        self.indicator_id_xpath = indicator_id_xpath
        self.indicator_name_xpath = indicator_name_xpath
        self.series_dimensions = {}
        InputBase.__init__(self)


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
        it = ET.iterparse(StringIO(xml.decode('utf-8')))
        if strip_namespaces:
            for _, el in it:
                if '}' in el.tag:
                    el.tag = el.tag.split('}', 1)[1]
        return it.root


    def get_indicator_map(self):
        """Get a mapping of SDMX "SERIES" codes to indicator IDs and names.

        Returns
        -------
        dict
            Dict of series codes keyed to dicts of indicator ids keyed to names.
            Example:
            'GB_XPD_RSDV':
                '9-5-1': 'Research and development expenditure as a proportion of GDP',
                '9-5-2': 'etc...',
        """
        # To save processing, return a cached version if available.
        if hasattr(self, 'indicator_map'):
            return self.indicator_map
        # Otherwise calculate it.
        series_to_indicators = {}
        codes = self.dsd.findall(".//Codelist[@id='CL_SERIES']/Code")
        for code in codes:
            code_map = {}
            code_id = code.attrib['id']
            indicator_ids = code.findall(self.indicator_id_xpath)
            indicator_ids = [self.normalize_indicator_id(element.text) for element in indicator_ids]
            indicator_names = code.findall(self.indicator_name_xpath)
            for index, element in enumerate(indicator_names):
                indicator_id = indicator_ids[index]
                indicator_name = self.normalize_indicator_name(element.text, indicator_id)
                code_map[indicator_id] = indicator_name
            series_to_indicators[code_id] = code_map
        # Cache it for later.
        self.indicator_map = series_to_indicators
        return series_to_indicators