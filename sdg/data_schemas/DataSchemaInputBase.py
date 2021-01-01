# -*- coding: utf-8 -*-

import frictionless

class DataSchemaInputBase:
    """A base class for importing a data schema, querying it, and validating with it.

    This class assumes imported schema are valid Table Schema.
    See here: https://specs.frictionlessdata.io/table-schema/
    """


    def __init__(self, schema_path=''):
        """Create a new SchemaBase object

        Parameters
        ----------
        schema_path : string
            A path to the schema file to input
        """

        self.schema_path = schema_path
        self.schema = self.load_schema()


    def load_schema(self):
        """Load the schema. This should be overridden by a subclass.
        See https://frictionlessdata.io/tooling/python/api-reference/#frictionless-schema
        """
        raise NotImplementedError


    def validate(self, indicator):
        """Validate the data for an Indicator object.

        Parameters
        ----------
        indicator : Indicator
            The instance of Indicator to validate

        Returns
        -------
        boolean
            True if validation passes, False otherwise
        """
        status = True
        if indicator.has_data():
            df = indicator.data
            report = frictionless.validate.validate_table(df, schema=self.schema)
            # TODO: Output some feedback of errors.
            status = report.valid()

        return status


    def get_descriptor(self):
        return dict(self.schema)


    def get_fields(self):
        return self.schema.field_names()


    def get_values(self, field_name):
        """Get the allowed values for a field.

        Parameters
        ----------
        field_name : string
            The name of a field to get allowed values for

        Returns
        -------
        list
            List of allowed values
        """
        field = self.schema.get_field(field_name)
        constraints = field.constraints()
        return constraints['enum'] if 'enum' in constraints else []
