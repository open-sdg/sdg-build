import pytest
import os
from sdg.schema import Schema

src_dir = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def default_schema():
    """Get the standard testing schema from _prose.yml"""
    return Schema(schema_file='_prose.yml', src_dir=src_dir)

@pytest.fixture
def old_schema():
    """Get the standard testing schema from _prose.yml"""
    return Schema(schema_file='_prose-old.yml', src_dir=src_dir)



def test_init_schema(default_schema):
    """Check schema loaded OK"""

    assert hasattr(default_schema, 'schema')
    assert hasattr(default_schema, 'schema_defaults')


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

def test_load_defaults(default_schema):
    """Check we read in defaults"""
    
    schema_defaults = default_schema.get_defaults()
    
    test_option = schema_defaults['reporting_status']['options'][0]
    
    assert test_option['value']== 'complete'


def test_merge_translations(old_schema):
    """Check we can add translations with an old style schema"""
    
    rep_opts = old_schema.get('reporting_status').get('options')
    
    assert rep_opts[1]['translation_key'] == 'status.statistics_in_progress'
