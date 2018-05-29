import pytest
import os
from sdg import check_all_csv

dir_path = os.path.dirname(os.path.realpath(__file__))

def test_out_path():
    """Check that we can check csvs"""
    check_result = check_all_csv(root=os.path.realpath(dir_path))
    assert check_result