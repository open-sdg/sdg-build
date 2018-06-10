"""
Created on Sun May 13 2018

@author: dashton

This is the parent script for building the data outputs. It loads the
raw data from csv and sends it through the various processors to
output the main data, edges, and headline in csv and json format.

"""

import sdg
from sdg.data import write_csv
from sdg.json import write_json, df_to_list_dict

# load each csv in and compute derivatives (edges, headline etc)
# hold onto the derivatives
# then write out in the different formats
# write out the "all" files for each derivative

# %% Read each csv and dump out to json and csv

def build_data(src_dir='', site_dir='_site', git=True, git_data_dir=None):
    """Read each input file and edge file and write out json.
    
    Args:
        src_dir: str. Directory root for the project where data and meta data
            folders are
        site_dir: str. Directory to build the site to
        git: bool. Do you want to check git for last updated dates?
        git_data_dir: str. Alternate folder with versioned data files."""
    status = True

    ids = sdg.path.get_ids(src_dir=src_dir)
    if len(ids) < 1:
        raise IOError('No ids found in src_dir: ' + src_dir)
        
    print("Processing data for " + str(len(ids)) + " indicators...")

    all_meta = dict()
    all_headline = dict()

    # Schema
    schema = sdg.schema.get_schema(prose_file='_prose.yml', src_dir=src_dir)
    status = status & write_json('schema', schema, ftype='meta', gz=False, site_dir=site_dir)

    for inid in ids:
        # Load the raw
        data = sdg.data.get_inid_data(inid, src_dir=src_dir)

        # Compute derived datasets
        edges = sdg.edges.edge_detection(inid, data)
        headline = sdg.data.filter_headline(data)

        # Output all the csvs
        status = status & write_csv(inid, data, ftype='data', site_dir=site_dir)
        status = status & write_csv(inid, edges, ftype='edges', site_dir=site_dir)
        status = status & write_csv(inid, headline, ftype='headline', site_dir=site_dir)
        # And JSON
        data_dict = df_to_list_dict(data, orient='list')
        edges_dict = df_to_list_dict(edges, orient='list')
        headline_dict = df_to_list_dict(headline, orient='records')

        status = status & write_json(inid, data_dict, ftype='data', gz=False, site_dir=site_dir)
        status = status & write_json(inid, edges_dict, ftype='edges', gz=False, site_dir=site_dir)
        status = status & write_json(inid, headline_dict, ftype='edges', gz=False, site_dir=site_dir)

        # combined
        comb = {'data': data_dict, 'edges': edges_dict}
        status = status & write_json(inid, comb, ftype='comb', gz=False, site_dir=site_dir)
        
        # Metadata
        meta = sdg.meta.read_meta(inid, git=git, src_dir=src_dir, git_data_dir=git_data_dir)
        status = status & sdg.json.write_json(inid, meta, ftype='meta', site_dir=site_dir)
        
        # Append to the build-time "all" output
        all_meta[inid] = meta
        all_headline[inid] = headline_dict

    status = status & sdg.json.write_json('all', all_meta, ftype='meta', site_dir=site_dir)
    status = status & sdg.json.write_json('all', all_headline, ftype='headline', site_dir=site_dir)

    return(status)
