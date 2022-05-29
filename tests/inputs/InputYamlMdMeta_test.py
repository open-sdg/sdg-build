import sdg
import os
import common

def test_yaml_md_meta_input():

    meta_pattern = os.path.join('tests', 'meta2', 'yamlmd', '*.md')
    meta_input = sdg.inputs.InputYamlMdMeta(
        path_pattern=meta_pattern,
        git=False,
    )
    indicator_options = sdg.IndicatorOptions()
    meta_input.execute(indicator_options=indicator_options)

    common.assert_input_has_correct_meta(meta_input.indicators['1-1-1'].meta)
