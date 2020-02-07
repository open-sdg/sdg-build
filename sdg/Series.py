import pandas as pd

class Series:
    """Data model for series within SDG indicators."""

    def __init__(self, disaggregations, values={}):
        """Constructor for the SDG series instances.

        Parameters
        ----------
        disaggregations : dict
            A dict describing the disaggregations contained in the series.
        values : dict
            A dict containing the year/value pairs for the series.
        """
        self.disaggregations = disaggregations
        self.values = values


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

    def add_value(self, year, value):
        """Add a new yearly value.

        Parameters
        ----------
        year : numeric
            The numerical year to add.
        value : numeric
            The numerical value to add.
        """
        self.values[year] = value

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
