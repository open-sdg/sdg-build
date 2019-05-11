# -*- coding: utf-8 -*-

class SchemaOutputBase:
    """A base class for outputing a schema to a file."""


    def __init__(self, schema):
        """Create a new SchemaBase object

        Args:
          schema: SchemaBase instance - the schema to output.
        """

        self.schema = schema


    def write_schema(self):
        """Write the schema. This should be overridden by a subclass."""
        raise NotImplementedError
