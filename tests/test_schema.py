import pytest
import os
from sdg.schema import Schema

src_dir = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def default_schema():
    """Get the standard testing schema from _prose.yml"""
    return Schema(schema_file='_prose.yml', src_dir=src_dir)


def test_init_schema(default_schema):
    """Check schema loaded OK"""

    assert hasattr(default_schema, 'schema')


def test_allowed_values(default_schema):
    """Can we read the allowed values from schema fields"""

    # Check the normal use case
    statuses = default_schema.get_values('reporting_status')
    assert set(statuses) == set(['notstarted', 'inprogress', 'complete'])

    # Check it fails when we ask for a bad field
    with pytest.raises(ValueError):
        statuses = default_schema.get_values('bad_field')

    # Check fails for non-options field
    with pytest.raises(ValueError):
        statuses = default_schema.get_values('title')
