import sdg
import os
import common

def test_csv_input():
    """Test the build with the object-oriented approach"""

    data_pattern = os.path.join('tests', 'data2', '*.csv')
    data_input = sdg.inputs.InputCsvData(path_pattern=data_pattern)
    indicator_options = sdg.IndicatorOptions()
    data_input.execute(indicator_options=indicator_options)

    common.assert_input_has_correct_data(data_input.indicators['1-1-1'].data)
