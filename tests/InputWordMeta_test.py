import sdg
import os
import inputs_common

def test_word_meta_input():

    meta_pattern = os.path.join('tests', 'assets', 'meta', 'word', '*.docm')
    meta_input = sdg.inputs.InputWordMeta(
        path_pattern=meta_pattern,
        git=False,
    )
    indicator_options = sdg.IndicatorOptions()
    meta_input.execute(indicator_options=indicator_options)
    meta = meta_input.indicators['1-1-1'].meta
    assert meta['SDG_INDICATOR_INFO'] == '<p>1</p>'
