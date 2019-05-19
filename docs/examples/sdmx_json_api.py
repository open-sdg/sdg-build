"""
This is an example of using an SDMX-JSON API for data (and minimal metadata) and
converting it into the JSON output suitable for the Open SDG reporting platform.
"""

import os
import sdg

# Map SDMX codes to SDG indicator ids. In practice this would be much longer,
# but for this example we are only doing Goal 1.
indicator_map = {
    'SI_POV_NAHC':    '1.2.1',
    'SI_POV_NMPI':    '1.2.2',
    'N_KH_010301_01': '1.3.1',
    'N_KH_010401_01': '1.4.1',
}

# Control how the SDMX dimensions are mapped to Open SDG output. Because the
# Open SDG platform relies on a particular "Units" column, we control that here.
dimension_map = {
    # Open SDG needs the unit column to be named specifically "Units".
    'UNIT_MEASURE': 'Units',
}

# The API endpoint where the source data is. A real-life example is provided so
# that this script can be run as-is.
endpoint = 'http://cambodgia-statvm1.eastasia.cloudapp.azure.com/SeptemberDisseminateNSIService/rest/data/KH_NIS,DF_SDG_KH,1.1/all/?startPeriod=2008&endPeriod=2018'

# Create the input object.
data_input = sdg.inputs.InputSdmxJsonApi(endpoint=endpoint,
                                         indicator_map=indicator_map,
                                         dimension_map=dimension_map)
inputs = [data_input]

# Use the Prose.io file for the metadata schema.
schema_path = os.path.join('tests', '_prose.yml')
schema = sdg.schemas.SchemaInputOpenSdg(schema_path=schema_path)

# Create an "output" from these inputs and schema, for JSON for Open SDG.
opensdg_output = sdg.outputs.OutputOpenSdg(inputs, schema, output_folder='_site')

# Validate the indicators.
validation_successful = opensdg_output.validate()

# If everything was valid, perform the build.
if validation_successful:
    opensdg_output.execute()
