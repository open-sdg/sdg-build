import sdg
import os
import inputs_common

def test_csv_input():

    data_pattern = os.path.join('tests', 'assets', 'data', 'csv', '*.csv')
    data_input = sdg.inputs.InputCsvData(path_pattern=data_pattern)
    indicator_options = sdg.IndicatorOptions()
    data_input.execute(indicator_options=indicator_options)

    inputs_common.assert_input_has_correct_data(data_input.indicators['1-1-1'].data)
