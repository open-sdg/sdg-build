"""
This is an example of converting CSV data and YAML metadata into the GeoJSON
output suitable for use on a regional map.
"""

import os
import sdg

# Input data from CSV files matching this pattern: tests/data/*-*.csv
data_pattern = os.path.join('tests', 'data', '*-*.csv')
data_input = sdg.inputs.InputCsvData(path_pattern=data_pattern)

# Input metadata from YAML files matching this pattern: tests/meta/*-*.md
meta_pattern = os.path.join('tests', 'meta', '*-*.md')
meta_input = sdg.inputs.InputYamlMdMeta(path_pattern=meta_pattern)

# Combine these inputs into one list.
inputs = [data_input, meta_input]

# Use a Prose.io file for the metadata schema.
schema_path = os.path.join('tests', '_prose.yml')
schema = sdg.schemas.SchemaInputOpenSdg(schema_path=schema_path)

# Pull in translations.
translations = [
    # Use two Git repos containing translations.
    sdg.translations.TranslationInputSdgTranslations(source='https://github.com/open-sdg/translations-un-sdg.git', tag='1.0.0-rc1'),
    sdg.translations.TranslationInputSdgTranslations(source='https://github.com/open-sdg/translations-open-sdg.git', tag='1.0.0-rc2'),
    # Also look for translations in a local 'translations' folder.
    sdg.translations.TranslationInputYaml(source='translations'),
]

# GeoJSON parameters.
geometry_file = 'tests/geometry.geojson'
name_property = 'kzName'
id_property = 'kzCode'
id_column = 'GeoCode'

# Create an "output" from these inputs/schema/translations, for GeoJSON output.
geojson_output = sdg.outputs.OutputGeoJson(
    inputs=inputs,
    schema=schema,
    output_folder='_site',
    translations=translations,
    geometry_file=geometry_file,
    name_property=name_property,
    id_property=id_property,
    id_column=id_column)

# Validate the indicators.
validation_successful = geojson_output.validate()

# If everything was valid, perform the build.
if validation_successful:
    # Here are several ways you can generate the build:
    # 1. Translated into a single language, like English: geojson_output.execute('en')
    #    (the build will appear in '_site/en')
    # 2. Translated into several languages: geojson_output.execute_per_language(['es', 'ru', 'en'])
    #    (three builds will appear in '_site/es', '_site/ru', and '_site/en')
    # 3. Untranslated: geojson_output.execute()
    #    (the build will appear in '_site')
    geojson_output.execute_per_language(['es', 'ru', 'en'])
else:
    raise Exception('There were validation errors. See output above.')
