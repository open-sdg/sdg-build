import sdg
import os
import common

def test_sdmx_multiple_input():

    data_pattern = os.path.join('tests', 'data2', 'sdmx', 'multiple', '*.xml')
    data_input = sdg.inputs.InputSdmxMl_Multiple(
        path_pattern=data_pattern,
        import_codes=True,
    )
    indicator_options = sdg.IndicatorOptions()
    data_input.execute(indicator_options=indicator_options)

    common.assert_input_has_correct_data(data_input.indicators['1-1-1'].data)
    common.assert_input_has_correct_data(data_input.indicators['1-2-1'].data)
