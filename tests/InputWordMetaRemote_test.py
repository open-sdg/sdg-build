import sdg
import os
import inputs_common

def test_word_meta_remote_input():

    indicator_id_map = {
        'https://github.com/open-sdg/sdg-build/raw/HEAD/tests/assets/meta/word/1-1-1.docm': '1-1-1',
    }
    meta_input = sdg.inputs.InputWordMetaRemote(
        indicator_id_map=indicator_id_map,
    )
    indicator_options = sdg.IndicatorOptions()
    meta_input.execute(indicator_options=indicator_options)
    meta = meta_input.indicators['1-1-1'].meta
    assert meta['SDG_INDICATOR_INFO'] == '<p>1</p>'
