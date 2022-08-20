from urllib.request import urlopen
import pandas as pd
import numpy as np
from sdg.Indicator import Indicator
from sdg.Loggable import Loggable
from sdg import helpers

class InputBase(Loggable):
    """Base class for sources of SDG data/metadata.

    logging: None or list
        Type of logs to print, including 'warn' and 'debug'.
    request_params : dict or None
        Optional dict of parameters to be passed to remote file fetches.
        Corresponds to the options passed to a urllib.request.Request.
        @see https://docs.python.org/3/library/urllib.request.html#urllib.request.Request
    column_map: string
        Remote URL of CSV column mapping or path to local CSV column mapping file
    code_map: string
        Remote URL of CSV code mapping or path to local CSV code mapping file
    meta_suffix: string
        String to add to each metadata key. Intended usage is to allow identical
        sets of metadata - one for global and one for national.
    """

    def __init__(self, logging=None, column_map=None, code_map=None, request_params=None,
                 meta_suffix=None):
        """Constructor for InputBase."""
        Loggable.__init__(self, logging=logging)
        self.request_params = request_params
        self.indicators = {}
        self.data_alterations = []
        self.meta_alterations = []
        self.last_executed_indicator_options = None
        self.merged_indicators = None
        self.previously_merged_inputs = []
        self.num_previously_merged_inputs = 0
        self.column_map = column_map
        self.code_map = code_map
        self.meta_suffix = meta_suffix


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
        for col in df.columns:
            for to_find in [None, "", "nan"]:
                try:
                    df[col].replace(to_replace={ to_find: np.NaN }, inplace=True)
                except Exception as e:
                    pass
        return df


    def fetch_file(self, location):
        return helpers.files.read_file(location, request_params=self.request_params)


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
        data = self.alter_data(data, indicator_id=indicator_id)
        meta = self.alter_meta(meta, indicator_id=indicator_id)
        indicator = Indicator(indicator_id, name=name, data=data, meta=meta, options=options, logging=self.logging)
        self.indicators[indicator_id] = indicator


    def alter_data(self, data, indicator_id=None):
        """Perform any alterations on some data.

        Parameters
        ---------
        data : DataFrame or None
        indicator_id : String or None
        """
        # If empty or None, do nothing.
        if data is None or not isinstance(data, pd.DataFrame) or data.empty:
            return data
        # Apply any mappings.
        data = self.apply_column_map(data)
        data = self.apply_code_map(data)
        # Perform any alterations on the data.
        for alteration in self.data_alterations:
            try:
                data = alteration(data, {
                    'indicator_id': indicator_id,
                })
            except:
                # Handle callbacks without the context parameter.
                data = alteration(data)
        if data is None:
            raise Exception('Data alteration functions should return the altered dataframe.')

        # Always do these hardcoded steps.
        data = self.fix_dataframe_columns(data)
        data = self.fix_empty_values(data)

        return data


    def alter_meta(self, meta, indicator_id=None):
        """Perform any alterations on some metadata.

        Parameters
        ---------
        meta : dict or None
        indicator_id : String or None
        """
        if not meta or meta is None:
            if len(self.meta_alterations) > 0:
                meta = {}
            else:
                return meta
        for alteration in self.meta_alterations:
            try:
                meta = alteration(meta, {
                    'indicator_id': indicator_id,
                })
            except:
                # Handle callbacks without the context parameter.
                meta = alteration(meta)
        if meta is None:
            raise Exception('Metadata alteration functions should return the altered dict.')

        if self.meta_suffix is not None:
            for key in list(meta.keys()):
                if not key.endswith(self.meta_suffix):
                    meta[key + self.meta_suffix] = meta[key]
                    del meta[key]
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


    def apply_column_map(self, data):
        if self.column_map is not None:
            column_map=pd.read_csv(self.column_map)
            column_dict = dict(zip(column_map['Text'], column_map['Value']))
            data.rename(columns=column_dict, inplace=True)
        return data


    def apply_code_map(self, data):
        if self.code_map is not None:
            code_map=pd.read_csv(self.code_map)
            code_dict = {}
            for _, row in code_map.iterrows():
                if row['Dimension'] not in code_dict:
                    code_dict[row['Dimension']] = {}
                code_dict[row['Dimension']][row['Text']] = row['Value']
            try:
                data.replace(to_replace=code_dict, value=None, inplace=True)
            except:
                data.replace(to_replace=code_dict, inplace=True)
        return data
