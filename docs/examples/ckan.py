"""
This is an example of converting CSV data and YAML metadata into the JSON output
suitable for the Open SDG reporting platform.
"""

import os
import sdg

# Input data from CKAN
resource_endpoint = 'https://inventory.data.gov/api/action/datastore_search'
resource_map = {
    # The resource ID for indicator 4.2.2.
    'f78445b3-e017-43b2-857f-b39d2004546b': '4-2-2'
}
data_input = sdg.inputs.InputCkan(
    resource_map=resource_map,
    resource_endpoint=resource_endpoint
)

# Combine the inputs into one list.
inputs = [data_input]

# Use a Prose.io file for the metadata schema.
schema_path = os.path.join('tests', '_prose.yml')
schema = sdg.schemas.SchemaInputOpenSdg(schema_path=schema_path)

# Create an "output" from these inputs and schema, for JSON for Open SDG.
opensdg_output = sdg.outputs.OutputOpenSdg(inputs, schema, output_folder='_site')

# Validate the indicators.
validation_successful = opensdg_output.validate()

# If everything was valid, perform the build.
if validation_successful:
    opensdg_output.execute()
