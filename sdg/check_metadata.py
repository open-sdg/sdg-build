"""
This deprecated file is left in for backwards compatibility.

See open_sdg.py for a replacement.
"""

import os
import sdg
import yaml
from sdg.open_sdg import open_sdg_check


def check_all_meta(src_dir='', schema_file='_prose.yml', config='config.yml'):
    """This function is deprecated but left in for backwards compatibility."""

    print('The check_all_meta function is deprecated. Use open_sdg_check instead.')
    return open_sdg_check(src_dir=src_dir, schema_file=schema_file, config=config)
