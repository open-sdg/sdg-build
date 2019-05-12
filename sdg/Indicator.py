import sdg
import pandas as pd

class Indicator:
    """Data model for SDG indicators."""

    def __init__(self, inid, data=None, meta=None):
        """Constructor for the SDG indicator instances.

        Parameters
        ----------
        inid : string
            The three-part dash-delimited ID (eg, 1-1-1).
        data : Dataframe
            Dataframe of all data, with at least "Year" and "Value" columns.
        meta : dict
            Dict of fielded metadata.
        """
        self.inid = inid
        self.data = data
        self.meta = meta
        self.set_headline()
        self.set_edges()


    def has_data(self):
        """Check to see if this indicator has data.

        Returns
        -------
        boolean
            True if the indicator has data.
        """
        if self.data is None:
            # If data has not been set yet, return False.
            return False
        # Otherwise return False if there are no rows in the dataframe.
        return False if len(self.data) < 1 else True


    def has_meta(self):
        """Check to see if this indicator has metadata.

        Returns
        -------
        boolean
            True if the indicator has metadata.
        """
        return False if self.meta is None else True


    def set_data(self, val):
        """Set the indicator data if a value is passed.

        Parameters
        ----------
        val : Dataframe or None
        """
        if val is not None:
            self.data = val
            self.set_headline()
            self.set_edges()


    def set_meta(self, val):
        """Set the indicator metadata if a value is passed.

        Parameters
        ----------
        val : Dict or None
        """
        if val is not None:
            self.meta = val


    def set_headline(self):
        """Calculate and set the headline for this indicator."""
        self.require_data()
        self.headline = sdg.data.filter_headline(self.data)


    def set_edges(self):
        """Calculate and set the edges for this indicator."""
        self.require_data()
        self.edges = sdg.edges.edge_detection(self.inid, self.data)


    def get_goal_id(self):
        """Get the goal number for this indicator.

        Returns
        -------
        string
            The number of the goal.
        """
        return self.inid.split('-')[0]


    def get_target_id(self):
        """Get the target id for this indicator.

        Returns
        -------
        string
            The target id, dot-delimited.
        """
        return '.'.join(self.inid.split('-')[0:2])


    def get_indicator_id(self):
        """Get the indicator id for this indicator (dot-delimited version).

        Returns
        -------
        string
            The indicator id, dot-delimited.
        """
        return self.inid.replace('-', '.')


    def require_meta(self, minimum_metadata={}):
        """Ensure the metadata for this indicator has minimum necessary values.

        Parameters
        ----------
        minimum_metadata : Dict
            Key/value pairs of minimum metadata for this indicator.
        """
        if self.meta is None:
            self.meta = minimum_metadata
        else:
            for key in minimum_metadata:
                if key not in self.meta:
                    self.meta[key] = minimum_metadata[key]


    def require_data(self):
        """Ensure at least an empty dataset for this indicator."""
        if self.data is None:
            self.data = pd.DataFrame({'Year':[], 'Value':[]})
