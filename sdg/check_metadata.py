# -*- coding: utf-8 -*-
"""
Created on Thu May  4 13:53:01 2017

@author: dougashton

Updated November 2019: This function serves as a shortcut for validating Open SDG
output from CSV data and YAML input. While this library is theoretically a
general-purpose tool, its main use remains to support Open SDG platform. This
library's API has shifted to an object-oriented approach, and so this function
is being updated accordingly.
"""

from sdg.legacy import opensdg_prep

# %% Read each yaml and run the checks

def check_all_meta(src_dir='', schema_file='_prose.yml', translation_tag='0.8.1',
                   translation_repo='https://github.com/open-sdg/sdg-translations.git'):
    """Run metadata checks for all indicators

    Args:
        src_dir: str. Directory root for the project where data and meta data
            folders are
        schema_file: Location of schema file relative to src_dir
        translation_repo: str. A git repository to pull translations from
        translation_tag: str. Tag/branch to use in the translation repo
    """

    opensdg_output = opensdg_prep(src_dir=src_dir, site_dir='_site',
        schema_file=schema_file, translation_repo=translation_repo,
        translation_tag=translation_tag)

    return opensdg_output.validate()
