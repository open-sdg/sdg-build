"""
This is an example of using an SDMX-JSON API for data (and minimal metadata) and
converting it into the JSON output suitable for the Open SDG reporting platform.
"""

import os
import sdg

# Control how the SDMX dimensions are mapped to Open SDG output. Because the
# Open SDG platform relies on a particular "Units" column, we control that here.
dimension_map = {
    # Open SDG needs the unit column to be named specifically "Units".
    'UNIT_MEASURE': 'Units',
}

# The API endpoint where the source data is. A real-life example is provided so
# that this script can be run as-is.
source = 'http://cambodgia-statvm1.eastasia.cloudapp.azure.com/SeptemberDisseminateNSIService/rest/data/KH_NIS,DF_SDG_KH,1.1/all/?startPeriod=2008&endPeriod=2018'

# Each SDMX source should have a DSD (data structure definition).
dsd = 'http://cambodgia-statvm1.eastasia.cloudapp.azure.com/SeptemberDisseminateNSIService/rest/dataflow/KH_NIS/DF_SDG_KH/1.1/?references=all'
# The "indicator_id" (such as 1-1-1, 1-2-1, etc.) is not yet formalized in the
# SDG DSD standard. It is typically there, but it's location is not predictable.
# So, specify here the XPath query needed to find the indicator id inside each
# series code. This is used to map series codes to indicator ids.
indicator_id_xpath = ".//Name"
indicator_name_xpath = ".//Name"
# This particular DSD contains a typo in indicator 4-c-5, so override that here.
indicator_id_map = {
    'N_KH_040c05_01': '4-c-d'
}

# Create the input object.
data_input = sdg.inputs.InputSdmxJson(
    source=source,
    dimension_map=dimension_map,
    dsd=dsd,
    indicator_id_map=indicator_id_map,
    indicator_id_xpath=indicator_id_xpath,
    indicator_name_xpath=indicator_name_xpath
)
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
else:
    raise Exception('There were validation errors. See output above.')
