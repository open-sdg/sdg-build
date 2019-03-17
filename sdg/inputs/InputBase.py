class InputBase:
    """Base class for sources of SDG data/metadata."""

    def fetch(self):
        """Fetch all data/metadata from source, returning a list of indicators."""
        raise NotImplementedError
