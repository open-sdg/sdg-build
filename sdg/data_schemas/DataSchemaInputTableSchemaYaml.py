# -*- coding: utf-8 -*-

from frictionless import Schema
from sdg.data_schemas import DataSchemaInputBase
import yaml

class DataSchemaInputTableSchemaYaml(DataSchemaInputBase):
    """A class for reading a data schema from a Table Schema in YAML format.
    The schema_path parameter should be the path to the YAML file."""


    def load_schema(self):
        with open(self.schema_path) as file:
            schema = yaml.load(file, Loader=yaml.FullLoader)
            return Schema(schema)
