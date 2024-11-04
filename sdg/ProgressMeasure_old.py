# TO DO:
# separate progress_thresholds from progress_calculation_options
# What to do about when aggregating over progress values where some are None? Ignore the None values? Return None?    


def apply(function, values, **kwargs):
    """
    Applies the input function to the input values.
    **kwargs can be specified, optionally.
    """
    return function(values, **kwargs)


def get_progress_calculation_options(metadata):
    """
    Get progress calculation options from the indicator metadata.
    If progress calculation options are not specified in the metadata, 
    return the default progress calculation options instead.
    """
    if metadata is not None:
        progress_calc_opts = metadata.get('progress_calculation_options')
        # progress_calc_opts is a list of dictionaries
        # each dictionary corresponds to the options for one series/unit/disaggregation
        if progress_calc_opts:
            return [config_defaults(config) for config in progress_calc_opts]
        
    return [default_progress_calc_options()]

def measure_indicator_progress(indicator, agg_func=min, **kwargs):
    """
    Read the progress calculation configurations from the indicator metadata and return the aggregate progress 
    measure value and status for the indicator. If the progress calculation configurations specify multiple 
    series, units, and/or disaggregations, the progress value for each is calculated and an aggregate progress 
    value is determined using the specified aggregation function.

    Args:
        indicator: Indicator object. 
        indicator_options: IndicatorOptions object. 
        agg_func: function. Function taken to compute the aggregate progress value from a list of progress values for each series/unit/disaggregation specified in the progress calculation configurations. Default: min()
        **kwargs: **kwargs for agg_func
    Returns:

    """
    data = indicator.data  # get indicator data
    meta = indicator.meta  # get configurations
    indicator_options = indicator.options

    # Check if progress calculation is turned on
    if meta.get('auto_progress_calculation') is True:
        # Get the progress calculation options from the metadata (or the default values if none are specified).
        progress_calc_options = get_progress_calculation_options(meta)
        method = get_method(meta)
        progress_thresholds = get_progress_thresholds(meta)
        # Calculate the progress measure value for each series/unit/disaggregation specified in the options.
        progress_values = [measure_progress(data, config, indicator_options) for config in progress_calc_options]
        # What to do with None values?
        # 1) ignore None values?
        progress_values = [x for x in progress_values if x is not None]
        output_value = apply(agg_func, progress_values, **kwargs)
        return output_value, get_progress_status(output_value, meta)
        # # OR 2) return None?
        # if None not in progress_values:
        #     output_value = apply(agg_func, progress_values, **kwargs)
        #     return output_value, get_progress_status(output_value, meta)



def measure_progress(data, config, indicator_options):
    """Sets up all needed parameters and data for progress calculation, determines methodology for calculation,
    and returns progress measure as an output.

    Args:
        data: 
        config: 
        indicator_options: 
    Returns:
        output: float. A value indicating the progress measurement for the indicator.
    """
    # get relevant data to calculate progress (aggregate/total line only)
    data = data_progress_measure(data, config, indicator_options)
    if data is None:
        return None

    # get years that exist in the data
    years = data["Year"]

    # set current year to be the most recent year that exists in data
    current_year = {'current_year': years.max()}
    # update the calculation inputs with the current year
    config.update(current_year)

    # check if the base year input exists in the data
    if config['base_year'] not in years.values:
        # return None if the base year input is in the future of the most recently available data
        if config['base_year'] > years.max():
            return None
        # if base year is not in available data and not in the future,
        # assign it to be the minimum existing year past the base year given
        config['base_year'] = years[years > config['base_year']].min()

    # return None if there is not enough data to calculate progress (must be at least 2 data points)
    if config['current_year'] - config['base_year'] < 1:
        return None

    # determine which methodology to run
    # if no target exists, run methodology for qualitative target. else run methodology for quantitative target.
    if config['target'] is None:
        # update progress thresholds for qualitative target
        config = update_progress_thresholds(config, method=1)
        # do progress calculation according to methodology for qualitative target
        output = methodology_1(data=data, config=config)

    else:
        # update progress thresholds for quantitative target
        config = update_progress_thresholds(config, method=2)
        # do progress calculation according to methodology for quantitative target
        output = methodology_2(data=data, config=config)

    return output


def config_defaults(config):
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
            # 'progress_thresholds': {}
        }
    )


def get_progress_thresholds(meta, method, default1={'high': 0.015, 'med': 0.005, 'low': 0}, default2={'high': 0.95, 'med': 0.6, 'low': 0}):
    """Checks for configured progress thresholds or updates thresholds based on methodology.
    Args:
        config: dict. Progress calculation inputs for indicator.
        method: int. Indicates which methodology is being used. Either 1 (for qualitative targets) or 2 (for
                quantitative targets).
    Returns:
        dict: Dictionary of updated inputs for calculation.
    """

    # if progress threshold inputs exist and are not empty, assign user input value as thresholds
    # otherwise if progress threshold inputs are empty, use defaults
    if ('progress_thresholds' in config.keys()) & (bool(config['progress_thresholds'])):
        progress_thresholds = config['progress_thresholds']
    elif method == 1:
        progress_thresholds = {'high': 0.015, 'med': 0.005, 'low': 0}
    elif method == 2:
        progress_thresholds = {'high': 0.95, 'med': 0.6, 'low': 0}
    else:
        progress_thresholds = {}

    # update inputs with thresholds
    config.update(progress_thresholds)

    return config


def data_progress_measure(data, config=None, indicator_options=None):
    """Checks and filters data for indicator for which progress is being calculated.

    If the Year column in data contains more than 4 characters (standard year format), takes the first 4 characters.
    If data contains disaggregation columns, take only the total line data.
    Removes any NA values.
    Checks that there is enough data to calculate progress.

    Args:
        data: DataFrame. Indicator data for which progress is being calculated.
    Returns:
        DataFrame: Data in valid format for calculating progress.
    """

    # check if the year value contains more than 4 digits (indicating a range of years)
    if (data['Year'].astype(str).str.len() > 4).any():
        # take the first year in the range
        data['Year'] = data['Year'].astype(str).str.slice(0, 4).astype(int)

    series_column = indicator_options.series_column
    unit_column = indicator_options.unit_column
    non_disaggregation_columns = indicator_options.non_disaggregation_columns
    cols = data.columns

    if len(cols) > 2:
        # Data has disaggregation columns. Find the appropriate subset of data for progress calculation
        # If units and/or series columns exist, keep only the user selected unit/series
        if (unit_column in cols) and ('unit' in config.keys()):
            data = data.loc[data[unit_column] == config['unit']]
        if (series_column in cols) and ('series' in config.keys()):
            data = data.loc[data[series_column] == config['series']]
        # If disaggregation specified by user, reduce the dataframe to only include the selected disaggregation
        disaggregation = config.get('disaggregation')
        if disaggregation:
            for k, v in disaggregation.items():
                data = data.loc[data[k] == v]
        # Otherwise, find headline data (rows where values in all disaggregation dimensions are NA)
        else:
            data = data[data.loc[:, ~cols.isin(non_disaggregation_columns)].isna().all('columns')]
        # Keep only Year and Value columns
        data = data.iloc[:, [0, -1]]

        # To do: 
        # Add PROGRESS/Progress to non_disaggregation columns
        # if progress column in cols: use progress column values instead of Value
        # What if no unit/series is selected by user but series/units column(s) exist? --> error? alphabetical? first appearing? None? Warning?
        # What if indicator_options = None or config = None?
        # Fix: when data not sufficiently reduced by user settings, there can be multiple values for the same year

    # remove any NA values from data
    data = data[data["Value"].notna()]

    # returns None if no rows in data (no total line to calculate progress)
    if data.shape[0] < 1:
        return None

    return data


def growth_calculation(val1, val2, t1, t2):
    """Calculate cumulative annual growth rate with required arguments.

    Args:
        val1: float. Current value.
        val2: float. Value from base year.
        t1: float. Current year.
        t2: float. Base year.
    Returns:
        float: Growth value.
    """

    return ((val1 / val2) ** (1 / (t1 - t2))) - 1


def methodology_1(data, config):
    """Calculate growth using progress measurement methodology 1 (no target value).

    Use configuration options to get the current and base value from indicator data and use to calculate growth.
    Compare growth to progress thresholds to return a progress measurement.

    Args:
        data: DataFrame. Indicator data for which progress is being calculated.
        config: dict. Configurations for indicator for which progress is being calculated.
    Returns:
        str: Progress measure.
    """

    direction = str(config['direction'])
    t = float(config['current_year'])
    t_0 = float(config['base_year'])
    x = float(config['high'])
    y = float(config['med'])
    z = float(config['low'])

    # get current value from data
    current_value = data.Value[data.Year == t].values[0]
    # get value from base year from data
    base_value = data.Value[data.Year == t_0].values[0]
    # calculate growth
    cagr_o = growth_calculation(current_value, base_value, t, t_0)

    # use negative growth value if desired direction of progress is negative
    if direction == "negative":
        cagr_o = -1 * cagr_o

    return cagr_o


def methodology_2(data, config):
    """Calculate growth using progress measurement methodology 2 (given target value).

    Check if target has already been achieved.
    Use configuration options to get the current and base value from indicator data and use to calculate growth ratio.

    Args:
        data: DataFrame. Indicator data for which progress is being calculated.
        config: dict. Configurations for indicator for which progress is being calculated.
    Returns:
        str: Progress status.
    """

    direction = str(config['direction'])
    t = float(config['current_year'])
    t_0 = float(config['base_year'])
    target = float(config['target'])
    t_tao = float(config['target_year'])

    # get current value from data
    current_value = data.Value[data.Year == t].values[0]
    # get base value from data
    base_value = data.Value[data.Year == t_0].values[0]

    # check if the target is achieved
    if (direction == "negative" and current_value <= target) or (direction == "positive" and current_value >= target):
        return "target_achieved"

    # calculate observed growth
    cagr_o = growth_calculation(current_value, base_value, t, t_0)
    # calculate theoretical growth
    cagr_r = growth_calculation(target, base_value, t_tao, t_0)
    # calculating growth ratio
    ratio = cagr_o / cagr_r

    return ratio


def get_progress_status(value, config):
    """Compare growth rate to progress thresholds provided in configs to return progress status.

    Use configuration options to get the high, middle, and low thresholds to compare to the value
    and return a progress status label.

    Args:
        value: float. Calculated value of either observed growth or growth ratio for an indicator.
        config: dict. Configurations for indicator for which progress is being calculated.

    Returns: str. Progress status label.

    """

    x = float(config['high'])
    y = float(config['med'])
    z = float(config['low'])

    # compare growth rate to progress thresholds to return progress measure
    if value >= x:
        return "on_track"
    elif y <= value < x:
        return "progress_needs_acceleration"
    elif z <= value < y:
        return "limited_progress"
    elif value < z:
        return "deterioration"
    else:
        return None