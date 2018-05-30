import pytest
import os
import json
import shutil
import numpy as np
import pandas as pd
from sdg import build_data
from sdg.path import output_path, input_path, get_ids

src_dir = os.path.dirname(os.path.realpath(__file__))

@pytest.fixture(scope='session')
def test_site_dir(tmpdir_factory):
    site_dir = tmpdir_factory.mktemp('_site')
    return str(site_dir)

def test_build(test_site_dir):
    """Check that output_path is as expected"""

    site_dir = test_site_dir

    build_result = build_data(src_dir=src_dir, site_dir=site_dir, git=False)
    assert build_result

    exp_dirs = set(['comb', 'data', 'edges', 'headline', 'meta'])
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
