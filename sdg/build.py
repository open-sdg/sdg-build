"""
Created on Sun May 13 2018

@author: dashton

This is the parent script for building the data outputs. It loads the
raw data from csv and sends it through the various processors to
output the main data, edges, and headline in csv and json format.

Updated November 2019: This function serves as a shortcut for producing Open SDG
output from CSV data and YAML input. While this library is theoretically a
general-purpose tool, its main use remains to support Open SDG platform. This
library's API has shifted to an object-oriented approach, and so this function
is being updated accordingly.
"""

from sdg.legacy import opensdg_prep

# load each csv in and compute derivatives (edges, headline etc)
# hold onto the derivatives
# then write out in the different formats
# write out the "all" files for each derivative

# %% Read each csv and dump out to json and csv


def build_data(src_dir='', site_dir='_site', schema_file='_prose.yml', languages=[],
               translation_repo='https://github.com/open-sdg/sdg-translations.git',
               translation_tag='0.8.1'):
    """Read each input file and edge file and write out json.

    Args:
        src_dir: str. Directory root for the project where data and meta data
            folders are
        site_dir: str. Directory to build the site to
        schema_file: Location of schema file relative to src_dir
        languages: list. A list of language codes, for translated builds
        translation_repo: str. A git repository to pull translations from
        translation_tag: str. Tag/branch to use in the translation repo

    Returns:
        Boolean status of file writes
    """
    status = True

    opensdg_output = opensdg_prep(src_dir=src_dir, site_dir=site_dir,
        schema_file=schema_file, translation_repo=translation_repo,
        translation_tag=translation_tag)

    if languages:
        # If languages were provide, perform a translated build.
        status = status & opensdg_output.execute_per_language(languages)
    else:
        # Otherwise perform an untranslated build.
        status = status & opensdg_output.execute()

    return status
