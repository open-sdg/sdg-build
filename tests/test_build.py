import pytest
import os
from sdg import build_data

dir_path = os.path.dirname(os.path.realpath(__file__))

def test_build():
    """Check that output_path is as expected"""
    build_result = build_data(root=os.path.realpath(dir_path), git=False)
    assert build_result

    exp_dirs = ['comb', 'data', 'edges', 'headline', 'meta']
    act_dirs = os.listdir(os.path.join(dir_path, '_site'))

    assert all([a == b for a, b in zip(exp_dirs, act_dirs)])
