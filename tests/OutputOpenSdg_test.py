import sdg
import os
import json
import pandas as pd
import outputs_common

english_build = os.path.join('_site_open_sdg', 'en')

def test_open_sdg_output():

    data_pattern = os.path.join('tests', 'assets', 'open-sdg', 'data', '*.csv')
    data_input = sdg.inputs.InputCsvData(path_pattern=data_pattern)
    schema_path = os.path.join('tests', 'assets', 'open-sdg', 'metadata_schema.yml')
    schema = sdg.schemas.SchemaInputOpenSdg(schema_path=schema_path)
    translations = sdg.translations.TranslationInputSdgTranslations()
    data_output = sdg.outputs.OutputOpenSdg([data_input], schema,
        translations=[translations],
        output_folder='_site_open_sdg',
    )
    assert data_output.validate()
    assert data_output.execute_per_language(['en'])

    exp_dirs = set(['comb', 'data', 'edges', 'headline', 'meta', 'stats', 'zip', 'translations'])
    act_dirs = os.listdir(english_build)
    assert all([a in exp_dirs for a in act_dirs])

def test_open_sdg_output_comb():

    json_path = os.path.join(english_build, 'comb', '1-1-1.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
        assert data['data']['Value'][0] == 100
        assert len(data['edges']) == 0

def test_open_sdg_output_data_json():

    json_path = os.path.join(english_build, 'data', '1-1-1.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
        assert data['Value'][0] == 100
    
def test_open_sdg_output_data_csv():

    csv_path = os.path.join(english_build, 'data', '1-1-1.csv')
    df = pd.read_csv(csv_path)
    outputs_common.assert_input_has_correct_data(df)

def test_open_sdg_output_edges_json():

    json_path = os.path.join(english_build, 'edges', '1-1-1.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
        assert len(data) == 0
    
def test_open_sdg_output_edges_csv():

    csv_path = os.path.join(english_build, 'edges', '1-1-1.csv')
    df = pd.read_csv(csv_path)
    assert df.columns.tolist() == ['From', 'To']
    assert len(df) == 0

def test_open_sdg_output_headline_json():

    json_path = os.path.join(english_build, 'headline', '1-1-1.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
        assert data[0]['Value'] == 100
    
def test_open_sdg_output_headline_csv():

    csv_path = os.path.join(english_build, 'headline', '1-1-1.csv')
    df = pd.read_csv(csv_path)
    outputs_common.assert_input_has_correct_headline(df)

def test_open_sdg_output_headline_all():

    json_path = os.path.join(english_build, 'headline', 'all.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
        assert data['1-1-1'][0]['Value'] == 100

def test_open_sdg_output_meta_json():

    json_path = os.path.join(english_build, 'meta', '1-1-1.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
        assert data['indicator_number'] == '1.1.1'

def test_open_sdg_output_meta_all():
    json_path = os.path.join(english_build, 'meta', 'all.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
        assert data['1-1-1']['indicator_number'] == '1.1.1'

def test_open_sdg_output_meta_schema():

    json_path = os.path.join(english_build, 'meta', 'schema.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
        assert data[0]['name'] == 'foo'

def test_open_sdg_output_stats_disaggregation():
    json_path = os.path.join(english_build, 'stats', 'disaggregation.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
        assert data['statuses'][0]['value'] == 'complete'
        assert data['overall']['statuses'][0]['status'] == 'complete'
        assert data['overall']['statuses'][0]['percentage'] == 0.0
        assert data['overall']['statuses'][3]['status'] == 'notapplicable'
        assert data['overall']['statuses'][3]['percentage'] == 100.0
        assert data['overall']['totals']['total'] == 1
        assert data['goals'][0]['goal'] == '1'
        assert data['goals'][0]['statuses'][3]['count'] == 1
        assert data['extra_fields'] == {}

def test_open_sdg_output_stats_reporting():
    json_path = os.path.join(english_build, 'stats', 'reporting.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
        assert data['statuses'][0]['value'] == 'complete'
        assert data['overall']['statuses'][0]['status'] == 'complete'
        assert data['overall']['statuses'][0]['percentage'] == 100.0
        assert data['overall']['totals']['total'] == 1
        assert data['goals'][0]['goal'] == 1
        assert data['goals'][0]['statuses'][0]['count'] == 1
        assert data['extra_fields'] == {}

def test_open_sdg_output_translations():
    json_path = os.path.join(english_build, 'translations', 'translations.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
        assert data['calendar']['April'] == 'April'

def test_open_sdg_output_zip():
    json_path = os.path.join(english_build, 'zip', 'all_indicators.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
        assert data['size_bytes'] == 191
        assert data['size_human'] == '191 Bytes'
        assert data['filename'] == 'all_indicators.zip'
    zip_path = os.path.join(english_build, 'zip', 'all_indicators.zip')
    assert os.path.isfile(zip_path)
