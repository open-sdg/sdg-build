import pytest
import os
from sdg import check_all_meta

src_dir = os.path.dirname(os.path.realpath(__file__))

def test_out_path():
    """Check that output_path is as expected"""
    check_result = check_all_meta(src_dir=os.path.realpath(src_dir))
    assert check_result
