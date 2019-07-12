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
endpoint = 'http://cambodgia-statvm1.eastasia.cloudapp.azure.com/SeptemberDisseminateNSIService/rest/data/KH_NIS,DF_SDG_KH,1.1/all/?startPeriod=2008&endPeriod=2018'

# Each SDMX source should have a DSD (data structure definition). If the SDMX
# source uses the global DSD (https://unstats.un.org/sdgs/files/SDG_DSD.xml)
# then the following optional settings are not needed. Otherwise you will need
# to set the dsd, namespaces, series_xpath, and indicator_id_xpath.
dsd = 'http://cambodgia-statvm1.eastasia.cloudapp.azure.com/SeptemberDisseminateNSIService/rest/dataflow/KH_NIS/DF_SDG_KH/1.1/?references=all'
namespaces = {
    "message": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message",
    "structure": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure",
    "common": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common"
}
series_xpath = ".//structure:Codelist[@id='CL_SERIES']/structure:Code"
indicator_id_xpath = ".//common:Name"

# Create the input object.
data_input = sdg.inputs.InputSdmxJsonApi(endpoint=endpoint,
                                         indicator_map=indicator_map,
                                         dimension_map=dimension_map,
                                         dsd=dsd,
                                         namespaces=namespaces,
                                         series_xpath=series_xpath,
                                         indicator_id_xpath=indicator_id_xpath)
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
