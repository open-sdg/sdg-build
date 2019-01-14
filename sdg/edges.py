# -*- coding: utf-8 -*-
"""
Created on 2017-10-04
@author: dougashton
This is one of the more complicated scripts in the suite. It does he following\
 for every csv file:
    1. For each column decide a parent child relationship with every other.
    2. Column A is a parent of column B if:
        a. B is only present when A is present
        b. A is sometimes present when B is not present
        c. If A and B are only seen together then the left-most column in the\
         data frame is the parent
    3. Once edges have been defined they are pruned so that grand parents are\
    not mistaken for parents
"""

# %% setup

import pandas as pd
import numpy as np
import itertools
import os

# %% Check correct columns - copied from csvcheck


def check_headers(inid, df):
    """This is copied from csv check but the primary goal is to check that
    the inid headers are appropriate for edge detection"""
    cols = df.columns

    if cols[0] != 'Year':
        raise ValueError(inid + ': First column not called "Year"')
    if cols[-1] != 'Value':
        raise ValueError(inid + ': Last column not called "Value"')


# %% Detect the edges


def x_without_y(x, y):
    """
     Args:
        x (pandas Series): Left hand column
        y (pandas Series): Right hand column
    """
    # returns true if there are any cases where an element in
    # the y column is empty (is a nan) and the corresponding element
    # in the x column is not empty
    return np.any(y.isnull() & x.notnull())


def detect_all_edges(inid, df):
    """Loop over the data frame and try all pairs"""
    cols = df.columns
    # Remove the protected columns
    cols = cols[[x not in ['Year', 'Units', 'Value', 'GeoCode'] for x in cols]]

    edges = pd.DataFrame(columns=['From', 'To'])

    # Loop over all pairs
    for a, b in itertools.combinations(cols, 2):
        # itertools.combinations returns pairs of columns in the order they appear
        # without repeating elements, so:
        # combinations('ABCD', 2)	produces AB AC AD BC BD CD
        # but does not produce BA, CA, etc.
        
        # Check if a and b are ever present without each other
        a_without_b = x_without_y(df[a], df[b])
        b_without_a = x_without_y(df[b], df[a])

        # Check if a and b are not empty.
        a_not_empty = not df[a].dropna().empty
        b_not_empty = not df[b].dropna().empty
        
        # test if ab is an edge (at least one case where b has an empty elements where a does not)
        if a_without_b and not b_without_a and b_not_empty:
            # A is a parent of B
            # so add to df of edges
            edges = edges.append(pd.DataFrame({'From': [a], 'To': [b]}))
        
        # if ab is not an edge, test whether ba is an edge (at least one case where a has empty and b doesn't)
        elif b_without_a and not a_without_b and a_not_empty:
            # B is a parent of A
            # so add to df of edges
            edges = edges.append(pd.DataFrame({'From': [b], 'To': [a]}))
            
        # if ab not an edge and ba not an edge, then test that for every element in a there is an element in 
        # b and vice versa
        elif not a_without_b and not b_without_a and a_not_empty and b_not_empty:
            # co-depedent; choose A as left-most
            edges = edges.append(pd.DataFrame({'From': [a], 'To': [b]}))

    return edges


# %% Remove Grand Parents


def prune_grand_parents(edges):
    """Prune edges that shortcut a parent-child relationship
    Args:
        edges (DataFrame): The edges data frame
    Returns:
        The data frame with grand parent edges removed
    """
    # if A is a parent of B and B is a parent of C, then the above code will
    # return from A to C as an edge (see 'transitive relation') 
    # this section removes the AC edge in those cases
    
    # for loop through unique 'children' (those that have parents)
    for group in edges['To'].unique():
        
        # list all the parents of the given child
        parents0 = list(edges['From'][edges['To'] == group])
        
        # create an empty list to fill with grandparents
        grand_parents = list()

        # elements will be removed from parents0 inside the while loop - once 
        # they have all been removed, end loop
        while len(parents0) > 0:
            
            # go through the list of parents
            for p in parents0:
                
                # define parents as the list of parents of p (a known parent)
                parents = list(edges['From'][edges['To'] == p])
                # if len(parents) > 0, then there are parents of the parent (p)
                if len(parents) > 0:
                    # so add them to the list of grand_parents
                    grand_parents = grand_parents + parents
                # set parents0 to be the newly identified grand parents
                parents0 = parents
        
        # drop all edges where the 'from' is in grandparents AND where the 'to'
        # is the child from the start of the outer for loop   
        keep = ~(edges['From'].isin(grand_parents) & (edges['To'] == group))
        
        edges = edges[keep]
    return edges


# %% Write out edges for one inid


def edge_detection(inid, df):
    """Check dependencies between columns and write out the edges
    If there are any problems return False as this is part of the build.
    Args:
        inid (str): The indicator id for printing
        df (pandas DataFrame): The indicator data read from raw csv
    Returns:
        DataFrame: edge data frame
    """
    # Run through the check functions
    check_headers(inid, df)
    
    # Get the edges
    edges = detect_all_edges(inid, df)
    edges = prune_grand_parents(edges)
    
    return edges
