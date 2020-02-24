import pytest
import os
import json
import shutil
import numpy as np
import pandas as pd
import sdg
from sdg import build_data
from sdg.path import output_path, input_path, get_ids

src_dir = os.path.dirname(os.path.realpath(__file__))

@pytest.fixture(scope='session')
def test_site_dir(tmpdir_factory):
    site_dir = tmpdir_factory.mktemp('_site')
    return str(site_dir)


def test_build(test_site_dir):
    """Test the build with the object-oriented approach"""

    site_dir = test_site_dir

    data_pattern = os.path.join('tests', 'data', '*-*.csv')
    data_input = sdg.inputs.InputCsvData(path_pattern=data_pattern)
    meta_pattern = os.path.join('tests', 'meta', '*-*.md')
    meta_input = sdg.inputs.InputYamlMdMeta(path_pattern=meta_pattern)
    inputs = [data_input, meta_input]
    schema_path = os.path.join('tests', '_prose.yml')
    schema = sdg.schemas.SchemaInputOpenSdg(schema_path=schema_path)
    translations = sdg.translations.TranslationInputSdgTranslations()
    opensdg_output = sdg.outputs.OutputOpenSdg(
        inputs=inputs,
        schema=schema,
        output_folder=site_dir,
        translations=translations)

    assert opensdg_output.validate()
    assert opensdg_output.execute()

    # Also generate GeoJSON output.
    geojson_output = sdg.outputs.OutputGeoJson(
        inputs=inputs,
        schema=schema,
        output_folder=site_dir,
        translations=translations,
        geojson_file=os.path.join(src_dir, 'geojson', 'england-regions.geojson'),
        name_property='rgn17nm',
        id_property='rgn17cd')

    assert geojson_output.validate()
    assert geojson_output.execute()

    exp_dirs = set(['comb', 'data', 'edges', 'headline', 'meta', 'stats', 'zip', 'translations', 'geojson'])
    act_dirs = os.listdir(site_dir)

    assert all([a in exp_dirs for a in act_dirs])


def test_built_json(test_site_dir):
    meta9 = json.load(
        open(
            output_path('9-3-1', ftype='meta', format='json',
                        site_dir=test_site_dir)
        )
    )
    assert meta9['indicator'] == '9.3.1'


def test_reporting_json(test_site_dir):
    stats_reporting = json.load(
        open(
            output_path('reporting', ftype='stats', format='json',
                        site_dir=test_site_dir)
        )
    )
    assert stats_reporting['goals'][7]['totals']['total'] == 2


# This stuff needs to go in tests
def isclose_df(df1, df2):
    """A mix of np isclose and pandas equals that works across
    python versions. So many api changes in pandas and numpy!"""
    status = True
    for col in df1:
        if np.issubdtype(df1[col].dtype, np.number):
            status = status & np.isclose(df1[col],
                                         df2[col],
                                         equal_nan=True).all()
        else:
            status = status & df1[col].equals(df2[col])
    return status


def compare_reload_data(inid, src_dir, site_dir):
    """Load the original csv and compare to reloading the JSON you wrote out
    which = 'edges' or 'data'
    """

    csv_path = input_path(inid, ftype='data', src_dir=src_dir)
    jsn_path = output_path(inid, ftype='comb', format='json', site_dir=site_dir)

    jsn = json.load(open(jsn_path))

    df_csv = pd.read_csv(csv_path, encoding='utf-8')
    df_jsn = pd.DataFrame(jsn['data']).replace({None: np.nan})

    # Account for empty data
    if df_jsn.shape[0] == df_csv.shape[0] == 0:
        return True

    df_jsn = df_jsn[df_csv.columns.values]

    status = isclose_df(df_csv, df_jsn)
    if not status:
        print("reload error in "+inid)

    return status


def test_built_comb_data(test_site_dir):
    ids = get_ids(src_dir=src_dir)
    for inid in ids:
        assert compare_reload_data(inid, src_dir=src_dir, site_dir=test_site_dir)


def test_built_translations(test_site_dir):
    translations = json.load(
        open(
            output_path('translations', ftype='translations', format='json',
                        site_dir=test_site_dir)
        )
    )
    assert translations['de']['global_goals']['1-short'] == 'Keine Armut'


def test_built_schema(test_site_dir):
    schema_output = json.load(
        open(
            output_path('schema', ftype='meta', format='json',
                        site_dir=test_site_dir)
        )
    )
    reporting_status_field = next((item for item in schema_output if item['name'] == 'reporting_status'), None)
    assert reporting_status_field
    assert reporting_status_field['field']['label'] == 'Reporting status'


def test_built_geojson(test_site_dir):
    geojson = json.load(
        open(os.path.join(test_site_dir, 'geojson', 'regions', 'indicator_1-3-1.geojson'))
    )
    assert 'features' in geojson
