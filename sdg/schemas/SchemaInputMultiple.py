from sdg.schemas import SchemaInputBase

class SchemaInputMultiple(SchemaInputBase):
    """Input schema from multiple other schemas."""

    def __init__(self, schemas=None, **kwargs):
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
        SchemaInputBase.__init__(self, **kwargs)


    def load_schema(self):
        """Import the SDMX MSD into JSON Schema. Overrides parent."""

        self.schema = {
            "allOf": []
        }

        for schema in self.schemas:
            self.schema['allOf'].append(schema.schema)
            for field in schema.get_field_order():
                self.add_item_to_field_order(field)


    def get(self, field, default=None, must_exist=False):
        value = None
        for schema in self.schema['allOf']:
            f = schema['properties'].get(field, default)
            if f is not None:
                value = f
                break
        if must_exist and value is None:
            raise ValueError(field + " doesn't exist in schema")
        if value is None:
            print(field)
        return value
