def measure_indicator_progress(indicator):
    """Sets up all needed parameters and data for progress calculation, determines methodology for calculation,
    and returns progress measure as an output.

    Args:
        indicator: Indicator for which the progress is being calculated for.
    Returns:
        output: str. A string indicating the progress measurement for the indicator.
    """

    data = indicator.data  # get indicator data
    config = indicator.meta  # get configurations

    # checks if progress calculation is turned on
    if 'auto_progress_calculation' in config.keys():

        # checks if any inputs have been configured
        if config['auto_progress_calculation']:

            if 'progress_calculation_options' in config.keys():
                # take manual user inputs
                config = config['progress_calculation_options'][0]

        else:
            return None

    # return None if auto progress calculation is not turned on
    else:
        return None

    # get calculation defaults and update with user inputs (if any)
    config = config_defaults(config)

    # get relevant data to calculate progress (aggregate/total line only)
    data = data_progress_measure(data)

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
            'progress_thresholds': {}
        }
    )


def update_progress_thresholds(config, method):
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


def data_progress_measure(data):
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

    # get just the total line values from data
    cols = data.columns.values
    if len(cols) > 2:
        cols = cols[1:-1]
        data = data[data[cols].isna().all('columns')]
        data = data.iloc[:, [0, -1]]

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

    return get_progress_status(cagr_o, config)


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

    return get_progress_status(ratio, config)


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