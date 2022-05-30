import sdg
import os
import json
import pandas as pd

english_build = os.path.join('_site', 'en')

def test_datapackage_output():

    data_pattern = os.path.join('tests', 'assets', 'data', 'csv', '*.csv')
    data_input = sdg.inputs.InputCsvData(path_pattern=data_pattern)
    schema_path = os.path.join('tests', 'assets', 'meta', 'metadata_schema.yml')
    schema = sdg.schemas.SchemaInputOpenSdg(schema_path=schema_path)
    translations = sdg.translations.TranslationInputSdgTranslations()
    data_output = sdg.outputs.OutputDataPackage([data_input], schema, translations=[translations])
    assert data_output.validate()
    assert data_output.execute_per_language(['en'])


def test_datapackage_output_json():

    json_path = os.path.join(english_build, 'data-packages', '1-1-1', 'datapackage.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
        assert data['resources'][0]['path'] == 'data.csv'
        assert data['resources'][0]['schema']['fields'][0] == {
            "name": "Year",
            "type": "integer",
            "title": "Year"
        }
        assert data['resources'][0]['schema']['fields'][1] == {
            "name": "SEX",
            "type": "string",
            "constraints": {
              "enum": [
                "M",
                "F",
                ""
              ]
            },
            "title": "SEX"
        }
        assert data['resources'][0]['schema']['fields'][2] == {
            "name": "Value",
            "type": "integer",
            "title": "Value"
        }

def test_datapackage_output_data():

    output_path = os.path.join(english_build, 'data-packages', '1-1-1', 'data.csv')
    correct_path = os.path.join('tests', 'assets', 'data', 'csv', 'indicator_1-1-1.csv')
    output_df = pd.read_csv(output_path)
    correct_df = pd.read_csv(correct_path)
    pd.testing.assert_frame_equal(correct_df, output_df)
