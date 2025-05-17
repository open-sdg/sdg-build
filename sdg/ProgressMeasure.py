import numpy as np
from sdg import Loggable

class IndicatorProgress(Loggable):
    """Indicator-level progress class"""
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
        return list with empty dictionary.
        """
        if self.meta is not None:
            progress_calc_opts = self.meta.get('progress_calculation_options')
            # progress_calc_opts is a list of dictionaries
            # each dictionary corresponds to the options for one series/unit/disaggregation
            if progress_calc_opts:
                return progress_calc_opts
            else:
                return [{}]

    def get_indicator_progress(self):
        """
        Read the progress calculation configurations from the indicator metadata and return the progress 
        measure score and status for the indicator. The mean progress score and associated progress 
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
        indicator_status = ''
        series_calculation_components = {}

        # Check if progress calculation is turned on
        if self.meta is not None:
            if self.meta.get('auto_progress_calculation') is True:
                # First try to use caching.
                if self.cache_store is not None and self.inid in self.cache_store:
                    # self.debug(f'{self.inid} progress from cache')
                    return (self.cache_store[self.inid]['score'], self.cache_store[self.inid]['progress_status'])
                # Get the progress measure score and status for each series/unit/disaggregation specified in the progress calculation options.
                scores = []
                targets = []
                for config in self.get_progress_calculation_options():
                    series = SeriesProgress(self.indicator, config, logging=self.logging)
                    score = series.score
                    if score is not None:
                        scores.append(score)
                        targets.append(series.target_achieved)
                    series_calculation_components.update(series.get_progress_calculation_components())
                # Update the indicator score and progress status
                if scores:
                    indicator_score = np.mean(scores)
                    target_achieved = all(targets) # True only when targets for all series are achieved
                    indicator_status = get_progress_status_from_score(indicator_score, target_achieved)
    
            else:
                # Use any progress status available in the metadata as a manual override
                if 'progress_status' in self.meta.keys():
                    indicator_status = self.meta['progress_status']
                    # indicator_score is None

        # Result to return is tuple of indicator score and progress status
        result = (indicator_score, indicator_status)
        
        # Cache the progress calculation components
        indicator_calculation_components = {'progress_status': indicator_status, 'score': floatNone(indicator_score)}
        indicator_calculation_components.update(series_calculation_components)  
        if self.cache_store is None:
            self.cache_store = {self.inid: indicator_calculation_components}
        else:
            self.cache_store[self.inid] = indicator_calculation_components

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
    """Series-level progress class.
    A series refers to a single time series in the indicator data."""
    def __init__(self, indicator, config={}, logging=None):

        # inherit the indicator-level attributes and methods
        IndicatorProgress.__init__(self, indicator, logging=logging)
        
        # Initialize series attributes
        self.series = config.get('series')
        self.unit = config.get('unit')
        self.disaggregation = config.get('disaggregation')
        self.tag = self.get_series_tag()
        # attributes from config
        self.base_year = config.get('base_year', 2015) # defaults to 2015
        self.target = config.get('target') # defaults to None
        if self.target == 0:
            self.warn(f'{self.inid} - Target is zero (invalid) for progress calculation of series: {self.tag}. Calculating progress with target = 0.001 instead.')
            self.target = 0.001
        self.target_year = config.get('target_year', 2030) # defaults to 2030
        self.direction = 1 if config.get('direction') == 'positive' else -1 # defaults to negative (-1)
        self.limit = config.get('limit') # defaults to None
        self.method = 1 if self.target is None else 2 # method is 1 for qualitative or 2 for quantitative
        self.progress_thresholds = config.get('progress_thresholds', {}) # may not want to allow user to configure progress thresholds
        # other attributes
        self.base_value = None
        self.current_year = None
        self.current_value = None
        self.sign = None
        self.target_achieved = False
        self.progress_value = None
        self.status = 'not_available'
        self.score = None

        # Filter data
        self.data = self.filter_data()

        if self.data is None:
            self.warn(f'{self.inid}: No data found for progress calculation of series: {self.tag}')
        else:
            # Lookup and update values for current_year, current_value, base_year, and base_value based on data
            years = self.data['Year']
            # set current year to be the most recent year that exists in data
            self.current_year = years.max()
            self.current_value = self.data.Value[self.data.Year == self.current_year].item()
            # check if the base year input exists in the data
            if self.base_year not in years.values:
                # if the base year is not in the available data, assign it to be the next available year
                self.base_year = years[years > self.base_year].min()
            # Set the base value
            self.base_value = self.data.Value[self.data.Year == self.base_year].item()

            # Update sign and progress_thresholds using updated base_value
            self.sign = -1 if self.base_value < 0 else 1 # note: base_value = 0 is invalid, would get zero division error in growth calculation
            self.progress_thresholds = self.get_progress_thresholds()
            
            # Get final results
            self.target_achieved = self.is_target_achieved()
            self.progress_value = self.calculate_progress_value()
            self.status = get_progress_status(self.progress_value, self.progress_thresholds, self.target_achieved)
            self.score = self.get_score()

    def get_series_tag(self):
        """Return a string that identifies the series for which progress is intended to be calculated.
        """
        tag = [self.inid]
        if self.series is not None:
            tag.append(self.series)
        if self.unit is not None:
            tag.append(self.unit)
        if self.disaggregation is not None:
            for disagg in self.disaggregation:
                tag.append(disagg['value'])
        return ' / '.join(tag)
    
    def filter_column(self, data, column, field):
        """Filter the input dataframe, keeping only rows where the value in 'column' is equal to 'field'.
        """
        if column in data.columns:
            if any(data[column] == field):
                data = data.loc[data[column] == field]
            else:
                self.warn(f'{self.inid} - Field {field} not found in column {column} for progress calculation of series: {self.tag}')
        else:
            self.warn(f'{self.inid} - Column {column} not found in data for progress calculation of series: {self.tag}')
        return data
    
    def filter_data(self):
        """Prepare indicator data and filter it, keeping only the relevant data for calculating the progress of the desired series/unit/disaggregation. 
        Return the filtered dataframe.      
        """
        data = self.data
        # check if the year value contains more than 4 digits (indicating a range of years)
        if (data['Year'].astype(str).str.len() > 4).any():
            # take the first year in the range
            data['Year'] = data['Year'].astype(str).str.slice(0, 4).astype(int)

        if len(data.columns) > 2:
            # Data has auxiliary and/or disaggregation columns. Find the appropriate subset of data for progress calculation
            
            # Drop any columns not relevant to filtering or progress calculation, e.g. non-disaggregation columns, observation attribute columns
            drop_columns = self.non_disaggregation_columns + self.indicator.options.get_observation_attributes()
            # Remove required non-disaggregation columns (Year, Value, Series, Units, Progress) from drop list
            drop_columns = [col for col in drop_columns if col not in ['Year', self.series_column, self.unit_column, self.progress_column, 'Value']]
            # Drop any irrelevant columns present in data
            data = data.drop(columns=drop_columns, errors='ignore')

            # If progress column is present, replace values with those from the progress column and drop progress column
            if self.progress_column in data.columns:
                data = data.assign(Value=data[self.progress_column])
                data = data.drop(columns=self.progress_column)                
            
            # If units and/or series columns exist, keep only the user selected unit/series
            if self.unit is not None:
                data = self.filter_column(data, self.unit_column, self.unit)
            if self.series is not None:
                data = self.filter_column(data, self.series_column, self.series)
            # If disaggregation specified by user, reduce the dataframe to only include the selected disaggregation
            if self.disaggregation:
                for disagg in self.disaggregation:
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
            self.warn(f'{self.inid} - No data found for progress calculation of series: {self.tag}')
            return None
        if not all_rows_unique(self.data):
            self.warn(f'{self.inid} - Duplicate rows detected in data selected for progress calculation of series: {self.tag}')
            return None
        if self.base_value == 0:
            self.warn(f'{self.inid} - Base value is zero (invalid) for progress calculation of series: {self.tag}. Calculating progress with base value = 0.001 instead.')
            self.base_value = 0.001
        if (self.base_value > 0 and self.current_value < 0) or (self.base_value < 0 and self.current_value > 0):
            self.warn(f'{self.inid} - Base value ({self.base_value}) and current value ({self.current_value}) must both be positive or both negative for progress calculation of series: {self.tag}. Consider transforming data values to a valid form in a progress column (see documentation).')
            return None
        # return None if the base year input is in the future of the most recently available data
        if self.base_year > self.current_year:
            self.warn(f'{self.inid} - Base year ({self.base_year}) is greater than the most recent available data ({self.current_year}) for series: {self.tag}')
            return None
        if self.current_year - self.base_year < 1:
            self.warn(f'{self.inid} - Not enough data to calculate progress (must have at least 2 data points) of series: {self.tag}')
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
        """Returns True if the current value achieves the target, False otherwise.
        """
        if self.target is not None:
            if (self.direction == -1 and self.current_value <= self.target) or (self.direction == 1 and self.current_value >= self.target):
                return True
        return False
        
    def get_score(self):
        """Returns the progress score [-5, 5] that corresponds to the calculated progress value for the series.
        If target is achieved, return 5 regardless of calculated progress value.
        """
        if self.target_achieved:
            return 5

        if self.progress_value is None:
            return None
        
        high = self.progress_thresholds['high']
        med = self.progress_thresholds['med']
        low = self.progress_thresholds['low']
        # Note: progress_thresholds are already reduced by the reduction coefficient

        # Score functions hardcoded based on default progress thresholds!
        if self.method == 1: # qualitative target
            coeff = self.progress_thresholds.get('coefficient', 1) # coeff value defaults to 1 if not available
            if self.progress_value < low:
                return max(125*self.progress_value-2.5, -5)
            if coeff == 0: # base value is equal to limit and progress value is >= 0, so limit is maintained or exceeded --> substantial progress
                return 5
            # When making progress in the desired direction, normalize progress value to same basis as reduced threshold
            if self.progress_value >= high:
                return min(500*self.progress_value/coeff-5, 5)
            if self.progress_value >= med:
                return 250*self.progress_value/coeff-1.25
            if self.progress_value >= low:
                return 500*self.progress_value/coeff-2.5
        else: # method == 2, quantitative target
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
        user_thresholds = self.progress_thresholds

        # Begin with the default progress thresholds for each method and update these with user configured thresholds, if present.
        if self.method == 1:
            # Qualitative method thresholds
            progress_thresholds = {'high': 0.015, 'med': 0.005, 'low': 0}
            progress_thresholds.update(user_thresholds)

            # Reduce thresholds when near limit
            if self.limit is not None:
                if (self.base_value < self.limit) and (self.direction == -1):
                    self.warn(f'{self.inid} - Base value ({self.base_value}) is below minimum limit ({self.limit}). Progress calculation may yield unexpected results for series: {self.tag}')
                if (self.base_value > self.limit) and (self.direction == 1):
                    self.warn(f'{self.inid} - Base value ({self.base_value}) is above maximum limit ({self.limit}). Progress calculation may yield unexpected results for series: {self.tag}')
                base_value = abs(self.base_value)
                limit = abs(self.limit)
                a = 4.44
                if base_value >= 2*limit: # check this condition first because want coeff = 1 if base_value and limit are both zero
                    coeff = 1
                elif base_value <= limit:
                    coeff = 1 - (base_value/limit)**a
                else:
                    coeff = 1 - ((2*limit - base_value)/limit)**a
            
                for key in ['high', 'med', 'low']:
                    progress_thresholds[key] *= coeff
                progress_thresholds['coefficient'] = coeff
                
        elif self.method == 2:
            # Quantitative method thresholds
            progress_thresholds = {'high': 0.95, 'med': 0.6, 'low': 0}
            progress_thresholds.update(user_thresholds)

            if self.limit is not None:
                self.warn(f'{self.inid} - Ignoring limit ({self.limit}) as target ({self.target}) already provided for progress calculation of series: {self.tag}')

        return progress_thresholds

    def get_progress_calculation_components(self):
        """Return a dict of the components for the progress calculation of this series.
        """
        return {
            self.tag: {
                'base_value': floatNone(self.base_value),
                'base_year': floatNone(self.base_year),
                'current_value': floatNone(self.current_value),
                'current_year': floatNone(self.current_year),
                'target': floatNone(self.target),
                'target_year': floatNone(self.target_year),
                'direction': self.direction,
                'sign': self.sign,
                'limit': self.limit,
                'progress_value': floatNone(self.progress_value),
                'status': self.status,
                'score': floatNone(self.score)
            }
        }


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
    
def floatNone(x):
    """Cast input value to float. 
    If input value is None, do not attempt to cast to float and return None instead.
    """
    if x is not None:
        return float(x)