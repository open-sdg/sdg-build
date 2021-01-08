# -*- coding: utf-8 -*-

from sdg.outputs import OutputDataPackage
from frictionless import describe_package
from csvw.frictionless import DataPackage
from csvw.metadata import URITemplate

class OutputCsvw(OutputDataPackage):
    """Output a CSVW package (CSV and JSON file).
    """

    def __init__(self, inputs, schema, common_properties=None,
                 table_schema_properties=None, column_properties=None,
                 at_properties=None, **kwargs):
        """ Constructor for OutputCsvw.

        Parameters
        ----------
        inputs : inherit
        schema : inherit
        common_properties : None or dict
            Optional dict of common properties to add to the CSVW metadata. For a
            list of support properties see https://w3c.github.io/csvw/metadata/#common-properties
        at_properties : None or dict
            Optional dict of "at" properties (those starting with @).
        table_schema_properties : None or dict
            Optional dict of properties to add to the CSVW table schema.
            Supported properties include (but may not be limited to):
                - aboutUrl
        column_properties : None or dict of dicts
            Optional dict of dicts of properties to add to the CSVW columns, keyed by column name.
            Support properties include (but may not be limited to):
                - propertyUrl
                - valueUrl
        kwargs
            All the other keyword parameters to be passed to OutputDataPackage class
        """
        OutputDataPackage.__init__(self, inputs, schema, **kwargs)
        if common_properties is None:
            common_properties = {}
        if at_properties is None:
            at_properties = {}
        if table_schema_properties is None:
            table_schema_properties = {}
        if column_properties is None:
            column_properties = {}
        self.common_properties = common_properties
        self.at_properties = at_properties
        self.table_schema_properties = table_schema_properties
        self.column_properties = column_properties


    def get_base_folder(self):
        return 'csvw'


    def write_indicator_package(self, package, descriptor_path, language=None):
        self.write_csvw_package(package, descriptor_path, language)


    def write_top_level_package(self, path, language=None):
        self.write_csvw_package(self.top_level_package, path, language)


    def write_csvw_package(self, package, path, language=None):
        package_dict = dict(package)
        csvw_package = DataPackage(package_dict)
        table_group = csvw_package.to_tablegroup()
        if language is not None:
            table_group.at_props['context'] = [
                "http://www.w3.org/ns/csvw",
                { "@language": language }
            ]
        self.apply_common_properties(table_group)
        self.apply_at_properties(table_group)
        self.apply_table_schema_properties(table_group)
        self.apply_column_properties(table_group)
        table_group.to_file(path)


    def apply_common_properties(self, table_group):
        for key in self.common_properties:
            table_group.common_props[key] = self.common_properties[key]


    def apply_at_properties(self, table_group):
        for key in self.at_properties:
            table_group.at_props[key] = self.at_properties[key]


    def apply_table_schema_properties(self, table_group):
        for table in table_group.tables:
            for property in self.table_schema_properties:
                value = self.table_schema_properties[property]
                self.apply_table_schema_property(table.tableSchema, property, value)


    def apply_table_schema_property(self, table_schema, property, value):
        if self.is_uri_property(property):
            value = URITemplate(value)
        if property == 'aboutUrl':
            table_schema.aboutUrl = value


    def is_uri_property(self, property):
        return property in [
            'aboutUrl',
            'propertyUrl',
            'valueUrl',
        ]


    def apply_column_properties(self, table_group):
        for table in table_group.tables:
            for column in self.column_properties:
                for property in self.column_properties[column]:
                    if column in table.tableSchema.columndict:
                        value = self.column_properties[column][property]
                        self.apply_column_property(table.tableSchema.columndict[column], property, value)


    def apply_column_property(self, column, property, value):
        if self.is_uri_property(property):
            value = URITemplate(value)
        if property == 'propertyUrl':
            column.propertyUrl = value
        elif property == 'valueUrl':
            column.valueUrl = value


    def get_documentation_title(self):
        return 'CSVW'


    def get_documentation_description(self):
        return """This output produces CSVW packages for each indicator."""
