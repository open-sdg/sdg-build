# -*- coding: utf-8 -*-
"""
Information about the metadata fields

@author: dashton

"""

# %% Imports and globals

import yaml
import os

# %% Read schema

def get_schema(prose_file='_prose.yml', src_dir=''):
    """Read the prose config and output as a JSON object
    
    Args:
        src_dir: str. Project root location
        prose_file: str. The file name where the prose config lives.
        
    Returns:
        The information about metadata fields as required by the web code.
        This is quite likely to evolve as the use of prose changes.
    """

    prose_path = os.path.join(src_dir, prose_file)

    with open(prose_path, encoding="UTF-8") as stream:
        config = next(yaml.safe_load_all(stream))

    all_fields = config['prose']['metadata']['meta']

    return all_fields
