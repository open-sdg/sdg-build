"""
This is an example of converting CSV data and YAML metadata into the JSON output
suitable for the Open SDG reporting platform. In contrast to the open_sdg.py
example, this approach uses helper functions along with a YAML configuration
file.
"""

import os
import sdg

config = os.path.join('tests', 'config.yml')

sdg.check_data(config=config)
sdg.build_data(config=config)