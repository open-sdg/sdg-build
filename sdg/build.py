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

def build_data(root='', git=True):
    """Read each input file and edge file and write out json.
    
    Args:
        root: str. Directory root for the project. Currently ignored for write out
        git: bool. Do you want to check git for last updated dates?"""
    status = True

    ids = sdg.path.get_ids(root=root)
    print("Processing data for " + str(len(ids)) + " indicators...")

    all_meta = dict()
    all_headline = dict()

    for inid in ids:
        # Load the raw
        data = sdg.data.get_inid_data(inid, root=root)

        # Compute derived datasets
        edges = sdg.edges.edge_detection(inid, data)
        headline = sdg.data.filter_headline(data)

        # Output all the csvs
        status = status & write_csv(inid, data, ftype='data', root=root)
        status = status & write_csv(inid, edges, ftype='edges', root=root)
        status = status & write_csv(inid, headline, ftype='headline', root=root)
        # And JSON
        data_dict = df_to_list_dict(data, orient='list')
        edges_dict = df_to_list_dict(edges, orient='list')
        headline_dict = df_to_list_dict(headline, orient='list')

        status = status & write_json(inid, data_dict, ftype='data', gz=False, root=root)
        status = status & write_json(inid, edges_dict, ftype='edges', gz=False, root=root)
        status = status & write_json(inid, headline_dict, ftype='edges', gz=False, root=root)

        # combined
        comb = {'data': data_dict, 'edges': edges_dict}
        status = status & write_json(inid, comb, ftype='comb', gz=False, root=root)
        
        # Metadata
        meta = sdg.meta.read_meta(inid, git=git, root=root)
        status = status & sdg.json.write_json(inid, meta, ftype='meta', root=root)
        
        # Append to the build-time "all" output
        all_meta[inid] = meta
        all_headline[inid] = headline_dict

    status = status & sdg.json.write_json('all', all_meta, ftype='meta')
    status = status & sdg.json.write_json('all', all_headline, ftype='headline')

    return(status)
