import pandas as pd
import sdg
import requests
from sdg.inputs import InputSdmx

class InputSdmxMl(InputSdmx):
    """Sources of SDG data that are SDMX-ML format."""

    def get_all_series(self):
        """Get the full series structure from the SDMX-ML.

        Returns
        -------
        dict
            Series structure from SDMX-JSON
        """
        return self.data.findall(".//Series")


    def get_dimension_value(self, dimension_id, dimension_value_id):
        """Return a human-readable value from a value code for a dimension.

        Parameters
        ----------
        string : dimension_id
            The SDMX id of the dimension

        string : dimension_value_id
            The SDMX id of the dimension value
        """
        dimension = self.dsd.find(".//DimensionList/Dimension[@id='" + dimension_id + "']")
        codelist_id = dimension.find(".//Enumeration/Ref").attrib['id']
        code = self.get_code(codelist_id, dimension_value_id)
        return code.find(".//Name").text


    def get_attribute_value(self, attribute_id, attribute_value_id):
        """Return a human-readable value from a value code for an attribute.

        Parameters
        ----------
        string : attribute_id
            The SDMX id of the attribute

        string : attribute_value_id
            The SDMX id of the attribute value
        """
        attribute = self.dsd.find(".//AttributeList/Attribute[@id='" + attribute_id + "']")
        codelist_id = attribute.find(".//Enumeration/Ref").attrib['id']
        code = self.get_code(codelist_id, attribute_value_id)
        return code.find(".//Name").text


    def get_series_dimensions(self, series):
        """Parse the dimensions/attributes/values for a particular series.

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
            value = self.get_dimension_value(dimension_id, dimension_value_id)
            dimensions[dimension_id] = value
        # We also add on attributes, as if they were dimensions too.
        # TODO: WHY is this failing?
        #attribute_elements = series.findall(".//Attributes/Value")
        #for element in attribute_elements:
        #    attribute_id = element.attrib['id']
        #    attribute_value_id = element.attrib['value']
        #    value = self.get_attribute_value(attribute_id, attribute_value_id)
        #    dimensions[attribute_id] = value
        return dimensions


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
        for key in dimensions:
            dimension = dimensions[key]
            print(key)
            continue
            series_id = dimension['dimension']['id']
            if series_id == 'SERIES' or series_id in self.drop_dimensions:
                # Skip "SERIES" and anything set to be dropped.
                continue
            elif self.drop_singleton_dimensions and len(dimension['dimension']['values']) < 2:
                # Ignore dimensions with only 1 variation.
                continue
            else:
                # Otherwise we will use this dimension as a disaggregation.
                dimension_name = self.get_dimension_name(dimension['dimension'])
                value_name = self.get_dimension_value_name(dimension['dimension'], dimension['value'])
                disaggregations[dimension_name] = value_name
        return disaggregations


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
        # TODO: Continue here....
        disaggregations = self.get_series_disaggregations(series)
        return []
        observations = self.get_observations(series)
        rows = []
        for observation_key in observations:
            year = self.get_years()[int(observation_key)]['name']
            value = observations[observation_key][0]
            row = self.get_row(year, value, disaggregations)
            rows.append(row)
        return rows


    def fetch_data(self):
        """Fetch the data from the source."""
        self.data = self.parse_xml(self.source)
