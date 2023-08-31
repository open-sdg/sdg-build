import pandas as pd
from sdg.Loggable import Loggable

class Series(Loggable):
    """Data model for series within SDG indicators.

    Indicator data can have multiple combinations of disaggregations, which are
    here called "series". For our purposes, a "series" is a full set of available
    years (for example, 2008, 2009, and 2010) with the corresponding values (for
    example, 0.7, 0.8, and 0.9) and a description of how it is disaggregated
    (for example, Female, Age 60+, Urban).

    Each series contains 'disaggregations' and 'values'. For example a series
    'disaggregations might look like this:
        {
            'Sex': 'Female',
            'Age': '60+',
            'Area': 'Urban'
        }
    And a series values might look like this:
        {
            2008: 0.7,
            2009: 0.8,
            2010: 0.9
        }
    """

    def __init__(self, disaggregations, indicator_id='Indicator', logging=None):
        """Constructor for the SDG series instances.

        Parameters
        ----------
        disaggregations : dict
            A dict describing the disaggregations contained in the series.
        indicator_id : string
            Optional indicator ID this series is a part of (eg, 1.1.1).
        """
        Loggable.__init__(self, logging=logging)
        self.disaggregations = disaggregations
        self.values = {}
        self.observation_attributes = {}
        self.indicator_id = indicator_id


    def get_disaggregations(self):
        """Get the disaggregations for this series.

        Returns
        -------
        dict
            A dict of key/value pairs describing the disaggregation.
        """
        return self.disaggregations

    def get_values(self):
        """Get the values for this series.

        Returns
        -------
        dict
            A dict of year/value pairs describing the data per year.
        """
        return self.values

    def get_observation_attributes(self):
        """Get the observation_attributes for this series.

        Returns
        -------
        dict
            A dict of year/attribute pairs describing the attributes per year.
        """
        return self.observation_attributes

    def add_value(self, year, value):
        """Add a new yearly value.

        Parameters
        ----------
        year : numeric
            The numerical year to add.
        value : numeric
            The numerical value to add.
        """
        if year in self.values:
            self.warn('{inid} - Duplicate values for year {year}: {value1} and {value2} in series: {series}',
                       inid=self.indicator_id, year=year, value1=value,
                       value2=self.values[year], series=self.get_disaggregations())
        else:
            self.values[year] = value

    def add_observation_attribute(self, year, attribute, value):
        """Add a new yearly observation attriute.

        Parameters
        ----------
        year : numeric
            The numerical year to add.
        attribute : string
            The name of the attribute.
        value : string
            The value of the attribute.
        """
        if year not in self.observation_attributes:
            self.observation_attributes[year] = {}
        self.observation_attributes[year][attribute] = value

    def has_disaggregation(self, disaggregation):
        """Check to see if the series has a specific disaggregation.

        Parameters
        ----------
        disaggregation : string
            The key of the disaggregation you're looking for.

        Returns
        -------
        boolean
            True if the disaggregation has a value, False otherwise.
        """
        if disaggregation not in self.disaggregations:
            return False
        if pd.isna(self.disaggregations[disaggregation]):
            return False
        return True

    def get_disaggregation(self, disaggregation):
        """Get the value of a specific disaggregation.

        Parameters
        ----------
        disaggregation : string
            The key of the disaggregation you're looking for.

        Returns
        -------
        string or None
            The value of that disaggregation, or None if not found.
        """
        if self.has_disaggregation(disaggregation):
            return self.disaggregations[disaggregation]
        else:
            return None
