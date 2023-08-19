"""
This is a second version of OutputOpenSdg_test.py, intended to test
small variations in the typical Open SDG output defaults.
"""

import sdg
import os
import json
import pandas as pd
import outputs_common

english_build = os.path.join('_site_open_sdg2', 'en')

def test_open_sdg_output():

    data_pattern = os.path.join('tests', 'assets', 'open-sdg', 'data', '*.csv')
    data_input = sdg.inputs.InputCsvData(path_pattern=data_pattern)
    meta_pattern = os.path.join('tests', 'assets', 'meta', 'yaml', '*.yml')
    meta_input = sdg.inputs.InputYamlMeta(
        path_pattern=meta_pattern,
        git=False,
    )
    schema_path = os.path.join('tests', 'assets', 'open-sdg', 'metadata_schema.yml')
    schema = sdg.schemas.SchemaInputOpenSdg(schema_path=schema_path)
    translations = sdg.translations.TranslationInputSdgTranslations()
    data_output = sdg.outputs.OutputOpenSdg([data_input, meta_input], schema,
        translations=[translations],
        output_folder='_site_open_sdg2',
        ignore_out_of_scope_disaggregation_stats=True,
    )
    assert data_output.validate()
    assert data_output.execute_per_language(['en'])

    exp_dirs = set(['data', 'geojson', 'translations', 'meta', 'stats', 'csvw', 'headline', 'edges', 'zip', 'data-packages', 'comb'])
    act_dirs = os.listdir(english_build)
    assert all([a in exp_dirs for a in act_dirs])


def test_open_sdg_output_stats_disaggregation():
    json_path = os.path.join(english_build, 'stats', 'disaggregation.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
        assert data['statuses'][0]['value'] == 'complete'
        assert data['overall']['statuses'][0]['status'] == 'complete'
        assert data['overall']['statuses'][0]['percentage'] == 0.0
        assert data['overall']['totals']['total'] == 0
        assert data['goals'][0]['goal'] == '1'
        assert data['extra_fields'] == {}
