"""
This is an example of converting PX files into the JSON output suitable for
the Open SDG reporting platform.
"""

import os
from sdg.open_sdg import open_sdg_build
from sdg.open_sdg import open_sdg_check

# Assumes that this 'open_sdg_config' file exists in the same folder as this one.
# For an example of the possible options, see docs/examples/open_sdg_config.yml.
folder = os.path.dirname(os.path.realpath(__file__))
config = os.path.join(folder, 'open_sdg_px_config.yml')

# Validate the indicators.
validation_successful = open_sdg_check(config=config)

# If everything was valid, perform the build.
if validation_successful:
    open_sdg_build(config=config)
else:
    raise Exception('There were validation errors. See output above.')
