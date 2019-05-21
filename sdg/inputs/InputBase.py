class InputBase:
    """Base class for sources of SDG data/metadata."""

    def __init__(self):
        """Constructor for InputBase."""
        self.indicators = {}


    def execute(self):
        """Fetch all data/metadata from source, fetching a list of indicators."""
        raise NotImplementedError


    def get_row(self, year, value, disaggregations):
        """Return a dict for placing a row in a dataframe.

        Parameters
        ----------
        year : number
            The year for this row
        value : number
            The metric/value for this row
        disaggregations : dict
            A dict of categories keyed to variations

        Returns
        -------
        dict
            A dict for a row to be added to a dataframe.
        """

        row = {}
        row['Year'] = year
        for disaggregation in disaggregations:
            row[disaggregation] = disaggregations[disaggregation]
        row['Value'] = value
        return row


    def fix_dataframe_columns(self, df):
        """Ensure that the columns of a dataframe match the requirements.

        Parameters
        ----------
        df : Dataframe
            The Pandas dataframe to fix

        Returns
        -------
        Dataframe
            The same dataframe with rearranged columns
        """

        cols = df.columns.tolist()
        cols.pop(cols.index('Year'))
        cols.pop(cols.index('Value'))
        cols = ['Year'] + cols + ['Value']
        return df[cols]
