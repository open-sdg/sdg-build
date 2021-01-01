# -*- coding: utf-8 -*-

class DataSchemaOutputBase:
    """A base class for outputing a data schema to a file."""


    def __init__(self, schema):
        """Create a new DataSchemaOutputBase object

        Parameters
        ---------
        schema : DataSchemaInputBase
            DataSchemaInputBase (or subclass) to output
        """

        self.schema = schema


    def write_schema(self):
        """Write the schema. This should be overridden by a subclass."""
        raise NotImplementedError
