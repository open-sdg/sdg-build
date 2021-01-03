# -*- coding: utf-8 -*-

from frictionless import Schema
from sdg.data_schemas import DataSchemaInputFiles
import yaml

class DataSchemaInputTableSchemaYaml(DataSchemaInputFiles):
    """A class for reading a data schema from a Table Schema in YAML format.
    The source parameter is assumed to be a path pattern (glob) showing
    where the YAML files are."""


    def load_schema(self, path):
        with open(path) as file:
            schema = yaml.load(file, Loader=yaml.FullLoader)
            return Schema(schema)
