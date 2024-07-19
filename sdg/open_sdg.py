"""
Historically this library has mainly served to create builds for the Open SDG
platform. Consequently it has functions dedicated to this purpose. While in
theory the library is more general-purpose, it remains primarily used by the
Open SDG platform. So these helper functions are here to provide the
functionality for easy use with Open SDG.
"""

import os
import sys
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
                   schema=None, languages=None, translations=None, map_layers=None,
                   reporting_status_extra_fields=None, config='open_sdg_config.yml',
                   inputs=None, alter_data=None, alter_meta=None, indicator_options=None,
                   docs_branding='Build docs', docs_intro='', docs_indicator_url=None,
                   docs_subfolder=None, indicator_downloads=None, docs_baseurl='',
                   docs_extra_disaggregations=None, docs_translate_disaggregations=False,
                   logging=None, indicator_export_filename='all_indicators',
                   datapackage=None, csvw=None, data_schema=None, docs_metadata_fields=None,
                   alter_indicator=None, indicator_callback=None,
                   ignore_out_of_scope_disaggregation_stats=False):
    """Read each input file and edge file and write out json.

    Args:
        Each argument is optional. The defaults above will be used if omitted.

        src_dir: str. Directory root for the project where data and meta data
            folders are
        site_dir: str. Directory to build the site to
        schema_file: str. Location of schema file relative to src_dir (@deprecated)
        schema: list. A list of SchemaInputBase descendants.
        languages: list. A list of language codes, for translated builds
        translations: list. A list of dicts describing instances of TranslationInputBase
        map_layers: list. A list of dicts describing geojson to process
        reporting_status_extra_fields: list. A list of extra fields to generate
          reporting stats for.
        config: str. Path to a YAML config file that overrides other parameters
        inputs: list. A list of dicts describing instances of InputBase
        alter_data: function. A callback function that alters a data Dataframe (for each input)
        alter_meta: function. A callback function that alters a metadata dictionary (for each input)
        alter_indicator: function. A callback function that alters the full Indicator objects (for each output)
        indicator_callback: function. A callback function that runs for each
          indicator after the outputs have already been generated.
        indicator_options: Dict. Options to pass into each indicator.
        docs_branding: string. A heading for all documentation pages
        docs_intro: string. An introduction for the documentation homepage
        docs_indicator_url: string. A pattern for indicator URLs on the site repo
        docs_subfolder: string. A subfolder in which to put the documentation pages
        docs_baseurl: string. A baseurl to put at the beginning of all absolute links
        indicator_downloads: list. A list of dicts describing calls to the
            write_downloads() method of IndicatorDownloadService
        docs_extra_disaggregations: list. An optional list of extra columns
            that would not otherwise be included in the disaggregation report
        docs_translate_disaggregations: boolean. Whether to provide translated columns
            in the disaggregation report
        datapackage: dict. Dict describing an instance of OutputDataPackage
        csvw: dict. Dict describing an instance of OutputCsvw
        data_schema: Dict describing an instance of DataSchemaInputBase subclass
        logging : list or None. The types of logs to print, including 'warn' and 'debug'.
        indicator_export_filename: string. Filename without extension for zip file
        docs_metadata_fields: list. List of dicts describing metadata fields for
            the MetadataReportService class.
        ignore_out_of_scope_disaggregation_stats: boolean. Whether to omit the
            not-applicable disaggregation stats.

    Returns:
        Boolean status of file writes
    """
    if map_layers is None:
        map_layers = []
    if inputs is None:
        inputs = open_sdg_input_defaults()
    if translations is None:
        translations = open_sdg_translation_defaults()
    if indicator_options is None:
        indicator_options = open_sdg_indicator_options_defaults()
    if logging is None:
        logging = ['warn']
    if docs_metadata_fields is None:
        docs_metadata_fields = []

    status = True

    # Build a dict of options for open_sdg_prep().
    defaults = {
        'src_dir': src_dir,
        'site_dir': site_dir,
        'schema_file': schema_file,
        'languages': languages,
        'translations': translations,
        'schema': schema,
        'map_layers': map_layers,
        'reporting_status_extra_fields': reporting_status_extra_fields,
        'inputs': inputs,
        'docs_branding': docs_branding,
        'docs_intro': docs_intro,
        'docs_indicator_url': docs_indicator_url,
        'docs_subfolder': docs_subfolder,
        'docs_baseurl': docs_baseurl,
        'docs_translate_disaggregations': docs_translate_disaggregations,
        'indicator_options': indicator_options,
        'indicator_downloads': indicator_downloads,
        'docs_extra_disaggregations': docs_extra_disaggregations,
        'datapackage': datapackage,
        'csvw': csvw,
        'data_schema': data_schema,
        'logging': logging,
        'indicator_export_filename': indicator_export_filename,
        'docs_metadata_fields': docs_metadata_fields,
        'ignore_out_of_scope_disaggregation_stats': ignore_out_of_scope_disaggregation_stats,
    }
    # Allow for a config file to update these.
    options = open_sdg_config(config, defaults)

    if options['schema'] is None:
        options['schema'] = open_sdg_schema_defaults(options['schema_file'])

    # Convert the translations and schemas.
    options['translations'] = open_sdg_translations_from_options(options)
    options['schema'] = open_sdg_schema_from_options(options)

    # Pass along our data/meta alterations.
    options['alter_data'] = alter_data
    options['alter_meta'] = alter_meta
    # And other callbacks.
    options['indicator_callback'] = indicator_callback
    options['alter_indicator'] = alter_indicator

    # Convert the indicator options.
    options['indicator_options'] = open_sdg_indicator_options_from_dict(options['indicator_options'])

    # Prepare the outputs.
    outputs = open_sdg_prep(options)

    for output in outputs:
        if options['languages']:
            status = status & output.execute_per_language(options['languages'])
            status = status & output.execute('untranslated')
        else:
            sys.exit('The data configuration must have a "languages" setting with at least one language. See the documentation here: https://open-sdg.readthedocs.io/en/latest/data-configuration/#languages')

    # Perform per-indicator callbacks.
    if callable(options['indicator_callback']):
        indicator_callback = options['indicator_callback']
        for output in outputs:
            if isinstance(output, sdg.outputs.OutputOpenSdg):
                for indicator in output.indicators.values():
                    indicator_callback(indicator)

    # Output the documentation pages.
    documentation_service = sdg.OutputDocumentationService(outputs,
        folder=options['site_dir'],
        subfolder=options['docs_subfolder'],
        branding=options['docs_branding'],
        intro=options['docs_intro'],
        languages=options['languages'],
        translations=options['translations'],
        indicator_url=options['docs_indicator_url'],
        baseurl=options['docs_baseurl'],
        extra_disaggregations=options['docs_extra_disaggregations'],
        translate_disaggregations=options['docs_translate_disaggregations'],
        logging=logging,
        metadata_fields=options['docs_metadata_fields'],
    )
    documentation_service.generate_documentation()

    return status


def open_sdg_indicator_options_defaults():
    return {
        'non_disaggregation_columns': [
            'Year',
            'Units',
            'Series',
            'Value',
            'GeoCode',
            'Observation status',
            'Unit multiplier',
            'Unit measure',
             # Support common SDMX codes.
            'UNIT_MEASURE',
            'SERIES',
            'COMMENT_TS',
            'DATA_LAST_UPDATE',
        ],
        'observation_attributes': [
            'COMMENT_OBS',
            'SOURCE_DETAIL',
        ],
        'series_column': 'Series',
        'unit_column': 'Units',
    }


def open_sdg_indicator_options_from_dict(options):
    options_obj = sdg.IndicatorOptions()
    if 'non_disaggregation_columns' in options:
        for column in options['non_disaggregation_columns']:
            options_obj.add_non_disaggregation_columns(column)
    if 'observation_attributes' in options:
        for column in options['observation_attributes']:
            options_obj.add_observation_attribute(column)
    if 'series_column' in options:
        options_obj.set_series_column(options['series_column'])
    if 'unit_column' in options:
        options_obj.set_unit_column(options['unit_column'])
    return options_obj


def open_sdg_check(src_dir='', schema_file='_prose.yml', config='open_sdg_config.yml',
        inputs=None, alter_data=None, alter_meta=None, indicator_options=None,
        data_schema=None, schema=None, logging=None, alter_indicator=None):
    """Run validation checks for all indicators.

    This checks both *.csv (data) and *.md (metadata) files.

    Args:
        Each argument is optional. The defaults above will be used if omitted.

        src_dir: str. Directory root for the project where data and meta data
            folders are
        schema_file: Location of schema file relative to src_dir (@deprecated)
        schema: list. List of SchemaInputBase descendants.
        config: str. Path to a YAML config file that overrides other parameters
        alter_data: function. A callback function that alters a data Dataframe (for each input)
        alter_meta: function. A callback function that alters a metadata dictionary (for each input)
        alter_indicator: function. A callback function that alters the full Indicator objects (for each output)
        data_schema: dict . Dict describing an instance of DataSchemaInputBase
        logging: Noneor list. Type of logs to print, including 'warn' and 'debug'

    Returns:
        boolean: True if the check was successful, False if not.
    """
    if inputs is None:
        inputs = open_sdg_input_defaults()
    if indicator_options is None:
        indicator_options = open_sdg_indicator_options_defaults()
    if logging is None:
        logging = ['warn']

    # Build a dict of options for open_sdg_prep().
    defaults = {
        'src_dir': src_dir,
        'site_dir': '_site',
        'schema_file': schema_file,
        'schema': schema,
        'map_layers': [],
        'inputs': inputs,
        'translations': [],
        'indicator_options': indicator_options,
        'indicator_downloads': None,
        'datapackage': None,
        'csvw': None,
        'data_schema': data_schema,
        'logging': logging,
        'indicator_export_filename': None,
        'ignore_out_of_scope_disaggregation_stats': False,
    }
    # Allow for a config file to update these.
    options = open_sdg_config(config, defaults)

    if options['schema'] is None:
        options['schema'] = open_sdg_schema_defaults(options['schema_file'])

    # Convert the translations.
    options['translations'] = open_sdg_translations_from_options(options)
    options['schema'] = open_sdg_schema_from_options(options)

    # Pass along our data/meta alterations.
    options['alter_data'] = alter_data
    options['alter_meta'] = alter_meta
    options['alter_indicator'] = alter_indicator

    # Convert the indicator options.
    options['indicator_options'] = open_sdg_indicator_options_from_dict(options['indicator_options'])

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

    # Use the specified metadata schema.
    schema = options['schema']

    # Indicate any extra fields for the reporting stats, if needed.
    reporting_status_extra_fields = []
    if 'reporting_status_extra_fields' in options:
        reporting_status_extra_fields = options['reporting_status_extra_fields']

    # Create an "output" from these inputs/schema/translations, for Open SDG output.
    opensdg_output = sdg.outputs.OutputOpenSdg(
        inputs=inputs,
        schema=schema,
        output_folder=options['site_dir'],
        translations=options['translations'],
        reporting_status_extra_fields=reporting_status_extra_fields,
        indicator_options=options['indicator_options'],
        indicator_downloads=options['indicator_downloads'],
        logging=options['logging'],
        indicator_export_filename=options['indicator_export_filename'],
        ignore_out_of_scope_disaggregation_stats=options['ignore_out_of_scope_disaggregation_stats'],
    )

    if callable(options['alter_indicator']):
        opensdg_output.add_indicator_alteration(options['alter_indicator'])

    outputs = [opensdg_output]

    # If there are any map layers, create some OutputGeoJsonOpenSdg objects.
    for map_layer in options['map_layers']:
        geojson_kwargs = {
            'inputs': inputs,
            'schema': schema,
            'output_folder': options['site_dir'],
            'translations': options['translations'],
            'indicator_options': options['indicator_options'],
            'logging': options['logging'],
        }
        for key in map_layer:
            geojson_kwargs[key] = map_layer[key]
        # If the geojson_file parameter is not remote, make sure it uses src_dir.
        if not geojson_kwargs['geojson_file'].startswith('http'):
            geojson_file = os.path.join(options['src_dir'], geojson_kwargs['geojson_file'])
            geojson_kwargs['geojson_file'] = geojson_file
        # Create the output.
        geojson_output = sdg.outputs.OutputGeoJsonOpenSdg(**geojson_kwargs)
        if callable(options['alter_indicator']):
            geojson_output.add_indicator_alteration(options['alter_indicator'])
        outputs.append(geojson_output)

    data_schema = None
    if options['data_schema'] is not None:
        data_schema = open_sdg_data_schema_from_dict(options['data_schema'], options)

    # Output datapackages and possible CSVW.
    datapackage_params = options['datapackage'] if options['datapackage'] is not None else {}
    datapackage_output = sdg.outputs.OutputDataPackage(
        inputs=inputs,
        schema=schema,
        output_folder=options['site_dir'],
        translations=options['translations'],
        indicator_options=options['indicator_options'],
        data_schema=data_schema,
        logging=options['logging'],
        **datapackage_params,
    )
    if callable(options['alter_indicator']):
        datapackage_output.add_indicator_alteration(options['alter_indicator'])
    outputs.append(datapackage_output)

    # Optionally output CSVW.
    if options['csvw'] is not None:
        csvw_params = options['csvw'] if options['csvw'] != True else {}
        csvw_output = sdg.outputs.OutputCsvw(
            inputs=inputs,
            schema=schema,
            output_folder=options['site_dir'],
            translations=options['translations'],
            indicator_options=options['indicator_options'],
            data_schema=data_schema,
            logging=options['logging'],
            **csvw_params,
        )
        if callable(options['alter_indicator']):
            csvw_output.add_indicator_alteration(options['alter_indicator'])
        outputs.append(csvw_output)

    # Add SDMX output if configured.
    if 'sdmx_output' in options and 'dsd' in options['sdmx_output']:
        if 'structure_specific' not in options['sdmx_output']:
            options['sdmx_output']['structure_specific'] = True
        sdmx_output = sdg.outputs.OutputSdmxMl(
            inputs=inputs,
            schema=schema,
            output_folder=options['site_dir'],
            translations=options['translations'],
            indicator_options=options['indicator_options'],
            logging=options['logging'],
            **options['sdmx_output']
        )
        if callable(options['alter_indicator']):
            sdmx_output.add_indicator_alteration(options['alter_indicator'])
        outputs.append(sdmx_output)

    # Add Global SDMX output separately, if configured.
    if 'sdmx_output_global' in options:
        params = options['sdmx_output_global']
        if type(params) is not dict:
            params = {}
        # Hardcode some options for global output.
        params['inputs'] = inputs
        params['schema'] = schema
        params['output_folder'] = options['site_dir']
        params['output_subfolder'] = 'sdmx-global'
        params['translations'] = options['translations']
        params['indicator_options'] = options['indicator_options']
        params['logging'] = options['logging']
        params['dsd'] = sdg.helpers.sdmx.get_dsd_url()
        params['msd'] = None
        params['structure_specific'] = True
        params['constrain_data'] = True
        params['constrain_meta'] = True
        params['global_content_constraints'] = True
        global_sdmx_output = sdg.outputs.OutputSdmxMl(**params)
        if callable(options['alter_indicator']):
            global_sdmx_output.add_indicator_alteration(options['alter_indicator'])
        outputs.append(global_sdmx_output)

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
            'git_data_dir': 'data',
        }
    ]


def open_sdg_data_schema_from_dict(params, options):
    if 'class' not in params:
        # Default to a table schema YAML input.
        params['class'] = 'DataSchemaInputTableSchemaYaml'
    data_schema_class = params['class']

    allowed = [
        'DataSchemaInputTableSchemaYaml',
        'DataSchemaInputSdmxDsd',
    ]
    if data_schema_class not in allowed:
        raise KeyError("Data schema class '%s' is not one of: %s." % (data_schema_class, ', '.join(allowed)))

    # We no longer need the "class" param.
    del params['class']

    # If using a local "source" we need to prepend our src_dir.
    if 'source' in params and isinstance(params['source'], str) and not params['source'].startswith('http'):
        params['source'] = os.path.join(options['src_dir'], params['source'])

    data_schema_instance = None
    if data_schema_class == 'DataSchemaInputTableSchemaYaml':
        data_schema_instance = sdg.data_schemas.DataSchemaInputTableSchemaYaml(**params)
    elif data_schema_class == 'DataSchemaInputSdmxDsd':
        data_schema_instance = sdg.data_schemas.DataSchemaInputSdmxDsd(**params)

    return data_schema_instance


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
        'InputSdmxMl_UnitedNationsApi',
        'InputYamlMdMeta',
        'InputSdmxMl_Multiple',
        'InputExcelMeta',
        'InputYamlMeta',
        'InputSdmxMeta',
        'InputJsonStat',
        'InputPxWebApi',
        'InputWordMeta',
        'InputSdgMetadata',
    ]
    if input_class not in allowed:
        raise KeyError("Input class '%s' is not one of: %s." % (input_class, ', '.join(allowed)))

    # We no longer need the "class" param.
    del params['class']

    # For "path_pattern" we need to prepend our src_dir.
    if 'path_pattern' in params:
        params['path_pattern'] = os.path.join(options['src_dir'], params['path_pattern'])

    params['logging'] = options['logging']

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
    elif input_class == 'InputSdmxMl_UnitedNationsApi':
        input_instance = sdg.inputs.InputSdmxMl_UnitedNationsApi(**params)
    elif input_class == 'InputYamlMdMeta':
        input_instance = sdg.inputs.InputYamlMdMeta(**params)
    elif input_class == 'InputSdmxMl_Multiple':
        input_instance = sdg.inputs.InputSdmxMl_Multiple(**params)
    elif input_class == 'InputExcelMeta':
        input_instance = sdg.inputs.InputExcelMeta(**params)
    elif input_class == 'InputYamlMeta':
        input_instance = sdg.inputs.InputYamlMeta(**params)
    elif input_class == 'InputSdmxMeta':
        input_instance = sdg.inputs.InputSdmxMeta(**params)
    elif input_class == 'InputJsonStat':
        input_instance = sdg.inputs.InputJsonStat(**params)
    elif input_class == 'InputPxWebApi':
        input_instance = sdg.inputs.InputPxWebApi(**params)
    elif input_class == 'InputWordMeta':
        input_instance = sdg.inputs.InputWordMeta(**params)
    elif input_class == 'InputSdgMetadata':
        input_instance = sdg.inputs.InputSdgMetadata(**params)

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


def open_sdg_translations_from_options(options):
    return [open_sdg_translation_from_dict(t_dict, options) for t_dict in options['translations']]


def open_sdg_translation_from_dict(params, options):

    if 'class' not in params:
        raise KeyError("Each 'translation' must have a 'class'.")
    translation_class = params['class']

    allowed = [
        'TranslationInputCsv',
        'TranslationInputSdgTranslations',
        'TranslationInputSdmx',
        'TranslationInputSdmxMsd',
        'TranslationInputYaml',
    ]
    if translation_class not in allowed:
        raise KeyError("Translation class '%s' is not one of: %s." % (translation_class, ', '.join(allowed)))

    # We no longer need the "class" param.
    del params['class']

    params['logging'] = options['logging']

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
    elif translation_class == 'TranslationInputSdmxMsd':
        translation_instance = sdg.translations.TranslationInputSdmxMsd(**params)
    elif translation_class == 'TranslationInputYaml':
        translation_instance = sdg.translations.TranslationInputYaml(**params)

    return translation_instance


def open_sdg_schema_defaults(schema_file='_prose.yml'):
    return [
        {
            'class': 'SchemaInputOpenSdg',
            'schema_path': schema_file,
        }
    ]


def open_sdg_schema_from_options(options):
    schema = [open_sdg_schema_from_dict(s_dict, options) for s_dict in options['schema']]
    return sdg.schemas.SchemaInputMultiple(schema)


def open_sdg_schema_from_dict(params, options):

    if 'class' not in params:
        raise KeyError("Each 'schema' must have a 'class'.")
    schema_class = params['class']

    allowed = [
        'SchemaInputOpenSdg',
        'SchemaInputSdmxMsd',
    ]
    if schema_class not in allowed:
        raise KeyError("Schema class '%s' is not one of: %s." % (schema_class, ', '.join(allowed)))

    # We no longer need the "class" param.
    del params['class']

    # For "schema_path" we need to prepend our src_dir.
    if 'schema_path' in params and not params['schema_path'].startswith('http'):
        params['schema_path'] = os.path.join(options['src_dir'], params['schema_path'])

    schema_instance = None
    if schema_class == 'SchemaInputOpenSdg':
        schema_instance = sdg.schemas.SchemaInputOpenSdg(**params)
    elif schema_class == 'SchemaInputSdmxMsd':
        schema_instance = sdg.schemas.SchemaInputSdmxMsd(**params)

    return schema_instance
