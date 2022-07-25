# TODO: Re-write docstrings
# TODO: create more tests
# import pandas as pd
import yaml
import sys
import sdg
import os


def measure_indicator_progress(indicator):
    """Assigns year values and determines methodology to be run.

    Args:
        indicator: str. Indicator number for which the data is being read.
    """

    data = indicator.data    # get indicator data
    print(data)

    config = indicator.meta  # get configurations
    print(config)

    # check if progress calculation is turned on and if inputs have been configured
    # return None if auto progress calculation is not turned on
    print('checking if progress calc is turned on...')
    if 'auto_progress_calculation' in config.keys():
        print('meta field required exists')
        if config['auto_progress_calculation']:
            print('progress calc is turned on. continuing...')
            if 'progress_calculation_options' in config.keys():
                print('taking user configured inputs')
                config = config['progress_calculation_options'][0]
                print(config)
        else:
            print('progress calc is not turned on. exit...')
            return(None)
    else:
        print('progress calc is not turned on. exit...')
        return(None)

    config = config_defaults(config)
    print(config)

    # get relevant data to calculate progress
    data = data_progress_measure(data)
    print(data)

    if data is None:
        return(None)

    years = data["Year"]                           # get years from data
    print(years)
    current_year = {'current_year': years.max()}   # set current year to be MAX(Year)
    print(current_year)
    config.update(current_year)
    print(config)



    if config['base_year'] not in years.values:          # check if assigned base year is in data
        print('base year is not in year values')
        if config['base_year'] > years.max():
            print('base year is ahead of most recently available data')
            return None
        config['base_year'] = years[years > 2015].min()  # if not, assign MIN(Year > 2015) to be base year
        print('updating base year to ' + str(config['base_year']))
    print(config)

    # check if there is enough data to calculate progress
    if config['current_year'] - config['base_year'] < 1:
        print('not enough data')
        return None


    # determine which methodology to run
    if config['target'] is None:
        print('updating progress thresholds')
        config = update_progress_thresholds(config, method=1)
        print('running methodology 1')
        output = methodology_1(data=data, config=config)

    else:
        print('updating progress thresholds')
        config = update_progress_thresholds(config, method=2)
        print('running methodology 2')
        output = methodology_2(data=data, config=config)

    return(output)

def check_auto_calc():
    print('temp')

def config_defaults(config):
    """Set progress calculation defaults and update them from the configuration.
    Args:
        indicator: str. Indicator number for which the configuration is from.
    Returns:
        dict: Dictionary of updated configurations.
    """

    # set default options for progress measurement
    defaults = default_progress_calc_options()
    defaults.update(config) # update the defaults with any user configured inputs

    # if target is 0, set to 0.001
    if defaults['target'] == 0:
        defaults['target'] = 0.001

    return defaults


def default_progress_calc_options():
    return(
        {
            'base_year': 2015,
            'target_year': 2030,
            'direction': 'negative',
            'target': None,
            'progress_thresholds': {}
        }
    )


def update_progress_thresholds(config, method):
    """Checks for configured progress thresholds and updates based on methodology.
    Args:
        config: dict. Configurations for indicator for which progress is being calculated.
        method: int. Indicates which methodology is being used. Either 1 or 2.
    Returns:
        dict: Dictionary of updated configurations.
    """

    if ('progress_thresholds' in config.keys()) & (bool(config['progress_thresholds'])):
        # TODO: Handle potential error inputs
        print('thresholds are configured')
        progress_thresholds = config['progress_thresholds']

    elif method == 1:
        print('thresholds are not configured, use defaults for method1')
        progress_thresholds = {'high': 0.01, 'med': 0, 'low': -0.01}

    elif method == 2:
        print('thresholds are not configured, use defaults for method2')
        progress_thresholds = {'high': 0.95, 'med': 0.6, 'low': 0}

    else:
        progress_thresholds = {}


    print(progress_thresholds)
    config.update(progress_thresholds)
    print(config)

    return config


def data_progress_measure(data):
    """Checks and filters data for indicator for which progress is being calculate.

    If the Year column in data contains more than 4 characters (standard year format), takes the first 4 characters.
    If data contains disaggregation columns, take only the total line data.
    Removes any NA values.
    Checks that there is enough data to calculate progress.

    Args:
        data: DataFrame. Indicator data for which progress is being calculate.
    Returns:
        DataFrame: Data in allowable format for calculating progress.
    """

    # check if the year value contains more than 4 digits (indicating a range of years)
    print('checking the year column')
    if (data['Year'].astype(str).str.len() > 4).any():
        data['Year'] = data['Year'].astype(str).str.slice(0, 4).astype(int)  # take the first year in the range

    # get just the aggregate values from data
    print('filtering out aggregates (if any)')
    cols = data.columns.values
    if len(cols) > 2:
        cols = cols[1:-1]
        data = data[data[cols].isna().all('columns')]
        data = data.iloc[:, [0, -1]]
    data = data[data["Value"].notna()]  # remove any NA values from data

    if data.shape[0] < 1:
        print('no aggregate')
        return(None)

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

    return ( (val1 / val2) ** (1 / (t1 - t2)) ) - 1


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
    t         = float(config['current_year'])
    t_0       = float(config['base_year'])
    x         = float(config['high'])
    y         = float(config['med'])
    z         = float(config['low'])

    current_value = data.Value[data.Year == t].values[0]
    base_value = data.Value[data.Year == t_0].values[0]
    cagr_o = growth_calculation(current_value, base_value, t, t_0)

    if direction=="negative":
        cagr_o = -1*cagr_o
    print('cagr_o:' + str(cagr_o))

    # TODO: Adopt categories to Open SDG progress categories (or make our categories work with Open SDG)
    # TODO: Change progress labels: Negative, negligeable, fair/moderate, substantial, target achieved.

    if cagr_o > x:
        return "substantial_progress"
    elif y < cagr_o <= x:
        return "moderate_progress"
    elif z <= cagr_o <= y:
        return "moderate_deterioration"
    elif cagr_o < z:
        return "significant_deterioration"
    else:
        return None


def methodology_2(data, config):
    """Calculate growth using progress measurement methodology 2 (given target value).

    Check if target has already been achieved.
    Use configuration options to get the current and base value from indicator data and use to calculate growth ratio.
    Compare growth ratio to progress thresholds to return a progress measurement.

    Args:
        data: DataFrame. Indicator data for which progress is being calculated.
        config: dict. Configurations for indicator for which progress is being calculated.
    Returns:
        str: Progress measure.
    """

    # TODO: how to deal with the instance of target being met then diverged from?
    # TODO: there's something wrong with the calculation - it is outputting significant progress when should be deterioration
    # TODO: ?????????????????????


    direction = str(config['direction'])
    t         = float(config['current_year'])
    t_0       = float(config['base_year'])
    target    = float(config['target'])
    t_tao     = float(config['target_year'])
    x         = float(config['high'])
    y         = float(config['med'])
    z         = float(config['low'])


    current_value = data.Value[data.Year == t].values[0]  # get current value from data
    print('current value:' + str(current_value))
    base_value = data.Value[data.Year == t_0].values[0]   # get base value from data
    print('base value:' + str(base_value))


    # check if the target is achieved
    if (direction == "negative" and current_value <= target) or (direction == "positive" and current_value >= target):
        return "target_achieved"

    cagr_o = growth_calculation(current_value, base_value, t, t_0)   # calculating observed growth
    print('cagr_o:' + str(cagr_o))
    cagr_r = growth_calculation(target, base_value, t_tao, t_0)      # calculating theoretical growth
    print('cagr_r:' + str(cagr_r))
    ratio  = cagr_o / cagr_r                                         # calculating growth ratio
    print('growth ratio:' + str(ratio))

    # TODO: Adopt categories to Open SDG progress categories (or make our categories work with Open SDG)
    # compare growth ratio to progress thresholds & return output
    if ratio >= x:
        return "substantial_progress"
    elif y <= ratio < x:
        return "moderate_progress"
    elif z <= ratio < y:
        return "negligible_progress"
    elif ratio < z:
        return "negative_progress"
    else:
        return None




# measure_indicator_progress('6-1-1') # example with target = 0
# measure_indicator_progress('3-2-1') # example with not enough data/fiscal year input
# measure_indicator_progress('3-4-1')   # example with no target

data_pattern = os.path.join('assets', 'progress-calculation', 'data', '*-*.csv')
data_input = sdg.inputs.InputCsvData(path_pattern=data_pattern)

# Input metadata from YAML files matching this pattern: tests/meta/*-*.md
meta_pattern = os.path.join('assets', 'progress-calculation', 'indicator-config', '*-*.yml')
meta_input = sdg.inputs.InputYamlMeta(path_pattern=meta_pattern)

# Combine these inputs into one list
inputs = [data_input, meta_input]

# Use a Prose.io file for the metadata schema.
schema_path = os.path.join('assets', 'meta', 'metadata_schema.yml')
schema = sdg.schemas.SchemaInputOpenSdg(schema_path=schema_path)

opensdg_output = sdg.outputs.OutputOpenSdg(
    inputs=inputs,
    schema=schema,
    output_folder='_site')

test_indicator = opensdg_output.test_indicator()
indicator_id = test_indicator.meta['indicator_number']

progress_measure = measure_indicator_progress(test_indicator)
print(progress_measure)
# prog_calcs = {indicator_id: progress_measure}
# print(prog_calcs)