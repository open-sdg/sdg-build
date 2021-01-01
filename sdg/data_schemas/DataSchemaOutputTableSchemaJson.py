# -*- coding: utf-8 -*-

import os
from sdg.data_schemas import DataSchemaOutputBase

class DataSchemaOutputTableSchemaJson(DataSchemaOutputBase):
    """A base class for outputing a data schema to a file."""


    def write_schema(self, output_folder='data-schema', filename='data-schema.json'):
        filepath = os.path.join(output_folder, filename)
        self.schema.to_json(target=filepath)
