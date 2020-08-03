import pandas as pd
import sdg
import requests
from sdg.inputs import InputSdmx

class InputSdmxMl_Structure(InputSdmx):
    """Sources of SDG data that are SDMX-ML format.

    Specifically this supports Version 2.1 of SDMX-ML "Structure" format.
    """

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
        # Also gather attributes as if they were dimensions.
        attribute_elements = series.findall(".//Attributes/Value")
        for element in attribute_elements:
            attribute_id = element.attrib['id']
            attribute_value_id = element.attrib['value']
            dimensions[attribute_id] = attribute_value_id
        return dimensions


    def get_series_id(self, series):
        """Get the id for a Series.

        Parameters
        ----------
        series : Element
            The XML element for the Series
        """
        return series.find(".//SeriesKey/Value[@id='SERIES']").attrib['value']


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
            if dimension_id in self.drop_dimensions:
                # Skip anything set to be dropped.
                continue
            else:
                # Otherwise we will use this dimension as a disaggregation.
                dimension_name = self.get_dimension_name(dimension_id)
                dimension_value_id = dimensions[dimension_id]
                value_name = self.get_dimension_value_name(dimension_id, dimension_value_id)
                disaggregations[dimension_name] = value_name

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
            obsvalue = observation.find(".//ObsValue")
            if obsvalue is None:
                continue
            value = obsvalue.attrib['value']
            row = self.get_row(year, value, disaggregations)
            rows.append(row)
        return rows


    def fetch_data(self):
        """Fetch the data from the source."""
        self.data = self.parse_xml(self.source)
