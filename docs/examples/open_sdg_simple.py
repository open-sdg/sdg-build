"""
This is an example of converting CSV data and YAML metadata into the JSON output
suitable for the Open SDG reporting platform. In contrast to the open_sdg.py
example, this approach uses helper functions along with a YAML configuration
file.
"""

import os
from sdg.open_sdg import open_sdg_build
from sdg.open_sdg import open_sdg_check

# Assumes that this 'open_sdg_config' file exists in the same folder as this one.
# For an example of the possible options, see docs/examples/open_sdg_config.yml.
folder = os.path.dirname(os.path.realpath(__file__))
config = os.path.join(folder, 'open_sdg_config.yml')

# Perhaps we need to alter the data in some way.
def alter_data(df):
    df['my_column'] = 'foo'

# Perhaps we need to alter the metadata in some way.
def alter_meta(meta):
    meta['my_field'] = 'bar'

# Validate the indicators.
validation_successful = open_sdg_check(config=config, alter_data=alter_data,
    alter_meta=alter_meta)

# If everything was valid, perform the build.
if validation_successful:
    open_sdg_build(config=config, alter_data=alter_data, alter_meta=alter_meta)
else:
    raise Exception('There were validation errors. See output above.')
