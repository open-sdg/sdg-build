import sdg
import os
import common

def test_sdmx_structure_specific_input():

    data_path = os.path.join('tests', 'data2', 'sdmx', 'structure-specific', '1-1-1--structure-specific.xml')
    data_input = sdg.inputs.InputSdmxMl_StructureSpecific(
        source=data_path,
        import_codes=True,
    )
    indicator_options = sdg.IndicatorOptions()
    data_input.execute(indicator_options=indicator_options)

    common.assert_input_has_correct_data(data_input.indicators['1-1-1'].data)
