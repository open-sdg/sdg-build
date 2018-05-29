import pytest
import os
from sdg import check_all_meta

dir_path = os.path.dirname(os.path.realpath(__file__))

def test_out_path():
    """Check that output_path is as expected"""
    check_result = check_all_meta(root=os.path.realpath(dir_path))
    assert check_result
