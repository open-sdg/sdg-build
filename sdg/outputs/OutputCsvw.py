# -*- coding: utf-8 -*-

from sdg.outputs import OutputDataPackage
from frictionless import describe_package
from csvw.frictionless import DataPackage

class OutputCsvw(OutputDataPackage):
    """Output a CSVW package (CSV and JSON file).
    """

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
        table_group.to_file(path)


    def get_documentation_title(self):
        return 'CSVW'


    def get_documentation_description(self):
        return """This output produces CSVW packages for each indicator."""
