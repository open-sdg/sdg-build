import sdg
import os
import pandas as pd

def test_sdmx_ml_output():

    data_path = os.path.join('tests', 'assets', 'data', 'sdmx', 'structure-specific', '1-1-1--structure-specific.xml')
    data_input = sdg.inputs.InputSdmxMl_StructureSpecific(
        source=data_path,
        import_codes=True,
        drop_singleton_dimensions=False,
        import_observation_attributes=False,
    )
    schema_path = os.path.join('tests', 'assets', 'meta', 'metadata_schema.yml')
    schema = sdg.schemas.SchemaInputOpenSdg(schema_path=schema_path)
    output_folder = '_site_sdmx'
    data_output = sdg.outputs.OutputSdmxMl([data_input], schema,
        structure_specific=True,
        meta_reporting_type='N',
        meta_ref_area=862,
        output_folder=output_folder
    )
    assert data_output.validate()
    assert data_output.execute()

    output_path = os.path.join(output_folder, 'sdmx', '1-1-1.xml')
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

def test_sdmx_ml_output_with_code_map():

    code_map = os.path.join('tests', 'assets', 'misc', 'code-map.csv')

    data_path = os.path.join('tests', 'assets', 'data', 'sdmx', 'structure-specific', '1-1-1--structure-specific.xml')
    data_input = sdg.inputs.InputSdmxMl_StructureSpecific(
        source=data_path,
        import_codes=True,
        drop_singleton_dimensions=False,
        import_observation_attributes=False,
    )
    schema_path = os.path.join('tests', 'assets', 'meta', 'metadata_schema.yml')
    schema = sdg.schemas.SchemaInputOpenSdg(schema_path=schema_path)
    output_folder = '_site_sdmx_mapped'
    data_output = sdg.outputs.OutputSdmxMl([data_input], schema,
        structure_specific=True,
        meta_reporting_type='N',
        meta_ref_area=862,
        code_map=code_map,
        output_folder=output_folder
    )
    assert data_output.validate()
    assert data_output.execute()

    output_path = os.path.join(output_folder, 'sdmx', '1-1-1.xml')
    output_input = sdg.inputs.InputSdmxMl_StructureSpecific(
        source=output_path,
        import_codes=True,
        drop_singleton_dimensions=False,
    )
    indicator_options = sdg.IndicatorOptions()
    output_input.execute(indicator_options=indicator_options)

    data_mapped_path = os.path.join('tests', 'assets', 'data', 'sdmx', 'structure-specific', '1-1-1--structure-specific.xml')
    data_mapped_input = sdg.inputs.InputSdmxMl_StructureSpecific(
        source=data_path,
        import_codes=True,
        drop_singleton_dimensions=False,
<<<<<<< HEAD
        code_map=code_map,
        dsd=dsd_path,
        import_observation_attributes=False,
=======
        code_map=code_map
>>>>>>> parent of 0b450bf... Version global dsd
    )
    data_mapped_input.execute(indicator_options=indicator_options)

    input_df = data_mapped_input.indicators['1-1-1'].data
    output_df = output_input.indicators['1-1-1'].data
    pd.testing.assert_frame_equal(input_df, output_df)
