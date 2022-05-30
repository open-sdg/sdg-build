import sdg
import os
import pandas as pd

def test_sdmx_ml_output():

    data_path = os.path.join('tests', 'data', 'sdmx', 'structure-specific', '1-1-1--structure-specific.xml')
    data_input = sdg.inputs.InputSdmxMl_StructureSpecific(
        source=data_path,
        import_codes=True,
        drop_singleton_dimensions=False,
    )
    schema_path = os.path.join('tests', 'meta', 'metadata_schema.yml')
    schema = sdg.schemas.SchemaInputOpenSdg(schema_path=schema_path)
    data_output = sdg.outputs.OutputSdmxMl([data_input], schema,
        structure_specific=True,
        meta_reporting_type='N',
        meta_ref_area=862,
    )
    assert data_output.validate()
    assert data_output.execute()

    output_path = os.path.join('_site', 'sdmx', '1-1-1.xml')
    output_input = sdg.inputs.InputSdmxMl_StructureSpecific(
        source=output_path,
        import_codes=True,
        drop_singleton_dimensions=False,
    )
    indicator_options = sdg.IndicatorOptions()
    output_input.execute(indicator_options=indicator_options)

    input_df = data_input.indicators['1-1-1'].data
    output_df = output_input.indicators['1-1-1'].data
    pd.testing.assert_frame_equal(input_df, output_df)
