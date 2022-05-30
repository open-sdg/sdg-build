import sdg
import os
import json
import pandas as pd
import outputs_common

english_build = os.path.join('_site', 'en')

def test_geojson_output():

    geojson_file = os.path.join('tests', 'geojson', 'england-regions.geojson')
    data_pattern = os.path.join('tests', 'data', 'csv-with-geocodes', '*.csv')
    data_input = sdg.inputs.InputCsvData(path_pattern=data_pattern)
    schema_path = os.path.join('tests', 'meta', 'metadata_schema.yml')
    schema = sdg.schemas.SchemaInputOpenSdg(schema_path=schema_path)
    translations = sdg.translations.TranslationInputSdgTranslations()
    data_output = sdg.outputs.OutputGeoJson([data_input], schema,
        translations=[translations],
        geojson_file=geojson_file,
        name_property='rgn17nm',
        id_property='rgn17cd',
    )
    assert data_output.validate()
    assert data_output.execute_per_language(['en'])

    json_path = os.path.join(english_build, 'geojson', 'regions', 'indicator_1-1-1.geojson')
    with open(json_path, 'r') as f:
        data = json.load(f)
        assert data['features'][0]['properties']['name'] == 'North East'
        assert data['features'][0]['properties']['disaggregations'][0]['Region'] == 'North East'
        assert data['features'][0]['properties']['values'][0]['2011'] == 70
