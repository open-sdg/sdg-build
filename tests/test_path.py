import sdg
import pytest
import os
from sdg.path import output_path

def test_out_path():
    """Check that output_path is as expected"""
    out_path = output_path(inid="1-2-1",  ftype='data', format='json')
    assert out_path == os.path.join('_site', 'data', '1-2-1.json')
