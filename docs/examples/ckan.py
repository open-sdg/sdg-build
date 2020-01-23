"""
This is an example of importing data from a CKAN instance and converting it
into the JSON output suitable for the Open SDG reporting platform.
"""

import os
import sdg
import pandas as pd

# Input data from CKAN
endpoint = 'https://inventory.data.gov/api/action/datastore_search'
indicator_id_map = {
    # The resource ID for indicator 4.2.2.
    'f78445b3-e017-43b2-857f-b39d2004546b': '4-2-2'
}
data_input = sdg.inputs.InputCkan(
    endpoint=endpoint,
    indicator_id_map=indicator_id_map
)

# The data in this example is not exactly what sdg-build expects, so we need to
# add a "data alteration" function to correct it.
def data_alteration(df):
    # The data in this example is in a "wide" format, so we need to convert it
    # to the "tidy" format expected by sdg-build.
    df = pd.melt(df, id_vars=['year'], var_name='gender', value_name='value')
    # We also rename some columns to match what sdg-build expects.
    df = df.rename(columns={'year': 'Year', 'value': 'Value'})
    return df
data_input.add_data_alteration(data_alteration)

# Combine the inputs into one list.
inputs = [data_input]

# Use a Prose.io file for the metadata schema.
schema_path = os.path.join('tests', '_prose.yml')
schema = sdg.schemas.SchemaInputOpenSdg(schema_path=schema_path)

# Use SDG Translations for translations
tag = '0.8.1'
translations = sdg.translations.TranslationInputSdgTranslations(tag=tag)

# Create an "output" from these inputs and schema, for JSON for Open SDG.
opensdg_output = sdg.outputs.OutputOpenSdg(
    inputs=inputs,
    schema=schema,
    output_folder='_site',
    translations=translations)

# Validate the indicators.
validation_successful = opensdg_output.validate()

# If everything was valid, perform the build.
if validation_successful:
    # Here are several ways you can generate the build:
    # 1. Translated into a single language, like English: opensdg_output.execute('en')
    #    (the build will appear in '_site/en')
    # 2. Translated into several languages: opensdg_output.execute_per_language(['es', 'ru', 'en'])
    #    (three builds will appear in '_site/es', '_site/ru', and '_site/en')
    # 3. Untranslated: opensdg_output.execute()
    #    (the build will appear in '_site')
    opensdg_output.execute_per_language(['es', 'ru', 'en'])
else:
    raise Exception('There were validation errors. See output above.')
