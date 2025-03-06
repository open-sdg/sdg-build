import numpy as np
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
        If the progress calculation is turned off and no progress status is found, it will return a default score 
        of None and 'not_available' as the progress status.

        Returns:
            tuple: (score, status)
        """
        # Initialize the score and progress status with defaults
        indicator_score = None
        indicator_status = 'not_available'

        # Check if progress calculation is turned on
        if self.meta.get('auto_progress_calculation') is True:
            # First try to use caching.
            if self.cache_store is not None and self.inid in self.cache_store:
                # self.debug(f'{self.inid} progress from cache')
                return self.cache_store[self.inid]
            # Get the progress measure score and status for each series/unit/disaggregation specified in the progress calculation options.
            scores = []
            targets = []
            for config in self.get_progress_calculation_options():
                series = SeriesProgress(self.indicator, config, logging=self.logging)
                score = series.score
                if score is not None:
                    scores.append(score)
                    targets.append(series.target_achieved)
            # Update the indicator score and progress status
            if scores:
                indicator_score = np.median(scores)
                target_achieved = all(targets) # True only when targets for all series are achieved
                indicator_status = get_progress_status_from_score(indicator_score, target_achieved)

        else:
            # Use any progress status available in the metadata as a manual override
            if 'progress_status' in self.meta.keys():
                indicator_status = self.meta['progress_status']
                # indicator_score is None

        # Result to return is tuple of indicator score and progress status
        result = (indicator_score, indicator_status)
        
        # Cache the result
        if self.cache_store is None:
            self.cache_store = {self.inid: result}
        else:
            self.cache_store[self.inid] = result

        return result

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

        IndicatorProgress.__init__(self, indicator, logging=logging)
        
        # Initialize series attributes
        self.config = config_defaults(config)
        self.tag = self.get_series_tag()
        self.base_year = None
        self.base_value = None
        self.current_year = None
        self.current_value = None
        self.target_year = None
        self.target = None
        self.direction = None
        self.sign = None
        self.method = None
        self.progress_thresholds = {}
        self.target_achieved = None
        self.progress_value = None
        self.status = 'not_available'
        self.score = None

        # Filter data and update the config with key values for the progress calculation
        self.data = self.filter_data()
        if self.data is None:
            self.warn(f'{self.inid}: No data found for progress calculation of series: {self.tag}')
        else:
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

    def get_series_tag(self):
        tag = {}
        if 'series' in self.config:
            tag[self.series_column] = self.config['series']
        if 'unit' in self.config:
            tag[self.unit_column] = self.config['unit']
        if 'disaggregation' in self.config:
            for disagg in self.config['disaggregation']:
                tag[disagg['field']] = disagg['value']
        return tag
        
    def update_config(self):
        # do nothing if there is no data
        if self.data is None:
            return self.config
        else:
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
    
    def filter_column(self, data, column, field):
        if column in data.columns:
            if any(data[column] == field):
                data = data.loc[data[column] == field]
            else:
                self.warn(f'{self.inid} - Field {field} not found in column {column} for progress calculation of series: {self.tag}')
        else:
            self.warn(f'{self.inid} - Column {column} not found in data for progress calculation of series: {self.tag}')
        return data
    
    def filter_data(self):
        data = self.data
        # check if the year value contains more than 4 digits (indicating a range of years)
        if (data['Year'].astype(str).str.len() > 4).any():
            # take the first year in the range
            data['Year'] = data['Year'].astype(str).str.slice(0, 4).astype(int)

        if len(data.columns) > 2:
            # Data has auxiliary and/or disaggregation columns. Find the appropriate subset of data for progress calculation
            
            # Remove auxiliary information columns (observation attributes and GeoCode), if present
            aux_columns = [col for col in self.indicator.options.get_observation_attributes() if col in data.columns]
            if 'GeoCode' in data.columns:
                aux_columns.append('GeoCode')
            data = data.drop(columns=aux_columns)

            # If progress column is present, replace values with those from the progress column and drop progress column
            if self.progress_column in data.columns:
                data = data.assign(Value=data[self.progress_column])
                data = data.drop(columns=self.progress_column)                
            
            # If units and/or series columns exist, keep only the user selected unit/series
            if self.config.get('unit') is not None:
                data = self.filter_column(data, self.unit_column, self.config['unit'])
            if self.config.get('series') is not None:
                data = self.filter_column(data, self.series_column, self.config['series'])
            # If disaggregation specified by user, reduce the dataframe to only include the selected disaggregation
            disaggregations = self.config.get('disaggregation')
            if disaggregations:
                for disagg in disaggregations:
                    data = self.filter_column(data, disagg['field'], disagg['value'])
            # Otherwise, find headline data (rows where values in all disaggregation dimensions are NA)
            else:
                headline = data[data.loc[:, ~data.columns.isin(self.non_disaggregation_columns)].isna().all('columns')]
                if (len(headline) == 0) and (len(headline) < len(data)):
                    raise Exception(f'{self.inid} - No headline found for progress calculation of series: {self.tag}')
                data = headline
            
            # Check if data was sufficiently reduced to a single series/unit/disaggregation
            grouping_columns = [col for col in data.columns if col not in ['Year', 'Value']]
            for col in grouping_columns:
                unique_groups = data[col].unique()
                if len(unique_groups) > 1:
                    raise Exception(f'{self.inid} - Detected many sub-series ({col}: {unique_groups}) at filter output for progress calculation of series: {self.tag}.')

            # Keep only Year and Value columns
            data = data[['Year', 'Value']]

        # remove any NA values from data
        data = data[data["Value"].notna()]
        # cast values to float
        data["Value"] = data["Value"].astype('float')

        # Raise exception if there are duplicate years in data.
        duped_years = data.loc[data['Year'].duplicated(False)]
        if duped_years.empty is False:
            error_messages = []
            for year, value in duped_years.values:
                error_messages.append(f'{self.inid} - Duplicate value for year {int(year)}: {value} for progress calculation of series: {self.tag}')
            raise Exception('\n'.join(error_messages))

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
            self.warn(f'{self.inid}: No data found for progress calculation of series: {self.tag}')
            return None
        if not all_rows_unique(self.data):
            self.warn(f'{self.inid}: Duplicate rows detected in data selected for progress calculation of series: {self.tag}')
            return None            
        if self.base_value == 0:
            self.warn(f'{self.inid}: Base value is zero (invalid) for series: {self.tag}')
            return None
        # return None if the base year input is in the future of the most recently available data
        if self.base_year > self.current_year:
            self.warn(f'{self.inid}: Base year ({self.base_year}) is greater than the most recent available data ({self.current_year}) for series: {self.tag}')
            return None
        if self.current_year - self.base_year < 1:
            self.warn(f'{self.inid}: Not enough data to calculate progress (must have at least 2 data points) of series: {self.tag}')
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
        # Note: progress_thresholds are already reduced by the reduction coefficient

        if self.method == 1:
            # Normalize progress values based on progress thresholds
            coeff = self.progress_thresholds.get('coefficient', 1) # coeff value defaults to 1 if not available
            reduced_progress = self.progress_value/coeff
            if self.progress_value >= high:
                return min(500*reduced_progress-5, 5)
            if self.progress_value >= med:
                return 250*reduced_progress-1.25
            if self.progress_value >= low:
                return 500*reduced_progress-2.5
            if self.progress_value < low:
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

def get_progress_status_from_score(score, target_achieved=False):
    """Determine the progress status from the score.

    Args:
        score: float. Progress score between -5 and 5.
        target_achieved: bool. If target is achieved, skip comparison with thresholds and return "target_achieved".
    Returns:
        str: Progress status label.
    """

    if target_achieved:
        return "target_achieved"

    if score is None:
        return "not_available"
    elif 2.5 <= score <= 5:
        return "substantial_progress"
    elif 0 <= score < 2.5:
        return "moderate_progress"
    elif -2.5 <= score < 0:
        return "limited_progress"
    elif -5 <= score < -2.5:
        return "deterioration"