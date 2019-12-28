"""
This is an example of converting CSV data and YAML metadata into the JSON output
suitable for the Open SDG reporting platform. In contrast to the open_sdg.py
example, this approach uses helper functions along with a YAML configuration
file.
"""

import os
import sdg

# Assumes that this config file exists. For an example of the possible options,
# see docs/examples/open_sdg_config.yml.
config = 'open_sdg_config.yml'

# Validate the indicators.
validation_successful = sdg.check_data(config=config)

# If everything was valid, perform the build.
if validation_successful:
    sdg.build_data(config=config)
else:
    raise Exception('There were validation errors. See output above.')
