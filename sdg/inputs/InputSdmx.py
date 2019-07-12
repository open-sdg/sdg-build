


from sdg.inputs import InputBase
from xml.etree import ElementTree as ET

class InputSdmx(InputBase):
    """Sources of SDG data that are SDMX format."""

    def __init__(self,
                 source='',
                 drop_dimensions=[],
                 drop_singleton_dimensions=True,
                 dimension_map={},
                 import_names=True,
                 dsd='https://unstats.un.org/sdgs/files/SDG_DSD.xml',
                 namespaces = {
                     "mes": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message",
                     "str": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure",
                     "com": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common",
                 },
                 series_xpath=".//str:Codelist[@id='CL_SERIES']/str:Code",
                 indicator_id_xpath=".//com:Annotation[com:AnnotationTitle='Indicator']/com:AnnotationText"):
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
        namespaces : dict
            A dict of namespaces that are used in the SDMX
        series_xpath : string
            An xpath query to find the collection of Series codes in the DSD
        indicator_id_xpath : string
            An xpath query to find the indicator id within each Series code
        """
        self.source = source
        self.dsd = self.parse_dsd(dsd)
        self.namespaces = namespaces
        self.drop_dimensions = drop_dimensions
        self.drop_singleton_dimensions = drop_singleton_dimensions
        self.dimension_map = dimension_map
        self.import_names = import_names
        self.series_xpath = series_xpath
        self.indicator_id_xpath = indicator_id_xpath
        self.series_dimensions = {}
        InputBase.__init__(self)


    def parse_dsd(self, location):
        """Fetch and parse the XML DSD (data structure definition).

        Parameters
        ----------
        location : string
            Remote URL of the SDMX DSD (data structure definition) or path to
            local file.
        """
        data = self.fetch_file(location)
        tree = ET.fromstring(data)
        return tree


    def get_indicator_id_map(self):
        """Get a mapping of SDMX "SERIES" codes to indicator IDs (1.1.1, etc.)"""
        # To save processing, return a cached version if available.
        if hasattr(self, 'indicator_id_map'):
            return self.indicator_id_map
        # Otherwise calculate it.
        series_to_indicator_ids = {}
        codes = self.dsd.findall(self.series_xpath, self.namespaces)
        for code in codes:
            code_id = code.attrib['id']
            indicator_ids = code.findall(self.indicator_id_xpath, self.namespaces)
            indicator_ids = [indicator_id.text for indicator_id in indicator_ids]
            # Normalize the indicator ids.
            indicator_ids = [self.normalize_indicator_id(indicator_id) for indicator_id in indicator_ids]
            series_to_indicator_ids[code_id] = indicator_ids
        # Cache it for later.
        self.indicator_id_map = series_to_indicator_ids
        return series_to_indicator_ids