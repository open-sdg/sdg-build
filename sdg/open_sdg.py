"""
Historically this library has mainly served to create builds for the Open SDG
platform. Consequently it has functions dedicated to this purpose. While in
theory the library is more general-purpose, it remains primarily used by the
Open SDG platform. So these helper functions are here to provide the
functionality of the following legacy functions:
* build_data
* check_all_csv
* check_all_meta
"""

import os
import sdg
import yaml


def open_sdg_build(src_dir='', site_dir='_site', schema_file='_prose.yml',
                   languages=None, translations=None, config='config.yml'):
    """Read each input file and edge file and write out json.

    Args:
        src_dir: str. Directory root for the project where data and meta data
            folders are
        site_dir: str. Directory to build the site to
        schema_file: str. Location of schema file relative to src_dir
        languages: list. A list of language codes, for translated builds
        translations: list. A list of git repositories to pull translations from
        config: str. Path to a configuration file

    Returns:
        Boolean status of file writes
    """

    status = True

    opensdg_output = open_sdg_prep(src_dir=src_dir, site_dir=site_dir,
        schema_file=schema_file, translations=translations, config=config)

    if languages:
        # If languages were provide, perform a translated build.
        status = status & opensdg_output.execute_per_language(languages)
    else:
        # Otherwise perform an untranslated build.
        status = status & opensdg_output.execute()

    return status


def open_sdg_check(src_dir='', schema_file='_prose.yml', config='config.yml'):
    """Run validation checks for all indicators.

    This checks both *.csv (data) and *.md (metadata) files.

    Args:
        src_dir: str. Directory root for the project where data and meta data
            folders are
        schema_file: Location of schema file relative to src_dir
        config: str. Location of config file relative to src_dir
    """

    opensdg_output = open_sdg_prep(src_dir=src_dir, site_dir='_site',
        schema_file=schema_file, config=config)

    return opensdg_output.validate()


def open_sdg_prep(src_dir='', site_dir='_site', schema_file='_prose.yml',
                 translations=None, languages=None, config='config.yml'):
    """Prepare Open SDG output for validation and builds.

    Args:
        src_dir: str. Directory root for the project where data and meta data
            folders are
        site_dir: str. Directory to build the site to
        schema_file: str. Location of schema file relative to src_dir
        languages: list. A list of language codes, for translated builds
        translations: list. A list of git repositories to pull translations from
        config: str. Location of config file relative to src_dir

    Returns:
        The prepared OutputBase object.
    """

    # Load parameters from a config file if present.
    config_path = os.path.join(src_dir, config)
    try:
        with open(config_path) as file:
            options = yaml.load(file, Loader=yaml.FullLoader)
            src_dir = options['source directory'] if 'source directory' in options else src_dir
            site_dir = options['destination directory'] if 'destination directory' in options else site_dir
            schema_file = options['schema file'] if 'schema file' in options else schema_file
            languages = options['languages'] if 'languages' in options else languages
            translations = options['translations'] if 'translations' in options else translations
    except:
        pass

    # Set defaults for the mutable parameters.
    if languages is None:
        languages = []
    if translations is None:
        translations = [
            'https://github.com/open-sdg/translations-un-sdg.git@1.0.0-rc1',
            'https://github.com/open-sdg/translations-open-sdg.git@1.0.0-rc1'
        ]

    # Input data from CSV files matching this pattern: tests/data/*-*.csv
    data_pattern = os.path.join(src_dir, 'data', '*-*.csv')
    data_input = sdg.inputs.InputCsvData(path_pattern=data_pattern)

    # Input metadata from YAML files matching this pattern: tests/meta/*-*.md
    meta_pattern = os.path.join(src_dir, 'meta', '*-*.md')
    meta_input = sdg.inputs.InputYamlMdMeta(path_pattern=meta_pattern)

    # Combine these inputs into one list.
    inputs = [data_input, meta_input]

    # Use a Prose.io file for the metadata schema.
    schema_path = os.path.join(src_dir, schema_file)
    schema = sdg.schemas.SchemaInputOpenSdg(schema_path=schema_path)

    # Pull in remote translations if needed.
    all_translations = []
    if translations:
        for repo in translations:
            # Support an "@" syntax for pinning to a git tag/branch/commit.
            parts = repo.split('@')
            tag = None
            if len(parts) == 2:
                repo = parts[0]
                tag = parts[1]
            all_translations.append(sdg.translations.TranslationInputSdgTranslations(
                source=repo, tag=tag
            ))
    # Also include local translations from a 'translation' folder if present.
    translation_dir = os.path.join(src_dir, 'translations')
    if os.path.isdir(translation_dir):
        all_translations.append(sdg.translations.TranslationInputYaml(source=translation_dir))

    # Create an "output" from these inputs/schema/translations, for Open SDG output.
    return sdg.outputs.OutputOpenSdg(
        inputs=inputs,
        schema=schema,
        output_folder=site_dir,
        translations=all_translations)
