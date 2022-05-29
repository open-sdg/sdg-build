import sdg
import os
import common

def test_sdmx_meta_input():

    meta_input = sdg.inputs.InputSdgMetadata(
        repo_subfolder='translations-metadata',
    )
    indicator_options = sdg.IndicatorOptions()
    meta_input.execute(indicator_options=indicator_options)
    meta = meta_input.indicators['1-2-1'].meta
    assert meta['SDG_GOAL'] == '<p>Goal 1: End poverty in all its forms everywhere</p>'
