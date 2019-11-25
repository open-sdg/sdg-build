"""
Historically this library has mainly served to create builds for the Open SDG
platform. Consequently it has functions dedicated to this purpose. While in
theory the library is more general-purpose, it remains primarily used by the
Open SDG platform. So these helper functions are here to help the backwards-
compatibility provided by the following files:
* build.py
* check_metadata.py
* check_csv.py
"""

import os
import sdg

def opensdg_prep(src_dir='', site_dir='_site', schema_file='_prose.yml',
                 translation_repo='https://github.com/open-sdg/sdg-translations.git',
                 translation_tag='0.8.1'):
    """Prepare Open SDG output for validation and builds.

    Args:
        src_dir: str. Directory root for the project where data and meta data
            folders are
        site_dir: str. Directory to build the site to
        schema_file: Location of schema file relative to src_dir
        translation_repo: str. A git repository to pull translations from
        translation_tag: str. Tag/branch to use in the translation repo

    Returns:
        The prepared OutputBase object.
    """
    # Input data from CSV files matching this pattern: tests/data/*-*.csv
    data_pattern = os.path.join(src_dir, 'data', '*-*.csv')
    data_input = sdg.inputs.InputCsvData(path_pattern=data_pattern)

    # Input metadata from YAML files matching this pattern: tests/meta/*-*.md
    meta_pattern = os.path.join(src_dir, 'meta', '*-*.md')
    meta_input = sdg.inputs.InputYamlMdMeta(path_pattern=meta_pattern)

    # Combine these inputs into one list.
    inputs = [data_input, meta_input]

    # Use a Prose.io file for the metadata schema.
    schema = sdg.schemas.SchemaInputOpenSdg(schema_path=schema_file)

    # Pull in remote translations if needed.
    translations = []
    if translation_repo:
        translations.append(sdg.translations.TranslationInputSdgTranslations(
            source=translation_repo, tag=translation_tag
        ))
    # Also include local translations from a 'translation' folder if present.
    translation_dir = os.path.join(src_dir, 'translations')
    if os.path.isdir(translation_dir):
        translations.append(sdg.translations.TranslationInputYaml(source=translation_dir))

    # Create an "output" from these inputs/schema/translations, for Open SDG output.
    return sdg.outputs.OutputOpenSdg(
        inputs=inputs,
        schema=schema,
        output_folder=site_dir,
        translations=translations)
