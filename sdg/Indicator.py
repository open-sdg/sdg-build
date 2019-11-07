import sdg
import pandas as pd
from sdg.translations import TranslationHelper

class Indicator:
    """Data model for SDG indicators."""

    def __init__(self, inid, name=None, data=None, meta=None):
        """Constructor for the SDG indicator instances.

        Parameters
        ----------
        inid : string
            The three-part dash-delimited ID (eg, 1-1-1).
        name : string
            The name of the indicator.
        data : Dataframe
            Dataframe of all data, with at least "Year" and "Value" columns.
        meta : dict
            Dict of fielded metadata.
        """
        self.inid = inid
        self.name = name
        self.data = data
        self.meta = meta
        self.set_headline()
        self.set_edges()


    def has_name(self):
        """Check to see if the indicator has a name.

        Returns
        -------
        boolean
            True if the indicator has a name.
        """
        return self.name is not None


    def get_name(self):
        """Get the name of the indicator if known, or otherwise the id.

        Returns
        -------
        string
            The name (or id) of the indicator.
        """
        return self.name if self.name is not None else self.inid


    def set_name(self, name=None):
        """Set the name of the indicator."""
        if name is not None:
            self.name = name


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
        # If empty or None, do nothing.
        if val is None or not isinstance(val, pd.DataFrame) or val.empty:
            return

        self.data = val
        self.set_headline()
        self.set_edges()


    def set_meta(self, val):
        """Set the indicator metadata if a value is passed.

        Parameters
        ----------
        val : Dict or None
        """
        if val is not None and val:
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
            df = pd.DataFrame({'Year':[], 'Value':[]})
            # Enforce the order of columns.
            cols = ['Year', 'Value']
            df = df[cols]
            self.data = df


    def translate(self, language, translation_helper):
        """Translate the entire indicator into a particular language.

        Parameters
        ----------
        language : string
            The language code to translate into.
        translation_helper : TranslationHelper
            The instance of TranslationHelper to perform the translations.
        """
        # Callback function for translating some metadata.
        def translate_meta(text):
            return translation_helper.translate(text, language)
        def translate_data(text):
            # Here we use a "default group" of "data". This is for backwards-
            # compatibility reasons specific to Open SDG. This may need to be
            # configurable if it is kept at all.
            return translation_helper.translate(text, language, 'data')
        # Translate the name.
        self.name = translate_meta(self.name)
        # Translate the metadata.
        for key in self.meta:
            self.meta[key] = translate_meta(self.meta[key])
        # Translate the data cells.
        for column in self.data:
            self.data[column] = self.data[column].apply(translate_data)
        # Translate the data column headers.
        self.data.rename(mapper=translate_meta, axis='columns', inplace=True)
        # Translate the edges.
        for column in self.edges:
            self.edges[column] = self.edges[column].apply(translate_data)
