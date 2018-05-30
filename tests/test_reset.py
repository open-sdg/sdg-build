import pytest
import os
import shutil
from sdg import reset_all_csv, reset_all_meta
import pandas as pd
import yaml

root = os.path.dirname(os.path.realpath(__file__))

def test_reset_csv():
    """Check that output_path is as expected"""

    testroot = os.path.join(root, 'testroot')

    os.makedirs(testroot, exist_ok=False)
    shutil.copytree(os.path.join(root, 'data'), os.path.join(testroot, 'data'))
    shutil.copytree(os.path.join(root, 'meta'), os.path.join(testroot, 'meta'))

    reset_all_csv(root=testroot)

    df = pd.read_csv(os.path.join(testroot, 'data', 'indicator_1-2-1.csv'))
    assert df.shape == (6, 3)

    # poor man's teardown
    shutil.rmtree(testroot)

def test_reset_meta():
    """Check that output_path is as expected"""

    testroot = os.path.join(root, 'testroot2')

    os.makedirs(testroot, exist_ok=False)
    shutil.copytree(os.path.join(root, 'meta'), os.path.join(testroot, 'meta'))
    shutil.copy(os.path.join(root, '_prose.yml'), os.path.join(testroot, '_prose.yml'))

    reset_all_meta(root=testroot)


    with open(os.path.join(testroot, 'meta', '1-2-1.md'), encoding="UTF-8") as stream:
        meta = next(yaml.safe_load_all(stream))
    
    assert meta['indicator'] == '1.2.1'
    assert meta['reporting_status'] == 'notstarted'

    # poor man's teardown
    shutil.rmtree(testroot)
