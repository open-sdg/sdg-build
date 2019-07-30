import pandas as pd
import sdg
import requests
from sdg.inputs import InputSdmxMl_Structure

class InputSdmxMl_StructureSpecific(InputSdmxMl_Structure):
    """Sources of SDG data that are SDMX-ML format.

    Specifically this supports Version 2.1 of SDMX-ML "Structure Specific"
    format, also known as Compact format.
    """


    def get_series_id(self, series):
        """Get the id for a Series.

        Parameters
        ----------
        series : Element
            The XML element for the Series
        """
        return series.attrib['SERIES']


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
        # The dimension consist of the attributes of the Series element.
        dimensions = series.attrib
        # We want to make sure we got the unit of measure. If it was not in the
        # series attributes, check the first observation.
        if 'UNIT_MEASURE' not in dimensions:
            observations = self.get_observations(series)
            if 'UNIT_MEASURE' in observations[0].attrib:
                dimensions['UNIT_MEASURE'] = observations[0].attrib['UNIT_MEASURE']

        return dimensions


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
            year = observation.attrib['TIME_PERIOD']
            value = observation.attrib['OBS_VALUE']
            row = self.get_row(year, value, disaggregations)
            rows.append(row)
        return rows
