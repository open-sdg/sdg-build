# -*- coding: utf-8 -*-

import os
from sdg.schemas import SchemaOutputBase

class SchemaOutputOpenSdg(SchemaOutputBase):
    """A class for outputing a schema to the Open SDG Prose.io/JSON file."""


    def write_schema(self, output_folder='meta', filename='schema.json'):
        """Write the Open SDG schema file to disk."""

        # Make sure the folder exists.
        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, filename)
