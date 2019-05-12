"""
This is an example of using an SDMX-JSON API for data, YAML for metadata, and
converting it into the JSON output suitable for the Open SDG reporting platform.

TODO: Can we also get metadata from the SDMX-JSON endpoint?
"""

import os
import sdg

# Input data from an SDMX-JSON API endpoint.
endpoint = 'http://cambodgia-statvm1.eastasia.cloudapp.azure.com/SeptemberDisseminateNSIService/rest/data/UNSD,DF_SDG,1.0/'
data_input = sdg.inputs.InputSdmxJsonApi(endpoint=endpoint)

# Input metadata from YAML files matching this pattern: tests/meta/*-*.md
meta_pattern = os.path.join('tests', 'meta', '*-*.md')
meta_input = sdg.inputs.InputYamlMdMeta(path_pattern=meta_pattern)

# Combine these inputs into one list.
inputs = [data_input, meta_input]

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
