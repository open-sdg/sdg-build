class Indicator:
    """Data model for SDG indicators."""

    def __init__(self, inid, data=None, meta=None, headline=None, edges=None):
        """Constructor for the SDG indicator instances.

        Keyword arguments:
        inid -- The three-part dash-delimited ID (eg, 1-1-1).
        data -- Dataframe of all data.
        meta -- Dict of fielded metadata.
        headline -- Dataframe of headline data.
        edges -- Dataframe of data edges.
        """
        self.inid = inid
        self.data = data
        self.meta = meta
        self.headline = headline
        self.edges = edges

    def set_data(self, val):
        """Set the indicator data if a value is passed."""
        if val:
            self.data = val

    def set_meta(self, val):
        """Set the indicator metadata if a value is passed."""
        if val:
            self.meta = val

    def set_headline(self, val):
        """Set the indicator headline if a value is passed."""
        if val:
            self.headline = val

    def set_edges(self, val):
        """Set the indicator edges if a value is passed."""
        if val:
            self.edges = val