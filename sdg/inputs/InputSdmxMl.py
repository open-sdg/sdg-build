import pandas as pd
import sdg
import requests
from sdg.inputs import InputSdmx

class InputSdmxMl(InputSdmx):
    """Sources of SDG data that are SDMX-ML format."""

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
        # Otherwise default to whatever is in the SDMX.
        codelist_id = self.dimension_id_to_codelist_id(dimension_id)
        if codelist_id:
            code = self.get_code(codelist_id, dimension_value_id)
            if code is not None:
                return code.find(".//Name").text
        # If still here, just return the SDMX ID.
        return dimension_value_id


    def get_attribute_value_name(self, attribute_id, attribute_value_id):
        """Determine the human-readable name of an attribute value.

        Parameters
        ----------
        attribute_id : string
            SDMX id of the Attribute
        attribute_value_id: string
            SDMX id of the Attribute value

        Returns
        -------
        string
            The human-readable name for the attribute value
        """
        map_key = attribute_id + '|' + attribute_value_id
        # First see if this is in our dimension map.
        if map_key in self.dimension_map:
            return self.dimension_map[map_key]
        # Aggregate values are always "_T", these can be empty strings.
        if attribute_value_id == '_T':
            return None
        # Otherwise default to whatever is in the SDMX.
        codelist_id = self.attribute_id_to_codelist_id(attribute_id)
        if codelist_id:
            code = self.get_code(codelist_id, attribute_value_id)
            if code is not None:
                return code.find(".//Name").text
        # If still here, just return the SDMX ID.
        return attribute_value_id


    def get_all_series(self):
        """Get the full series structure from the SDMX-ML.

        Returns
        -------
        dict
            Series structure from SDMX-JSON
        """
        return self.data.findall(".//Series")


    def get_series_dimensions(self, series):
        """Parse the dimensions/values for a particular series.

        Parameters
        ----------
        series : Element
            The XML element for the Series

        Returns
        -------
        dict
            A custom dict structure, dimension id keyed to value
        """
        dimensions = {}
        dimension_elements = series.findall(".//SeriesKey/Value")
        for element in dimension_elements:
            dimension_id = element.attrib['id']
            dimension_value_id = element.attrib['value']
            dimensions[dimension_id] = dimension_value_id
        return dimensions


    def get_series_attributes(self, series):
        """Parse the attributes/values for a particular series.

        Parameters
        ----------
        series : Element
            The XML element for the Series

        Returns
        -------
        dict
            A custom dict structure, attribute id keyed to value
        """
        attributes = {}
        attribute_elements = series.findall(".//Attributes/Value")
        for element in attribute_elements:
            attribute_id = element.attrib['id']
            attribute_value_id = element.attrib['value']
            attributes[attribute_id] = attribute_value_id
        return attributes


    def get_series_id(self, series):
        """Get the id for a Series.

        Parameters
        ----------
        series : Element
            The XML element for the Series
        """
        return series.find(".//SeriesKey/Value[@id='SERIES']").attrib['value']


    def get_indicators(self, series):
        """Get the indicator ids/names for a series.

        Parameters
        ----------
        series : Element
            The XML element for the Series

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


    def get_series_disaggregations(self, series):
        """Get the disaggregation categories/values for a series.

        Parameters
        ----------
        series : Element
            The XML element for the Series

        Returns
        -------
        dict
            Disaggregation values, keyed by category, for this series
        """
        disaggregations = {}
        dimensions = self.get_series_dimensions(series)
        for dimension_id in dimensions:
            if dimension_id == 'SERIES' or dimension_id in self.drop_dimensions:
                # Skip "SERIES" and anything set to be dropped.
                continue
            else:
                # Otherwise we will use this dimension as a disaggregation.
                dimension_name = self.get_dimension_name(dimension_id)
                dimension_value_id = dimensions[dimension_id]
                value_name = self.get_dimension_value_name(dimension_id, dimension_value_id)
                disaggregations[dimension_name] = value_name
        # Roughly the same for attributes (mainly for Unit of Measurement).
        attributes = self.get_series_attributes(series)
        for attribute_id in attributes:
            if attribute_id in self.drop_dimensions:
                continue
            else:
                attribute_name = self.get_dimension_name(attribute_id)
                attribute_value_id = attributes[attribute_id]
                value_name = self.get_attribute_value_name(attribute_id, attribute_value_id)
                disaggregations[attribute_name] = value_name

        return disaggregations


    def get_observations(self, series):
        """Get the list of observations for a particular series.

        Parameters
        ----------
        series : Element
            The XML element for the Series

        Returns
        -------
        list
            A list of Obs XML elements for a series
        """
        return series.findall(".//Obs")


    def get_series_data(self, series):
        """Convert a set of observations into a list of rows.

        Parameters
        ----------
        series : Element
            The XML element for the Series

        Returns
        -------
        List
            The rows of data for this series.
        """
        disaggregations = self.get_series_disaggregations(series)
        observations = self.get_observations(series)
        rows = []
        for observation in observations:
            year = observation.find(".//ObsDimension[@id='TIME_PERIOD']").attrib['value']
            value = observation.find(".//ObsValue").attrib['value']
            row = self.get_row(year, value, disaggregations)
            rows.append(row)
        return rows


    def fetch_data(self):
        """Fetch the data from the source."""
        self.data = self.parse_xml(self.source)
