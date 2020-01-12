"""
This deprecated file is left in for backwards compatibility.

See open_sdg.py for a replacement.
"""

import os
import sdg
import yaml
from sdg.open_sdg import open_sdg_build


def build_data(src_dir='', site_dir='_site', schema_file='_prose.yml',
               languages=None, translations=None, config='open_sdg_config.yml'):
    """The build_data function is deprecated. Use open_sdg_build instead."""

    return open_sdg_build(src_dir=src_dir, site_dir=site_dir,
                          schema_file=schema_file, languages=languages,
                          translations=translations, config=config)
