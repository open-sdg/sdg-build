import sdg
import os
import inputs_common

def test_sdmx_structure_specific_input():

    dimension_query = {
        'SERIES': 'SI_POV_DAY1',
        'SEX': 'F',
    }
    data_input = sdg.inputs.InputSdmxMl_UnitedNationsApi(
        reference_area=826,
        dimension_query=dimension_query,
        import_codes=True,
    )
    indicator_options = sdg.IndicatorOptions()
    data_input.execute(indicator_options=indicator_options)

    df = data_input.indicators['1-1-1'].data
    value_2015 = df.loc[df['Year'] == 2015, 'Value']
    assert value_2015.iloc[0] == 0.55696
