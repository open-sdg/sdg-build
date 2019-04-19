import sdg

class Indicator:
    """Data model for SDG indicators."""

    def __init__(self, inid, data=None, meta=None):
        """Constructor for the SDG indicator instances.

        Keyword arguments:
        inid -- The three-part dash-delimited ID (eg, 1-1-1).
        data -- Dataframe of all data.
        meta -- Dict of fielded metadata.
        """
        self.inid = inid
        self.data = data
        self.meta = meta
        self.set_headline()
        self.set_edges()

    def has_data(self):
        """Check to see if this indicator has data."""
        return False if self.data is None else True

    def set_data(self, val):
        """Set the indicator data if a value is passed."""
        if val:
            self.data = val
            self.set_headline()
            self.set_edges()

    def set_meta(self, val):
        """Set the indicator metadata if a value is passed."""
        if val:
            self.meta = val

    def set_headline(self):
        self.headline = sdg.data.filter_headline(self.data) if self.has_data() else None

    def set_edges(self):
        self.edges = sdg.edges.edge_detection(self.inid, self.data) if self.has_data() else None

    def get_goal(self):
        return self.inid.split('.')[0]

    def require_meta(self):
        """Ensure that the metadata for this indicator has the minimum required fields."""
        required = {
            "reporting_status": "notstarted",
            "sdg_goal": self.get_goal()
        }
        if self.meta is None:
            self.meta = required
        else:
            for key in required:
                self.meta[key] = required[key]