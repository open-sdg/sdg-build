from urllib.request import urlopen
import pandas as pd
import numpy as np
from sdg.Indicator import Indicator
from sdg.Loggable import Loggable

class InputBase(Loggable):
    """Base class for sources of SDG data/metadata."""

    def __init__(self, logging=None, column_map=None, code_map=None):
        """Constructor for InputBase."""
        Loggable.__init__(self, logging=logging)
        self.indicators = {}
        self.data_alterations = []
        self.meta_alterations = []
        self.last_executed_indicator_options = None
        self.merged_indicators = None
        self.previously_merged_inputs = []
        self.num_previously_merged_inputs = 0
        self.column_map = column_map
        self.code_map = code_map


    def execute_once(self, indicator_options):
        # To avoid unnecessarily executing the same input multiple times,
        # track the indicator options and skip execution if they did not
        # change from the last time.
        if self.last_executed_indicator_options is not None:
            if indicator_options == self.last_executed_indicator_options:
                return
        self.last_executed_indicator_options = indicator_options
        self.execute(indicator_options)


    def execute(self, indicator_options):
        self.debug('Starting input: {class_name}')


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
        for col in cols:
            df[col] = df[col].map(str, na_action='ignore')
        cols = ['Year'] + cols + ['Value']
        return df[cols]

    def fix_empty_values(self, df):
        """Ensure that empty values are np.NaN rather than None or "".

        Parameters
        ----------
        df : Dataframe
            The Pandas dataframe to fix

        Returns
        -------
        Dataframe
            The same dataframe with rearranged columns
        """
        return df.replace([None, "", "nan"], np.NaN)


    def fetch_file(self, location):
        """Fetch a file, either on disk, or on the Internet.

        Parameters
        ----------
        location : String
            Either an http address, or a path on disk
        """
        file = None
        data = None
        if location.startswith('http'):
            file = urlopen(location)
            data = file.read().decode('utf-8')
        else:
            file = open(location)
            data = file.read()
        file.close()
        return data


    def normalize_indicator_id(self, indicator_id):
        """Normalize an indicator id (1-1-1, 1-2-1, etc).

        Parameters
        ----------
        indicator_id : string
            The raw indicator ID
        """
        # If there are multiple words, assume the first word is the id.
        words = indicator_id.split(" ")
        indicator_id = words[0]
        # Convert dots to dashes (ie, prefer 1-1-1 to 1.1.1).
        indicator_id = indicator_id.replace('.', '-')
        # Make sure there are no preceding/trailing dashes.
        indicator_id = indicator_id.strip('-')
        return indicator_id


    def normalize_indicator_name(self, indicator_name, indicator_id):
        """Normalize an indicator name.

        Parameters
        ----------
        indicator_name : string
            The raw indicator name
        indicator_id : string
            The indicator id (eg, 1.1.1, 1-1-1, etc.) for this indicator
        """
        # Sometimes the indicator names includes the indicator id, so
        # remove it here. Both dash or dot-delimited.
        dashes = indicator_id.replace('.', '-')
        dots = indicator_id.replace('-', '.')
        indicator_name = indicator_name.replace(dashes, '')
        indicator_name = indicator_name.replace(dots, '')
        # Trim any whitespace.
        return indicator_name.strip()


    def create_dataframe(self, rows):
        """Convert a list of rows into a dataframe.

        Parameters
        ----------
        rows : List
            A list of row dicts

        Returns
        -------
        Dataframe
            The dataframe of rows of data for this indicator.
        """
        df = pd.DataFrame(rows)
        # Enforce position of "Year" and "Value".
        df = self.fix_dataframe_columns(df)
        # Remove empty columns, because they are not necessary.
        df = df.dropna(axis='columns', how='all')
        return df


    def add_indicator(self, indicator_id, name=None, data=None, meta=None, options=None):
        """Add an indicator to this input.

        Parameters
        ----------
        indicator_id : string
            The indicator ID
        name : string or None
            The indicator name
        data : DataFrame or None
            The indicator data
        meta : dict or None
            The indicator metadata
        options : IndicatorOptions or None
            The indicator options
        """
        data = self.alter_data(data)
        meta = self.alter_meta(meta)
        indicator = Indicator(indicator_id, name=name, data=data, meta=meta, options=options, logging=self.logging)
        self.indicators[indicator_id] = indicator


    def alter_data(self, data):
        """Perform any alterations on some data.

        Parameters
        ---------
        data : DataFrame or None
        """
        # If empty or None, do nothing.
        if data is None or not isinstance(data, pd.DataFrame) or data.empty:
            return data
        # Apply any mappings.
        self.apply_column_map()
        self.apply_code_map()
        # Perform any alterations on the data.
        for alteration in self.data_alterations:
            data = alteration(data)
        # Always do these hardcoded steps.
        data = self.fix_dataframe_columns(data)
        data = self.fix_empty_values(data)

        return data


    def alter_meta(self, meta):
        """Perform any alterations on some metadata.

        Parameters
        ---------
        meta : dict or None
        """
        if not meta or meta is None:
            if len(self.meta_alterations) > 0:
                meta = {}
            else:
                return meta
        for alteration in self.meta_alterations:
            meta = alteration(meta)
        return meta


    def add_data_alteration(self, alteration):
        """Add an alteration for data.

        Parameters
        ----------
        alteration : function
            The alteration function.
        """
        self.data_alterations.append(alteration)


    def add_meta_alteration(self, alteration):
        """Add an alteration for meta.

        Parameters
        ----------
        alteration : function
            The alteration function.
        """
        self.meta_alterations.append(alteration)


    def has_merged_indicators(self, inputs):
        """Whether this is the first of a set of already-merged inputs.

        Parameters
        ----------
        inputs : list
            List of InputBase subclasses.


        Returns
        -------
        boolean
            Whether or not this input is the first of a set of already-merged inputs.
        """
        return all([
            self.get_merged_indicators() is not None,
            self == inputs[0],
            self.previously_merged_inputs == inputs,
            self.num_previously_merged_inputs == len(inputs),
        ])


    def get_merged_indicators(self):
        """Return a set of already-merged indicators.

        Returns
        -------
        dict or None
            Dict of Indicator objects keyed by id, if available, else None.
        """
        return self.merged_indicators


    def set_merged_indicators(self, merged_indicators, inputs):
        """Set merged indicators for later retrieval.

        Parameters
        ----------
        merged_indicators : dict
            Dict of Indicator objects keyed by id.
        inputs : list
            List of InputBase subclasses.
        """
        self.merged_indicators = merged_indicators
        self.previously_merged_inputs = inputs
        self.num_previously_merged_inputs = len(inputs)


    def apply_column_map(self):
        if self.column_map is not None:
            column_map=pd.read_csv(self.column_map)
            for col in data.columns:
                if col in column_map['Text'].to_list():
                    try:
                        newcol=column_map['Value'].loc[column_map['Text']==col].iloc[0]
                        data.rename(columns={col:newcol}, inplace=True)
                    except Exception as e:
                        self.warn('Error when mapping data column: ' + col)
                        print(e)


    def apply_code_map(self):
        if self.code_map is not None:
            code_map=pd.read_csv(self.code_map)
            for col in data.columns:
                for i in data.index:
                    try:
                        if data.at[i, col] in code_map['Text'].to_list():
                            data.at[i, col]=code_map['Value'].loc[code_map['Dimension']==col].loc[code_map['Text']==data.at[i, col]].iloc[0]
                    except Exception as e:
                        self.warn('Error when mapping codes for column ' + col)
                        print(e)
