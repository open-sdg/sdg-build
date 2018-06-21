"""
Created on 2018-06-21

@author: Martin Bamford

Unit tests written retrospectively for the edge detection function (a fairly complex function which did not previously have any tests)
"""

import sdg
import pytest
import os

src_dir = os.path.dirname(os.path.realpath(__file__))

def test_edge_detection_no_edges():
    """Tests an indicator in the test data which has no parent-child relationships
    The edge detection function should return an empty DataFrame
    Acts as a control for the other tests
    """
    inid = "17-19-2"
    data = sdg.data.get_inid_data(inid, src_dir=src_dir)
    edges = sdg.edges.edge_detection(inid, data)
    assert edges.empty

def test_edge_detection_simple():
    """Tests an indicator in the test data which has a single parent-child relationship
    The edge detection function should return a DataFrame with a single row reflecting this relationship
    """
    inid = "1-a-2"
    data = sdg.data.get_inid_data(inid, src_dir=src_dir)
    edges = sdg.edges.edge_detection(inid, data)
    assert len(edges.index) == 1
    assert parent_has_child(edges, 'Area of spending category', 'Area of spending sub-category')

def test_edge_detection_pruned_grandparents():
    """Tests an indicator in the test data which has multiple parent-child relationships including grandparents
    For example it has the grandparent>parent>child relationship Sex>Ethnicity>Ethnic Group
    (Since the ethnic columns are never present without the Sex being specified)
    As the edge detection routine prunes grandparent relationship the results should include
    Sex>Ethnicity and Ethnicity>Ethnic Group but not Sex>Ethnic Group  
    """
    inid = "5-2-2"
    data = sdg.data.get_inid_data(inid, src_dir=src_dir)
    edges = sdg.edges.edge_detection(inid, data)
    assert parent_has_child(edges, 'Sex', 'Ethnicity')
    assert not parent_has_child(edges, 'Sex', 'Ethnic group')
    assert parent_has_child(edges, 'Ethnicity', 'Ethnic group')

def parent_has_child(edges, parent, child):
    """Determines whether the passed DataFrame contains a row matching the following criteria:
    A column named 'From' whose value matches the 'parent' paremeter and a column named 'To' whose value matches the 'child' parameter
    """
    parents = edges.query('From == "' + parent + '"')
    children = parents.get('To')   
    return child in children.unique()