import pytest
import os
from sdg.schema import get_schema

root = os.path.dirname(os.path.realpath(__file__))

def test_schema():
    """Read the schema file and output"""

    schema = get_schema('_prose.yml', root=root)

    assert schema[0]['name'] == 'title'
