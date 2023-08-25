import sdg
import os
import inputs_common
import pytest

def test_yaml_md_meta_input():

    meta_pattern = os.path.join('tests', 'assets', 'meta', 'yamlmd', '*.md')
    meta_input = sdg.inputs.InputYamlMdMeta(
        path_pattern=meta_pattern,
        git=False,
    )
    indicator_options = sdg.IndicatorOptions()
    meta_input.execute(indicator_options=indicator_options)

    inputs_common.assert_input_has_correct_meta(meta_input.indicators['1-1-1'].meta)

def test_yaml_md_meta_input_with_problems():
    meta_pattern = os.path.join('tests', 'assets', 'meta', 'yamlmd-with-problems', '*.md')
    meta_input = sdg.inputs.InputYamlMdMeta(
        path_pattern=meta_pattern,
        git=False,
    )
    indicator_options = sdg.IndicatorOptions()
    with pytest.raises(Exception) as e_info:
        meta_input.execute(indicator_options=indicator_options)
