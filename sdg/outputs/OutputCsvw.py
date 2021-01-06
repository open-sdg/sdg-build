# -*- coding: utf-8 -*-

from sdg.outputs import OutputDataPackage
from frictionless import describe_package
from csvw.frictionless import DataPackage

class OutputCsvw(OutputDataPackage):
    """Output a CSVW package (CSV and JSON file).
    """

    def __init__(self, inputs, schema, common_properties=None, **kwargs):
        """ Constructor for OutputCsvw.

        Parameters
        ----------
        inputs : inherit
        schema : inherit
        common_properties : None or dict
            Optional dict of common properties to add to the CSVW metadata.
            See https://w3c.github.io/csvw/metadata/#common-properties
        kwargs
            All the other keyword parameters to be passed to OutputDataPackage class
        """
        OutputDataPackage.__init__(self, inputs, schema, **kwargs)
        if common_properties is None:
            common_properties = {}
        self.common_properties = common_properties


    def get_base_folder(self):
        return 'csvw'


    def write_indicator_package(self, package, descriptor_path):
        self.write_csvw_package(package, descriptor_path)


    def write_top_level_package(self, path):
        self.write_csvw_package(self.top_level_package, path)


    def write_csvw_package(self, package, path):
        package_dict = dict(package)
        csvw_package = DataPackage(package_dict)
        table_group = csvw_package.to_tablegroup()
        self.apply_common_properties(table_group)
        table_group.to_file(path)


    def apply_common_properties(self, table_group):
        for key in self.common_properties:
            table_group.common_properties[key] = self.common_properties[key]


    def get_documentation_title(self):
        return 'CSVW'


    def get_documentation_description(self):
        return """This output produces CSVW packages for each indicator."""
