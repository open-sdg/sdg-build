"""
Historically this library has mainly served to create builds for the Open SDG
platform. Consequently it has functions dedicated to this purpose. While in
theory the library is more general-purpose, it remains primarily used by the
Open SDG platform. So these helper functions are here to provide the
functionality of the following legacy functions that were specific to Open SDG:
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
        Dict of options.
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
                   languages=None, translations=None, map_layers=None,
                   reporting_status_extra_fields=None, config='open_sdg_config.yml'):
    """Read each input file and edge file and write out json.

    Args:
        src_dir: str. Directory root for the project where data and meta data
            folders are
        site_dir: str. Directory to build the site to
        schema_file: str. Location of schema file relative to src_dir
        languages: list. A list of language codes, for translated builds
        translations: list. A list of git repositories to pull translations from
        map_layers: list. A list of dicts describing geojson to process
        reporting_status_extra_fields: list. A list of extra fields to generate
          reporting stats for.
        config: str. Path to a YAML config file that overrides other parameters

    Returns:
        Boolean status of file writes
    """
    if map_layers is None:
        map_layers = []

    status = True

    # Build a dict of options for open_sdg_prep().
    defaults = {
        'src_dir': src_dir,
        'site_dir': site_dir,
        'schema_file': schema_file,
        'languages': languages,
        'translations': translations,
        'map_layers': map_layers,
        'reporting_status_extra_fields': reporting_status_extra_fields
    }
    # Allow for a config file to update these.
    options = open_sdg_config(config, defaults)

    # Prepare the outputs.
    outputs = open_sdg_prep(options)

    for output in outputs:
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
        'site_dir': '_site',
        'schema_file': schema_file,
    }
    # Allow for a config file to update these.
    options = open_sdg_config(config, defaults)

    # Prepare and validate the output.
    outputs = open_sdg_prep(options)

    status = True
    for output in outputs:
        status = status & output.validate()

    return status


def open_sdg_prep(options):
    """Prepare Open SDG output for validation and builds.

    Args:
        options: Dict of options.

    Returns:
        List of the prepared OutputBase objects.
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

    # Indicate any extra fields for the reporting stats, if needed.
    reporting_status_extra_fields = []
    if 'reporting_status_extra_fields' in options:
        reporting_status_extra_fields = options['reporting_status_extra_fields']

    # Create an "output" from these inputs/schema/translations, for Open SDG output.
    opensdg_output = sdg.outputs.OutputOpenSdg(
        inputs=inputs,
        schema=schema,
        output_folder=options['site_dir'],
        translations=all_translations,
        reporting_status_extra_fields=reporting_status_extra_fields)

    outputs = [opensdg_output]

    # If there are any map layers, create some OutputGeoJson objects.
    for map_layer in options['map_layers']:
        geojson_kwargs = {
            'inputs': inputs,
            'schema': schema,
            'output_folder': options['site_dir'],
            'translations': all_translations
        }
        for key in map_layer:
            geojson_kwargs[key] = map_layer[key]
        # If the geojson_file parameter is not remote, make sure it uses src_dir.
        if not geojson_kwargs['geojson_file'].startswith('http'):
            geojson_file = os.path.join(options['src_dir'], geojson_kwargs['geojson_file'])
            geojson_kwargs['geojson_file'] = geojson_file
        # Create the output.
        outputs.append(sdg.outputs.OutputGeoJson(**geojson_kwargs))

    return outputs
