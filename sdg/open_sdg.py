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


def open_sdg_config(config_file, defaults):
    """Look for a YAML config file with Open SDG options.

    Args:
        config_file: str. Path to the YAML config file.
        defaults: dict. Set of options to default to.

    Returns:
        Dict of options, or None if no config file is found.
    """
    options = {}
    try:
        with open(config_file) as file:
            options = yaml.load(file, Loader=yaml.FullLoader)
    except:
        pass

    defaults.update(options)
    return defaults


def open_sdg_build(src_dir='', site_dir='_site', schema_file='_prose.yml',
                   languages=None, translations=None, config='open_sdg_config.yml'):
    """Read each input file and edge file and write out json.

    Args:
        src_dir: str. Directory root for the project where data and meta data
            folders are
        site_dir: str. Directory to build the site to
        schema_file: str. Location of schema file relative to src_dir
        languages: list. A list of language codes, for translated builds
        translations: list. A list of git repositories to pull translations from
        config: str. Path to a YAML config file that overrides other parameters

    Returns:
        Boolean status of file writes
    """

    status = True

    # Build a dict of options for open_sdg_prep().
    defaults = {
        'src_dir': src_dir,
        'site_dir': site_dir,
        'schema_file': schema_file,
        'languages': languages,
        'translations': translations
    }
    # Allow for a config file to update these.
    options = open_sdg_config(config, defaults)

    # Prepare the output.
    output = open_sdg_prep(options)

    if options['languages']:
        # If languages were provide, perform a translated build.
        status = status & output.execute_per_language(options['languages'])
    else:
        # Otherwise perform an untranslated build.
        status = status & output.execute()

    return status


def open_sdg_check(src_dir='', schema_file='_prose.yml', config='open_sdg_config.yml'):
    """Run validation checks for all indicators.

    This checks both *.csv (data) and *.md (metadata) files.

    Args:
        src_dir: str. Directory root for the project where data and meta data
            folders are
        schema_file: Location of schema file relative to src_dir
        config: str. Path to a YAML config file that overrides other parameters

    Returns:
        boolean: True if the check was successful, False if not.
    """

    # Build a dict of options for open_sdg_prep().
    defaults = {
        'src_dir': src_dir,
        'schema_file': schema_file,
    }
    # Allow for a config file to update these.
    options = open_sdg_config(config, defaults)

    # Prepare and validate the output.
    output = open_sdg_prep(options)
    return output.validate()


def open_sdg_prep(options):
    """Prepare Open SDG output for validation and builds.

    Args:
        options: Dict of options.

    Returns:
        The prepared OutputBase object.
    """

    # Set defaults for the mutable parameters.
    if 'languages' in options and options['languages'] is None:
        options['languages'] = []
    if 'translations' in options and options['translations'] is None:
        options['translations'] = [
            'https://github.com/open-sdg/translations-un-sdg.git@1.0.0-rc1',
            'https://github.com/open-sdg/translations-open-sdg.git@1.0.0-rc1'
        ]

    # Input data from CSV files matching this pattern: tests/data/*-*.csv
    data_pattern = os.path.join(options['src_dir'], 'data', '*-*.csv')
    data_input = sdg.inputs.InputCsvData(path_pattern=data_pattern)

    # Input metadata from YAML files matching this pattern: tests/meta/*-*.md
    meta_pattern = os.path.join(options['src_dir'], 'meta', '*-*.md')
    meta_input = sdg.inputs.InputYamlMdMeta(path_pattern=meta_pattern)

    # Combine these inputs into one list.
    inputs = [data_input, meta_input]

    # Use a Prose.io file for the metadata schema.
    schema_path = os.path.join(options['src_dir'], options['schema_file'])
    schema = sdg.schemas.SchemaInputOpenSdg(schema_path=schema_path)

    # Pull in remote translations if needed.
    all_translations = []
    if 'translations' in options:
        for repo in options['translations']:
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
    translation_dir = os.path.join(options['src_dir'], 'translations')
    if os.path.isdir(translation_dir):
        all_translations.append(sdg.translations.TranslationInputYaml(source=translation_dir))

    # Create an "output" from these inputs/schema/translations, for Open SDG output.
    return sdg.outputs.OutputOpenSdg(
        inputs=inputs,
        schema=schema,
        output_folder=options['site_dir'],
        translations=all_translations)
