import sdg
import pytest
import os
from sdg.path import output_path, input_path

def test_out_path():
    """Check that output_path is as expected"""
    out_path = output_path(inid="1-2-1",  ftype='data', format='json', site_dir='_site')
    assert out_path == os.path.join('_site', 'data', '1-2-1.json')

def test_in_path():
    """Check input path as expected"""
    in_path = input_path(inid="1-2-1", ftype='meta', src_dir = '')
    assert in_path == os.path.join('meta','1-2-1.md')
