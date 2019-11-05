"""
This is an example of converting CSV data and YAML metadata into the JSON output
suitable for the Open SDG reporting platform.
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

# Use SDG Translations for translations
translations = sdg.translations.TranslationInputSdgTranslations()

# Create an "output" from these inputs/schema/translations, for Open SDG output.
opensdg_output = sdg.outputs.OutputOpenSdg(
    inputs=inputs,
    schema=schema,
    output_folder='_site',
    translations=translations)

# Validate the indicators.
validation_successful = opensdg_output.validate()

# If everything was valid, perform the build.
if validation_successful:
    opensdg_output.execute()
