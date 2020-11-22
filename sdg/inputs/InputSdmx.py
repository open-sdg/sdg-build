import sdg
from sdg.inputs import InputBase
from xml.etree import ElementTree as ET
from io import StringIO
import pandas as pd
import numpy as np

class InputSdmx(InputBase):
    """Sources of SDG data that are SDMX format."""

    def __init__(self,
                 source='',
                 drop_dimensions=None,
                 drop_singleton_dimensions=True,
                 dimension_map=None,
                 indicator_id_map=None,
                 import_names=True,
                 import_codes=False,
                 import_translation_keys=False,
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
        indicator_id_map : dict
            A dict for mapping SDMX series codes to indicator ids. Normally this
            is not needed, but sometimes the DSD may contain typos or mistakes,
            or the DSD may not contain any reference to the indicator ID numbers.
            This need not contain all indicator ids, only those that need it.
            If a particular series should be mapped to multiple indicators, then
            they can be a list of strings. Otherwise each indicator is a string.
            For example:
            {
                'AB_CD_EF_1': '1-2-1',
                'UV_WX_YZ_1': ['1-3-1', '5-1-1'],
            }
        import_names : boolean
            Whether to import names. Set to False to rely on global names
        import_codes : boolean
            Whether to import SDMX codes instead of text values. Set to True
            to import codes. This overrides the deprecated "import_translation_keys"
            and inherits its value if set.
        dsd : string
            Remote URL of the SDMX DSD (data structure definition) or path to
            local file.
        indicator_id_xpath : string
            An xpath query to find the indicator id within each Series code
        indicator_name_xpath : string
            An xpath query to find the indicator name within each Series code
        """
        if drop_dimensions is None:
            drop_dimensions = []
        if dimension_map is None:
            dimension_map = {}
        if indicator_id_map is None:
            indicator_id_map = {}

        self.source = source
        self.dsd = self.parse_xml(dsd)
        self.drop_dimensions = drop_dimensions
        self.drop_singleton_dimensions = drop_singleton_dimensions
        self.dimension_map = dimension_map
        self.indicator_id_map = indicator_id_map
        self.import_names = import_names
        self.import_codes = import_codes
        # Also use deprecated import_translation_keys.
        if not import_codes and import_translation_keys:
            self.import_codes = import_translation_keys
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
        it = ET.iterparse(StringIO(xml))
        if strip_namespaces:
            for _, el in it:
                if '}' in el.tag:
                    el.tag = el.tag.split('}', 1)[1]
        return it.root


    def dimension_id_to_codelist_id(self, dimension_id):
        xpath = ".//DimensionList/Dimension[@id='{}']"
        dimension = self.dsd.find(xpath.format(dimension_id))
        # If not found, maybe it is an Attribute.
        if dimension is None:
            xpath = ".//AttributeList/Attribute[@id='{}']"
            dimension = self.dsd.find(xpath.format(dimension_id))
        ref_element = dimension.find(".//Enumeration/Ref")
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
        if self.import_codes:
            return concept_id
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
            # First check to see if the indicator ids are hardcoded.
            if code_id in self.indicator_id_map:
                indicator_ids = self.indicator_id_map[code_id]
                # Make sure it is a list, even if only one.
                if not isinstance(indicator_ids, list):
                    indicator_ids = [indicator_ids]
            else:
                # If indicator_ids are not hardcoded, try to get them from the DSD.
                indicator_ids = code.findall(self.indicator_id_xpath)
                indicator_ids = [element.text for element in indicator_ids]
            # Normalize the indicator ids.
            indicator_ids = [self.normalize_indicator_id(inid) for inid in indicator_ids]
            # Now get the indicator names from the DSD.
            indicator_names = code.findall(self.indicator_name_xpath)
            # Before going further, make sure there is an indicator name for
            # each indicator id.
            if len(indicator_ids) > len(indicator_names):
                for i in range(len(indicator_ids) - len(indicator_names)):
                    # If there were more indicator ids than indicator names,
                    # just pad the list of names with the first one.
                    indicator_names.append(indicator_names[0])
            elif len(indicator_names) > len(indicator_ids):
                # If there were more indicator names than indicator ids, we
                # just have to arbitrarily pick the first ones.
                indicator_names = indicator_names[0:len(indicator_ids)]

            # Now loop through, normalize and store the ids and names per series id.
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


    def ensure_numeric_values(self, df, indicator_id):
        """SDMX values get imported as strings, so we need to convert them here.

        Parameters
        ----------
        Dataframe : df
            The dataframe containing a 'Value' column.

        string : indicator_id
            The indicator id that we are fixing.

        Returns
        -------
        Dataframe
            The same dataframe with all numeric values.
        """
        try:
            df['Value'] = pd.to_numeric(df['Value'], errors='raise')
        except KeyError as e:
            print('WARNING: Indicator ' + indicator_id + ' did not have a value column - inserting null values.')
            df['Value'] = np.nan
        except ValueError as e:
            print('WARNING: Indicator ' + indicator_id + ' has a non-numeric value: ' + str(e))
        return df


    def get_dimension_name(self, dimension_id):
        """Determine the human-readable name of a dimension.

        Parameters
        ----------
        dimension_id : string
            The SDMX id of the dimension

        Returns
        -------
        string
            The human-readable name for the dimension
        """
        # First see if this is in our dimension map.
        if dimension_id in self.dimension_map:
            return self.dimension_map[dimension_id]
        # Otherwise default to whatever is in the DSD.
        return self.get_concept_name(dimension_id)


    def get_dimension_value_name(self, dimension_id, dimension_value_id):
        """Determine the human-readable name of a dimension value.

        Parameters
        ----------
        dimension_id : string
            SDMX id of the Dimension
        dimension_value_id: string
            SDMX id of the Dimension value

        Returns
        -------
        string
            The human-readable name for the dimension_value
        """
        map_key = dimension_id + '|' + dimension_value_id
        # First see if this is in our dimension map.
        if map_key in self.dimension_map:
            return self.dimension_map[map_key]
        # Aggregate values are always "_T", these can be empty strings.
        if dimension_value_id == '_T':
            return None
        codelist_id = self.dimension_id_to_codelist_id(dimension_id)
        if codelist_id:
            # Return the ids if necessary.
            if self.import_codes:
                return dimension_value_id
            # Otherwise default to whatever is in the SDMX.
            code = self.get_code(codelist_id, dimension_value_id)
            if code is not None:
                return code.find(".//Name").text
        # If still here, just return the SDMX ID.
        return dimension_value_id


    def get_indicators(self, series):
        """Get the indicator ids/names for a series.

        Parameters
        ----------
        series : mixed
            The variable for the series, depending on the needs of the subclass

        Returns
        -------
        list
            Indicator ids for this series
        """
        series_id = self.get_series_id(series)
        indicator_map = self.get_indicator_map()
        if series_id not in indicator_map:
            return None
        return indicator_map[series_id]


    def execute(self, indicator_options):
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
            if not indicator_data[indicator_id]:
                continue
            data = self.create_dataframe(indicator_data[indicator_id])
            data = self.drop_singleton_columns(data)
            data = self.ensure_numeric_values(data, indicator_id)
            name = indicator_names[indicator_id] if self.import_names else None
            self.add_indicator(indicator_id, data=data, name=name, options=indicator_options)
