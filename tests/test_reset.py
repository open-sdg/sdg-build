import pytest
import os
import shutil
from sdg import reset_all_csv, reset_all_meta
import pandas as pd
import yaml

src_dir = os.path.dirname(os.path.realpath(__file__))

def test_reset_csv(tmpdir):
    """Check reset csvs work"""

    testroot = str(tmpdir.mkdir('resetcsv'))

    shutil.copytree(os.path.join(src_dir, 'data'), os.path.join(testroot, 'data'))
    shutil.copytree(os.path.join(src_dir, 'meta'), os.path.join(testroot, 'meta'))

    reset_all_csv(src_dir=testroot)

    df = pd.read_csv(os.path.join(testroot, 'data', 'indicator_1-2-1.csv'))
    assert df.shape == (6, 3)

def test_reset_meta(tmpdir):
    """Check reset metadata"""

    testroot = str(tmpdir.mkdir('resetmeta'))

    shutil.copytree(os.path.join(src_dir, 'meta'), os.path.join(testroot, 'meta'))
    shutil.copy(os.path.join(src_dir, '_prose.yml'), os.path.join(testroot, '_prose.yml'))

    reset_all_meta(src_dir=testroot)

    with open(os.path.join(testroot, 'meta', '1-2-1.md'), encoding="UTF-8") as stream:
        meta = next(yaml.safe_load_all(stream))
    
    assert meta['indicator'] == '1.2.1'
    assert meta['reporting_status'] == 'notstarted'
