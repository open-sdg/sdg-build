import pytest
import os
import sdg
from sdg.stats import reporting_status


src_dir = os.path.dirname(os.path.realpath(__file__))

# Get the schema and metadata
schema = sdg.schema.Schema('_prose.yml', src_dir=src_dir)

all_meta = dict()
ids = sdg.path.get_ids(src_dir=src_dir)
for inid in ids:
    meta = sdg.meta.read_meta(
            inid, git=False,
            src_dir=src_dir,
            git_data_dir=None)
    all_meta[inid] = meta


def test_reporting():
    """Reporting Status"""

    rep_stat = reporting_status(schema, all_meta)

    assert set(rep_stat.keys()) == set(['statuses', 'goals', 'overall'])

    assert rep_stat['overall']['totals']['total'] == 15
