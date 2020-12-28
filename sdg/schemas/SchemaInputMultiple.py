from sdg.schemas import SchemaInputBase

class SchemaInputMultiple(SchemaInputBase):
    """Input schema from multiple other schemas."""

    def __init__(self, schemas=None):
        """Create a new SchemaBase object

        Parameters
        ----------
        schemas : list
            A list of other SchemaInputBase descendants
        """

        if schemas is None:
            schemas = []

        if len(schemas) < 1:
            raise Exception('SchemaInputMultiple requires at least one schema.')

        self.schemas = schemas
        SchemaInputBase.__init__(self)


    def load_schema(self):
        """Import the SDMX MSD into JSON Schema. Overrides parent."""

        self.schema = {
            "allOf": []
        }

        for schema in self.schemas:
            self.schema['allOf'].append(schema.schema)
            self.field_order += schema.field_order
