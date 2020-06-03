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
import inspect
import importlib
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
    except FileNotFoundError:
        print('Config file not found, using defaults.')
        pass

    defaults.update(options)
    return defaults


def open_sdg_build(src_dir='', site_dir='_site', schema_file='_prose.yml',
                   languages=None, translations=None, map_layers=None,
                   reporting_status_extra_fields=None, config='open_sdg_config.yml',
                   inputs=None, alter_data=None, alter_meta=None,
                   docs_branding='Build docs', docs_intro=''):
    """Read each input file and edge file and write out json.

    Args:
        Each argument is optional. The defaults above will be used if omitted.

        src_dir: str. Directory root for the project where data and meta data
            folders are
        site_dir: str. Directory to build the site to
        schema_file: str. Location of schema file relative to src_dir
        languages: list. A list of language codes, for translated builds
        translations: list. A list of dicts describing instances of TranslationInputBase
        map_layers: list. A list of dicts describing geojson to process
        reporting_status_extra_fields: list. A list of extra fields to generate
          reporting stats for.
        config: str. Path to a YAML config file that overrides other parameters
        inputs: list. A list of dicts describing instances of InputBase
        alter_data: function. A callback function that alters a data Dataframe
        alter_meta: function. A callback function that alters a metadata dictionary
        docs_branding: string. A heading for all documentation pages
        docs_intro: string. An introduction for the documentation homepage

    Returns:
        Boolean status of file writes
    """
    if map_layers is None:
        map_layers = []
    if inputs is None:
        inputs = open_sdg_input_defaults()
    if translations is None:
        translations = open_sdg_translation_defaults()

    status = True

    # Build a dict of options for open_sdg_prep().
    defaults = {
        'src_dir': src_dir,
        'site_dir': site_dir,
        'schema_file': schema_file,
        'languages': languages,
        'translations': translations,
        'map_layers': map_layers,
        'reporting_status_extra_fields': reporting_status_extra_fields,
        'inputs': inputs,
        'docs_branding': docs_branding,
        'docs_intro': docs_intro,
    }
    # Allow for a config file to update these.
    options = open_sdg_config(config, defaults)

    # Pass along our data/meta alterations.
    options['alter_data'] = alter_data
    options['alter_meta'] = alter_meta

    # Prepare the outputs.
    outputs = open_sdg_prep(options)

    for output in outputs:
        if options['languages']:
            # If languages were provide, perform a translated build.
            status = status & output.execute_per_language(options['languages'])
        else:
            # Otherwise perform an untranslated build.
            status = status & output.execute()

    # Output the documentation pages.
    documentation_service = sdg.OutputDocumentationService(outputs,
        folder=options['site_dir'],
        branding=options['docs_branding'],
        intro=options['docs_intro'],
        languages=options['languages']
    )
    documentation_service.generate_documentation()

    return status


def open_sdg_check(src_dir='', schema_file='_prose.yml', config='open_sdg_config.yml',
        inputs=None, alter_data=None, alter_meta=None):
    """Run validation checks for all indicators.

    This checks both *.csv (data) and *.md (metadata) files.

    Args:
        Each argument is optional. The defaults above will be used if omitted.

        src_dir: str. Directory root for the project where data and meta data
            folders are
        schema_file: Location of schema file relative to src_dir
        config: str. Path to a YAML config file that overrides other parameters
        alter_data: function. A callback function that alters a data Dataframe
        alter_meta: function. A callback function that alters a metadata dictionary

    Returns:
        boolean: True if the check was successful, False if not.
    """
    if inputs is None:
        inputs = open_sdg_input_defaults()

    # Build a dict of options for open_sdg_prep().
    defaults = {
        'src_dir': src_dir,
        'site_dir': '_site',
        'schema_file': schema_file,
        'map_layers': [],
        'inputs': inputs,
        'translations': []
    }
    # Allow for a config file to update these.
    options = open_sdg_config(config, defaults)

    # Pass along our data/meta alterations.
    options['alter_data'] = alter_data
    options['alter_meta'] = alter_meta

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

    # Combine the inputs into one list.
    inputs = [open_sdg_input_from_dict(input_dict, options) for input_dict in options['inputs']]

    # Do any data/metadata alterations.
    if callable(options['alter_data']):
        for input in inputs:
            input.add_data_alteration(options['alter_data'])
    if callable(options['alter_meta']):
        for input in inputs:
            input.add_meta_alteration(options['alter_meta'])

    # Use a Prose.io file for the metadata schema.
    schema_path = os.path.join(options['src_dir'], options['schema_file'])
    schema = sdg.schemas.SchemaInputOpenSdg(schema_path=schema_path)

    # Pull in remote translations if needed.
    translations = [open_sdg_translation_from_dict(t_dict, options) for t_dict in options['translations']]

    # Indicate any extra fields for the reporting stats, if needed.
    reporting_status_extra_fields = []
    if 'reporting_status_extra_fields' in options:
        reporting_status_extra_fields = options['reporting_status_extra_fields']

    # Create an "output" from these inputs/schema/translations, for Open SDG output.
    opensdg_output = sdg.outputs.OutputOpenSdg(
        inputs=inputs,
        schema=schema,
        output_folder=options['site_dir'],
        translations=translations,
        reporting_status_extra_fields=reporting_status_extra_fields)

    outputs = [opensdg_output]

    # If there are any map layers, create some OutputGeoJson objects.
    for map_layer in options['map_layers']:
        geojson_kwargs = {
            'inputs': inputs,
            'schema': schema,
            'output_folder': options['site_dir'],
            'translations': translations
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


def open_sdg_input_defaults():
    return [
        {
            'class': 'InputCsvData',
            'path_pattern': os.path.join('data', '*-*.csv')
        },
        {
            'class': 'InputYamlMdMeta',
            'path_pattern': os.path.join('meta', '*-*.md'),
            'git': True,
            'git_data_dir': None,
        }
    ]


def open_sdg_input_from_dict(params, options):
    if 'class' not in params:
        raise KeyError("Each 'input' must have a 'class'.")
    input_class = params['class']

    allowed = [
        'InputCkan',
        'InputCsvData',
        'InputCsvMeta',
        'InputSdmxJson',
        'InputSdmxMl_Structure',
        'InputSdmxMl_StructureSpecific',
        'InputYamlMdMeta',
        'InputSdmxMl_Multiple',
        'InputExcelMeta',
    ]
    if input_class not in allowed:
        raise KeyError("Input class '%s' is not one of: %s." % (input_class, ', '.join(allowed)))

    # We no longer need the "class" param.
    del params['class']

    # For "path_pattern" we need to prepend our src_dir.
    if 'path_pattern' in params:
        params['path_pattern'] = os.path.join(options['src_dir'], params['path_pattern'])

    input_instance = None
    if input_class == 'InputCkan':
        input_instance = sdg.inputs.InputCkan(**params)
    elif input_class == 'InputCsvData':
        input_instance = sdg.inputs.InputCsvData(**params)
    elif input_class == 'InputCsvMeta':
        input_instance = sdg.inputs.InputCsvMeta(**params)
    elif input_class == 'InputSdmxJson':
        input_instance = sdg.inputs.InputSdmxJson(**params)
    elif input_class == 'InputSdmxMl_Structure':
        input_instance = sdg.inputs.InputSdmxMl_Structure(**params)
    elif input_class == 'InputSdmxMl_StructureSpecific':
        input_instance = sdg.inputs.InputSdmxMl_StructureSpecific(**params)
    elif input_class == 'InputYamlMdMeta':
        input_instance = sdg.inputs.InputYamlMdMeta(**params)
    elif input_class == 'InputSdmxMl_Multiple':
        input_instance = sdg.inputs.InputSdmxMl_Multiple(**params)
    elif input_class == 'InputExcelMeta':
        input_instance = sdg.inputs.InputExcelMeta(**params)

    return input_instance


def open_sdg_translation_defaults():
    return [
        {
            'class': 'TranslationInputSdgTranslations',
            'source': 'https://github.com/open-sdg/sdg-translations.git',
            'tag': 'master',
        },
        {
            'class': 'TranslationInputYaml',
            'source': 'translations',
        }
    ]


def open_sdg_translation_from_dict(params, options):

    if 'class' not in params:
        raise KeyError("Each 'translation' must have a 'class'.")
    translation_class = params['class']

    allowed = [
        'TranslationInputCsv',
        'TranslationInputSdgTranslations',
        'TranslationInputSdmx',
        'TranslationInputYaml',
    ]
    if translation_class not in allowed:
        raise KeyError("Translation class '%s' is not one of: %s." % (translation_class, ', '.join(allowed)))

    # We no longer need the "class" param.
    del params['class']

    # For "source" in TranslationInputYaml/Csv we need to prepend our src_dir.
    if translation_class == 'TranslationInputCsv' or translation_class == 'TranslationInputYaml':
        if 'source' in params:
            params['source'] = os.path.join(options['src_dir'], params['source'])

    translation_instance = None
    if translation_class == 'TranslationInputCsv':
        translation_instance = sdg.translations.TranslationInputCsv(**params)
    elif translation_class == 'TranslationInputSdgTranslations':
        translation_instance = sdg.translations.TranslationInputSdgTranslations(**params)
    elif translation_class == 'TranslationInputSdmx':
        translation_instance = sdg.translations.TranslationInputSdmx(**params)
    elif translation_class == 'TranslationInputYaml':
        translation_instance = sdg.translations.TranslationInputYaml(**params)

    return translation_instance
