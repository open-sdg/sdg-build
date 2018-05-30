# -*- coding: utf-8 -*-
"""
Reset the metadata files so that markdown content is removed, any metadata
other than global & page metadata is removed, and reporting status is reset

@author: Doug Ashton
"""

# %% setup

import yaml
import glob
import os
import sys
from sdg.path import get_ids, input_path

# %% A dictionary of defaults to add

add_fields = {'reporting_status': 'notstarted', 'published': True, 'graph_type': 'line'}

# %% Which metadata items do we keep?


def get_fields(prose_path):
    """Read the config file and decide which fields to save"""
    with open(prose_path, encoding="UTF-8") as stream:
        config = next(yaml.safe_load_all(stream))

    all_fields = config['prose']['metadata']['meta']

    # Using a list to preserve order
    all_scopes = [get_scope(field) for field in all_fields]

    keep_fields = [
            name for name, scope in all_scopes
            if scope in ['page', 'global']
            ]

    return keep_fields


# %% Extract the scope from a field

def get_scope(field):
    """For a single field get the scope variable
    Return a tuple with name:scope pairs"""
    name = field['name']
    if 'scope' in field['field']:
        scope = field['field']['scope']
    else:
        scope = ''

    return (name, scope)


# %% Resetting a single item
def reset_meta(meta, fname, keep_fields):
    """Check an individual metadata and return logical status"""
    # TODO: Use the status
    status = True

    keep_meta = {
            key: value for (key, value) in meta.items()
            if key in keep_fields
            }

    # Add the defaults
    final_meta = keep_meta.copy()
    final_meta.update(add_fields)
    # final_meta = {**keep_meta, **add_fields} # this is python >=3.5

    # Write to a string first because I want to override trailing dots
    yaml_string = yaml.dump(final_meta,
                            default_flow_style=False,
                            explicit_start=True,
                            explicit_end=True)
    with open(fname, "w") as md_file:
        md_file.write(yaml_string.replace("\n...\n", "\n---\n"))

    return status


# %% Read each yaml and run the checks

def reset_all_meta(root=''):

    status = True

    # Read the config files
    prose_path = os.path.join(root, '_prose.yml')
    keep_fields = get_fields(prose_path)

    status = True

    ids = get_ids(root=root)

    if len(ids) == 0:
        raise FileNotFoundError("No indicator IDs found")
    
    print("Resetting " + str(len(ids)) + " metadata files...")
    
    for inid in ids:
        met = input_path(inid, ftype='meta', root=root)
        with open(met, encoding="UTF-8") as stream:
            meta = next(yaml.safe_load_all(stream))
        status = status & reset_meta(meta, fname=met, keep_fields=keep_fields)

    return(status)
