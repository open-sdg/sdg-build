import pytest
import os
from sdg import build_data
from sdg.path import output_path
import json
import shutil

root = os.path.dirname(os.path.realpath(__file__))

def test_build():
    """Check that output_path is as expected"""

    _site = os.path.join(root, '_site')

    build_result = build_data(root=root, git=False)
    assert build_result

    exp_dirs = set(['comb', 'data', 'edges', 'headline', 'meta'])
    act_dirs = os.listdir(_site)

    assert all([a in exp_dirs for a in act_dirs])

    meta9 = json.load(open(output_path('9-3-1', ftype='meta', format='json', root=root)))
    assert meta9['indicator'] == '9.3.1'

    # poor man's teardown
    shutil.rmtree(_site)
