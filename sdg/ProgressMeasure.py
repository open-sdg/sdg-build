from sdg import Loggable

class IndicatorProgress(Loggable):
    def __init__(self, indicator, logging=None, cache_store=None):

        Loggable.__init__(self, logging=logging)
        self.indicator = indicator
        self.inid = indicator.inid
        self.data = indicator.data
        self.meta = indicator.meta
        self.cache_store = cache_store
        # self.indicator_options = indicator.options

        # self.auto_progress_calculation = self.meta.get('auto_progress_calculation') is True
        # self.progress_calculation_options = self.get_progress_calculation_options()

        self.cols = self.data.columns
        self.series_column = self.indicator.options.series_column
        self.unit_column = self.indicator.options.unit_column
        self.progress_column = self.indicator.options.progress_column
        self.non_disaggregation_columns = self.indicator.options.non_disaggregation_columns

    def get_progress_calculation_options(self):
        """
        Get progress calculation options from the indicator metadata.
        If progress calculation options are not specified in the metadata, 
        return the default progress calculation options instead.
        """
        if self.meta is not None:
            progress_calc_opts = self.meta.get('progress_calculation_options')
            # progress_calc_opts is a list of dictionaries
            # each dictionary corresponds to the options for one series/unit/disaggregation
            if progress_calc_opts:
                return [config_defaults(config) for config in progress_calc_opts]
            else:
                return [default_progress_calc_options()]

    def get_indicator_progress(self):
        """
        Read the progress calculation configurations from the indicator metadata and return the progress 
        measure score and status for the indicator. The minimum progress score and associated progress 
        status are taken as the aggregate score for the indicator when multiple series, units, and/or 
        disaggregations are specified in the progress calculation configurations.
        When the progress calculation is turned off, any manually specified progress status found in the 
        metadata is returned alongside a score of None.
        If the progress calculation is turned off and no progress status is found, it will return a score 
        of None and 'not_available' as the progress status.

        Returns:
            tuple: (score, status)
        """
        # Check if progress calculation is turned on
        if self.meta.get('auto_progress_calculation') is True:
            # First try to use caching.
            if self.cache_store is not None and self.inid in self.cache_store:
                # self.debug(f'{self.inid} progress from cache')
                return self.cache_store[self.inid]
            # Get the progress measure score and status for each series/unit/disaggregation specified in the progress calculation options.
            progress_outputs = []
            for config in self.get_progress_calculation_options():
                pm = SeriesProgress(self.indicator, config, logging=self.logging)
                score = pm.score
                # discard progress outputs when score is None
                if score is not None:
                    # append a tuple of (score, status) for each specified series/unit/disaggregation
                    progress_outputs.append((score, pm.status))

            if progress_outputs:
                # Cache/return a tuple of the minimum score and associated progress status
                results = min(progress_outputs, key=lambda x: x[0])
                if self.cache_store is None:
                    self.cache_store = {self.inid: results}
                else:
                    self.cache_store[self.inid] = results
                return results
        else:
            # Use any progress status available in the metadata as a manual override
            if 'progress_status' in self.meta.keys():
                return (None, self.meta['progress_status'])
                
        return (None, "not_available")

    def get_indicator_score(self):
        """
        Get the indicator's progress score.
        """
        return self.get_indicator_progress()[0]


    def get_indicator_status(self):
        """
        Get the indicator's progress status.
        """
        return self.get_indicator_progress()[1]


class SeriesProgress(IndicatorProgress):
    # inherit the indicator-level attributes and methods
    def __init__(self, indicator, config={}, logging=None):

        self.config = config_defaults(config)

        IndicatorProgress.__init__(self, indicator, logging=logging)

        # Filter data and update the config with key values for the progress calculation
        self.data = self.filter_data()
        self.config = self.update_config()

        self.base_year = self.config.get('base_year')
        self.base_value = self.config.get('base_value')
        self.current_year = self.config.get('current_year')
        self.current_value = self.config.get('current_value')
        self.target_year = self.config.get('target_year')
        self.target = self.config.get('target')
        self.direction = -1 if self.config.get('direction') == 'negative' else 1
        self.sign = -1 if self.base_value < 0 else 1 # note: base_value = 0 is invalid, would get zero division error in growth calculation
        
        self.method = 1 if self.target is None else 2 # method is 1 for qualitative or 2 for quantitative
        self.progress_thresholds = self.get_progress_thresholds() # may not want to allow user to configure progress thresholds
        
        self.target_achieved = self.is_target_achieved()
        self.progress_value = self.calculate_progress_value()
        self.status = get_progress_status(self.progress_value, self.progress_thresholds, self.target_achieved)
        self.score = self.get_score()

    def update_config(self):
        # get years that exist in the data
        years = self.data["Year"]
    
        # set current year to be the most recent year that exists in data
        self.config['current_year'] = years.max()
        self.config['current_value'] = self.data.Value[self.data.Year == self.config['current_year']].item() # GET ERROR HERE IF DISAGGREGATION SELECTION NOT SUFFICIENTLY REDUCED
    
        # check if the base year input exists in the data
        if self.config['base_year'] not in years.values:
            # if the base year is not in the available data, assign it to be the next available year
            self.config['base_year'] = years[years > self.config['base_year']].min()
        # Set the base value
        self.config['base_value'] = self.data.Value[self.data.Year == self.config['base_year']].item()

        return self.config
    
    def filter_data(self):
        data = self.data
        # check if the year value contains more than 4 digits (indicating a range of years)
        if (data['Year'].astype(str).str.len() > 4).any():
            # take the first year in the range
            data['Year'] = data['Year'].astype(str).str.slice(0, 4).astype(int)

        if len(self.cols) > 2:
            # Data has disaggregation columns. Find the appropriate subset of data for progress calculation
            # If units and/or series columns exist, keep only the user selected unit/series
            if (self.unit_column in self.cols) and ('unit' in self.config.keys()):
                data = data.loc[data[self.unit_column] == self.config['unit']]
            if (self.series_column in self.cols) and ('series' in self.config.keys()):
                data = data.loc[data[self.series_column] == self.config['series']]
            # If disaggregation specified by user, reduce the dataframe to only include the selected disaggregation
            disaggregations = self.config.get('disaggregation')
            if disaggregations:
                for disagg in disaggregations:
                    data = data.loc[data[disagg['field']] == disagg['value']]
            # Otherwise, find headline data (rows where values in all disaggregation dimensions are NA)
            else:
                data = data[data.loc[:, ~self.cols.isin(self.non_disaggregation_columns)].isna().all('columns')]

            if self.progress_column in self.cols:
                # Replace values with those from the progress column, then drop progress column
                data = data.assign(Value=data[self.progress_column])
                # data['Value'] = data[self.progress_column]
                # data.drop(self.progress_column, axis=1, inplace=True)
            # Keep only Year and Value columns
            data = data[['Year', 'Value']]

            # To do: 
            # What if no unit/series is selected by user but series/units column(s) exist? --> Warn user and return not_available progress status
            # Fix: Warn user when data not sufficiently reduced by settings. There can be multiple values for the same year, so return not_available progress status

        # remove any NA values from data
        data = data[data["Value"].notna()]
        # cast values to float
        data["Value"] = data["Value"].astype('float')

        # returns None if no rows in data
        if data.shape[0] < 1:
            return None

        return data
    
    def calculate_progress_value(self):
        """Sets up all needed parameters and data for progress calculation, determines methodology for calculation,
        and returns progress value as an output.

        Returns:
            output: float. A value indicating the progress measurement value for the indicator.
        """
        # Run checks on config settings before calculating progress.
        if self.data is None:
            self.warn(f'{self.inid}: No data found for progress calculation')
            return None
        if not all_rows_unique(self.data):
            self.warn(f'{self.inid}: Duplicate rows detected in data selected for progress calculation: {self.config}')
            return None            
        if self.base_value == 0:
            self.warn(f'{self.inid}: Base value is zero (invalid)')
            return None
        # return None if the base year input is in the future of the most recently available data
        if self.base_year > self.current_year:
            self.warn(f'{self.inid}: Base year is greater than the most recent available data: {self.config}')
            return None
        if self.current_year - self.base_year < 1:
            self.warn(f'{self.inid}: Not enough data to calculate progress (must have at least 2 data points): {self.config}')
            return None
    
        if self.method == 1:
            # do progress calculation according to methodology for qualitative target
            output = self.methodology_1()
        else:
            # do progress calculation according to methodology for quantitative target
            output = self.methodology_2()
    
        return output

    def methodology_1(self):
        """Calculate growth using progress measurement methodology 1 (no target value).
    
        Returns:
            float: Progress value.
        """      
        # calculate growth
        return self.sign * self.direction * growth_calculation(self.current_value, self.base_value, self.current_year, self.base_year)


    def methodology_2(self):
        """Calculate growth using progress measurement methodology 2 (given target value).
    
        Check if target has already been achieved.
        Use configuration options to get the current and base value from indicator data and use to calculate growth ratio.

        Returns:
            float: Progress value.
        """
        # calculate observed growth
        cagr_o = growth_calculation(self.current_value, self.base_value, self.current_year, self.base_year)
        # calculate theoretical growth
        cagr_r = growth_calculation(self.target, self.base_value, self.target_year, self.base_year)
        
        return self.sign * self.direction * cagr_o / abs(cagr_r)
            
    def is_target_achieved(self):
        if self.target is not None:
            if (self.direction == -1 and self.current_value <= self.target) or (self.direction == 1 and self.current_value >= self.target):
                return True
        return False
        
    def get_score(self):

        if self.progress_value is None:
            return None
        
        if self.target_achieved:
            return 5
        
        high = self.progress_thresholds['high']
        med = self.progress_thresholds['med']
        low = self.progress_thresholds['low']

        if self.method == 1:
            # Normalize progress values based on progress thresholds
            coeff = self.progress_thresholds.get('coefficient', 1) # coeff value defaults to 1 if not available
            reduced_progress = self.progress_value/coeff
            if reduced_progress >= high:
                return min(500*reduced_progress-5, 5)
            if reduced_progress >= med:
                return 250*reduced_progress-1.25
            if reduced_progress >= low:
                return 500*reduced_progress-2.5
            if reduced_progress < low:
                return max(125*reduced_progress-2.5, -5)
        else: # method == 2
            if self.progress_value >= high:
                return min((7.1429 * self.progress_value) - 4.2857, 5)
            if self.progress_value >= med:
                return min((7.1429 * self.progress_value) - 4.2857, 5)
            if self.progress_value >= low:
                return max((4.1667 * self.progress_value) - 2.5, -5)
            if self.progress_value < low:
                return max((4.1667 * self.progress_value) - 2.5, -5)

    def get_progress_thresholds(self):
        """Checks for configured progress thresholds and updates default thresholds based on methodology.
        Returns:
            progress_thresholds: dict. Dictionary of progress thresholds: {'high': x, 'med': y, 'low': z}
        """      
        # Get the user configured progress thresholds from the metadata.
        user_thresholds = self.config.get('progress_thresholds')

        # Begin with the default progress thresholds for each method and update these with user configured thresholds, if present.
        if self.method == 1:
            # Qualitative method thresholds
            progress_thresholds = {'high': 0.015, 'med': 0.005, 'low': 0}
            progress_thresholds.update(user_thresholds)

            # Reduce thresholds when near limit
            limit = self.config.get('limit')
            if limit is not None:
                base_value = abs(self.base_value)
                limit = abs(limit)
                a = 4.44
                if base_value <= limit:
                    coeff = 1 - (base_value/limit)**a
                elif base_value <= 2*limit:
                    coeff = 1 - ((2*limit - base_value)/limit)**a
                else:
                    coeff = 1
            
                for key in ['high', 'med', 'low']:
                    progress_thresholds[key] *= coeff
                progress_thresholds['coefficient'] = coeff
                
        elif self.method == 2:
            # Quantitative method thresholds
            progress_thresholds = {'high': 0.95, 'med': 0.6, 'low': 0}
            progress_thresholds.update(user_thresholds)

        return progress_thresholds


def config_defaults(config={}):
    """Set progress calculation defaults and update them if any user inputs exist.
    Args:
        config: dict. Indicator configurations passed as a dictionary.
    Returns:
        dict: Dictionary of updated configurations.
    """

    # set default options for progress measurement
    defaults = default_progress_calc_options()
    # update the defaults with any user configured inputs
    defaults.update(config)

    # if target is 0, set to 0.001 (avoids dividing by 0 in calculation)
    if defaults['target'] == 0:
        defaults['target'] = 0.001

    return defaults

def default_progress_calc_options():
    """Provide default inputs for calculating progress."""
    return (
        {
            'base_year': 2015,
            'target_year': 2030,
            'direction': 'negative',
            'target': None,
            'progress_thresholds': {}
        }
    )

def all_rows_unique(df, ignore_columns=['Value', 'Progress']):
    """
    Check dataframe for duplicate rows. Ignores data columns (value and progress columns).
    Returns True if the check succeeded (no duplicate rows found) or False if the check failed (duplicate rows found).

    Args:
        df: dataframe
        ignore_columns: list. List of column names to ignore while checking row uniqueness.
    Returns:
        bool: True if uniqueness check is successful, otherwise False
    """
    cols = [col for col in df.columns if col not in ignore_columns]
    
    success = False
    if not df.duplicated(subset=cols).any():
        success = True

    return success

def growth_calculation(val1, val2, t1, t2):
    """Calculate compound annual growth rate with required arguments.

    Args:
        val1: float. Current value.
        val2: float. Value from base year.
        t1: float. Current year.
        t2: float. Base year.
    Returns:
        float: Compound annual growth rate value.
    """

    return ((val1 / val2) ** (1 / (t1 - t2))) - 1

def get_progress_status(value, thresholds, target_achieved=False):
    """Compare progress value to progress thresholds and return progress status.

    Args:
        value: float. Calculated value of either observed growth or growth ratio for an indicator.
        thresholds: dict. Thresholds for high, medium, and low progress. format: {'high': x, 'med': y, 'low': z}
        target_achieved: bool. If target is achieved, skip comparison with thresholds and return "target_achieved".
    Returns:
        str: Progress status label.
    """

    x = float(thresholds['high'])
    y = float(thresholds['med'])
    z = float(thresholds['low'])

    # compare growth rate to progress thresholds to return progress measure
    if target_achieved:
        return "target_achieved"
    
    if value is not None:
        if value >= x:
            return "substantial_progress"
        elif y <= value < x:
            return "moderate_progress"
        elif z <= value < y:
            return "limited_progress"
        elif value < z:
            return "deterioration"

    return "not_available"