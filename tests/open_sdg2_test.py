"""
This is a second version of open_sdg_test.py, intended to test
small variations in the typical Open SDG output defaults.
"""

import sdg
import os
import OutputOpenSdg2_test

def test_open_sdg():
    config_path = os.path.join('tests', 'assets', 'open-sdg', 'config_data2.yml')
    assert sdg.open_sdg_check(config=config_path)
    assert sdg.open_sdg_build(config=config_path)

    OutputOpenSdg2_test.test_open_sdg_output_stats_disaggregation()
