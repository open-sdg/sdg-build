import sdg
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
                 indicator_id_xpath=".//Annotation[AnnotationTitle='Indicator']/AnnotationText",
                 indicator_name_xpath=".//Annotation[AnnotationTitle='IndicatorTitle']/AnnotationText"):
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


    def dimension_id_to_codelist_id(self, dimension_id):
        xpath = ".//DimensionList/Dimension[@id='{}']"
        dimension = self.dsd.find(xpath.format(dimension_id))
        return dimension.find(".//Enumeration/Ref").attrib['id']



    def attribute_id_to_codelist_id(self, attribute_id):
        xpath = ".//AttributeList/Attribute[@id='{}']"
        attribute = self.dsd.find(xpath.format(attribute_id))
        ref_element = attribute.find(".//Enumeration/Ref")
        return ref_element.attrib['id'] if ref_element is not None else None


    def get_codes(self, codelist_id):
        """Get all the SDMX Codes for a particular CodeList.

        Parameters
        ----------
        string : codelist_id
            The id of the CodeList to get Codes from

        Returns
        -------
        list of Elements
            The XML elements for each Code in the CodeList
        """
        xpath = ".//Codelist[@id='{}']/Code"
        return self.dsd.findall(xpath.format(codelist_id))


    def get_code(self, codelist_id, code_id):
        """Get a particular SDMX Code in a particular CodeList.

        Parameters
        ----------
        string : codelist_id
            The id of the CodeList to look in

        string : code_id
            The id of the Code to get

        Returns
        -------
        Element
            The XML element for the Code
        """
        xpath = ".//Codelist[@id='{}']/Code[@id='{}']"
        return self.dsd.find(xpath.format(codelist_id, code_id))


    def get_concept(self, concept_id):
        """Get the Concept from the SDMX DSD.

        Parameters
        ----------
        string : concept_id
            The SDMX ID for the Concept

        Returns
        -------
        Element
            The Concept XML element
        """
        xpath = ".//Concept[@id='{}']"
        return self.dsd.find(xpath.format(concept_id))


    def get_concept_name(self, concept_id):
        """Get the human-readable Concept name from the SDMX DSD.

        Parameters
        ----------
        string : concept_id
            The SDMX ID for the Concept

        Returns
        -------
        string
            The human-readable SDMX Concept name
        """
        concept = self.get_concept(concept_id)
        return concept.find(".//Name").text


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
        codes = self.get_codes('CL_SERIES')
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


    def drop_singleton_columns(self, df):
        if self.drop_singleton_dimensions:
            special_cols = ['Year', 'Value']
            for col in df.columns:
                if col in special_cols:
                    continue
                if len(df[col].unique()) == 1:
                    df.drop(col, inplace=True, axis=1)
        return df


    def execute(self):
        """Execute this input. Overrides parent."""

        # Fetch the response from the SDMX endpoint.
        self.fetch_data()

        # SDMX divides the data into series, but we want to divide
        # the data into indicators. Indicators contain multiple series,
        # so we need to loop through the series and build up indicators.
        indicator_data = {}
        indicator_names = {}

        # Loop through each "series" in the SDMX-JSON.
        for series in self.get_all_series():

            # Get the indicator ids (some series apply to multiple indicators).
            indicators = self.get_indicators(series)

            # Skip any series if we cannot figure out the indicator id.
            if indicators is None:
                continue

            for indicator_id in indicators:
                # Get the indicator name if needed.
                if indicator_id not in indicator_names:
                    indicator_names[indicator_id] = indicators[indicator_id]
                    # Also start off an empty list of rows.
                    indicator_data[indicator_id] = []

                # Get the rows of data for this series.
                indicator_data[indicator_id].extend(self.get_series_data(series))

        # Create the Indicator objects.
        for indicator_id in indicator_data:
            data = self.create_dataframe(indicator_data[indicator_id])
            data = self.drop_singleton_columns(data)
            name = indicator_names[indicator_id] if self.import_names else None
            indicator = sdg.Indicator(indicator_id, data=data, name=name)
            self.indicators[indicator_id] = indicator
