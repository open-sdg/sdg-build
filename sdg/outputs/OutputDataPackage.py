# -*- coding: utf-8 -*-

import os
from sdg.outputs import OutputBase
from sdg.data_schemas import DataSchemaInputIndicator
from frictionless import Schema
from frictionless import Package
from frictionless import describe_package
from frictionless import describe_resource
from pathlib import Path

class OutputDataPackage(OutputBase):
    """Output a tabular data package (https://specs.frictionlessdata.io/data-package/).
    """

    def __init__(self, inputs, schema, output_folder='_site', translations=None,
        indicator_options=None, data_schema=None, package_properties=None,
        resource_properties=None, field_properties=None, sorting='default',
        logging=None):
        """Constructor for OutputDataPackage.

        Parameters
        ----------

        Inherits all the parameters from OutputBase, plus the following:

        data_schema : DataSchemaInputBase
            An optional subclass of DataSchemaInputBase
        package_properties : dict
            Common properties to add to all the data packages.
            Note that this can also be set per-indicator in a "datapackage" metadata property.
        resource_properties : dict
            Common properties to add to the resource in all data packages.
            Note that this can also be set per-indicator in a "datapackage" metadata property.
        field_properties : dict of dicts
            Properties to add to specific fields, keyed by field name.
            Note that this can also be set per-indicator in a "datapackage" metadata property.
        sorting : string
            Strategy to use when sorting the columns and values. Options are:
            - alphabetical: Sort columns/values in alphabetical order
            - default: Use the default sorting, either from the data_schema or
              from the position of columns/values in the source data
        """

        OutputBase.__init__(self, inputs, schema,
            output_folder=output_folder,
            translations=translations,
            indicator_options=indicator_options,
            logging=logging
        )
        self.top_level_package = None
        self.data_schema = data_schema
        if package_properties is None:
            package_properties = {}
        if resource_properties is None:
            resource_properties = {}
        if field_properties is None:
            field_properties = {}
        self.package_properties = package_properties
        self.resource_properties = resource_properties
        self.field_properties = field_properties
        self.sorting = sorting
        self.per_indicator_metadata_field = 'datapackage'


    def get_base_folder(self):
        return 'data-packages'


    def build(self, language=None):
        """Write the JSON output expected by Open SDG. Overrides parent."""
        status = True

        self.create_top_level_package('all', 'All indicators')

        backup_data_schema = DataSchemaInputIndicator(source=self.indicators)
        data_schema_not_specified = False
        if self.data_schema is None:
            data_schema_not_specified = True
            self.data_schema = backup_data_schema

        for indicator_id in self.get_indicator_ids():
            # Make sure the folder exists.
            package_folder = os.path.join(self.output_folder, self.get_base_folder(), indicator_id)
            Path(package_folder).mkdir(parents=True, exist_ok=True)

            indicator = self.get_indicator_by_id(indicator_id).language(language)
            backup_schema_was_used = False
            data_schema_for_indicator = self.data_schema.get_schema_for_indicator(indicator)
            if data_schema_for_indicator is None:
                backup_schema_was_used = True
                data_schema_for_indicator = backup_data_schema.get_schema_for_indicator(indicator)

            # Clone the schema so that it can be sorted and translated.
            data_schema_for_indicator = Schema(dict(data_schema_for_indicator))
            # We only sort the schema if it was not specified or if
            # the backup schema was used.
            if data_schema_not_specified or backup_schema_was_used:
                self.sort_data_schema(data_schema_for_indicator)
            if language is not None:
                self.translate_data_schema(data_schema_for_indicator, language)

            # Write the data.
            data_path = os.path.join(package_folder, 'data.csv')
            self.write_data(indicator.data, data_path)

            # Write the descriptor.
            descriptor_path = os.path.join(package_folder, 'datapackage.json')
            indicator_package = self.create_indicator_package(data_schema_for_indicator, data_path, indicator_id, indicator)
            self.write_indicator_package(indicator_package, descriptor_path, indicator, language=language)

            # Add to the top level package.
            top_level_data_path = indicator_id + '/data.csv'
            top_level_resource = self.create_resource(data_schema_for_indicator, data_path, indicator_id, indicator, top_level_data_path)
            self.add_to_top_level_package(top_level_resource)

        top_level_descriptor_path = os.path.join(self.output_folder, self.get_base_folder(), 'all.json')
        self.write_top_level_package(top_level_descriptor_path, language=language)

        return status


    def create_top_level_package(self, name, title):
        self.top_level_package = Package(self.package_properties)
        self.top_level_package.name = name
        self.top_level_package.title = title


    def write_top_level_package(self, path, language=None):
        self.top_level_package.to_json(path)
        # Workaround for https://github.com/frictionlessdata/frictionless-py/issues/788
        os.chmod(path, 0o644)


    def add_to_top_level_package(self, resource):
        self.top_level_package.add_resource(resource)


    def write_data(self, df, path):
        df.to_csv(path, index=False)


    def apply_package_properties(self, package, indicator):
        for key in self.package_properties:
            package[key] = self.package_properties[key]
        indicator_props = self.get_properties_per_indicator(indicator, 'package_properties')
        for key in indicator_props:
            package[key] = indicator_props[key]


    def apply_resource_properties(self, resource, indicator):
        for key in self.resource_properties:
            resource[key] = self.resource_properties[key]
        indicator_props = self.get_properties_per_indicator(indicator, 'resource_properties')
        for key in indicator_props:
            resource[key] = indicator_props[key]


    def apply_field_properties(self, resource, indicator):
        for field_name in self.field_properties:
            field = resource.get_field(field_name)
            if field is not None:
                for key in self.field_properties[field_name]:
                    field[key] = self.field_properties[field_name][key]
        indicator_props = self.get_properties_per_indicator(indicator, 'field_properties')
        for field_name in indicator_props:
            field = resource.get_field(field_name)
            if field is not None:
                for key in indicator_props[field_name]:
                    field[key] = indicator_props[field_name][key]


    def create_resource(self, schema, data_path, indicator_id, indicator, data_path_override=None):
        resource = describe_resource(data_path)
        self.apply_resource_properties(resource, indicator)
        resource.schema = schema
        resource.path = data_path_override if data_path_override is not None else data_path
        resource.name = indicator_id
        resource.title = indicator.get_name()
        self.apply_field_properties(resource, indicator)
        return resource


    def create_indicator_package(self, schema, data_path, indicator_id, indicator):
        package = describe_package(data_path)
        self.apply_package_properties(package, indicator)
        package.name = indicator_id
        package.title = indicator.get_name()
        resource = package.get_resource('data')
        self.apply_resource_properties(resource, indicator)
        resource.schema = schema
        resource.path = 'data.csv'
        return package


    def write_indicator_package(self, package, descriptor_path, indicator, language=None):
        package.to_json(descriptor_path)
        # Workaround for https://github.com/frictionlessdata/frictionless-py/issues/788
        os.chmod(descriptor_path, 0o644)


    def sort_data_schema(self, schema):
        if self.sorting == 'alphabetical':
            schema.fields.sort(key=lambda field: field.name)
            for field in schema.fields:
                if 'enum' in field.constraints:
                    field.constraints['enum'].sort(key=str)


    def translate_data_schema(self, schema, language):
        groups_common = ['data']
        for field in schema.fields:
            groups = groups_common + [field.name]
            # Translate the field titles.
            field.title = self.translation_helper.translate(field.name, language, groups)
            # Translate the values.
            if 'enum' in field.constraints:
                field.constraints['enum'] = [
                    self.translation_helper.translate(value, language, groups)
                    for value in field.constraints['enum']
                ]


    def get_properties_per_indicator(self, indicator, property_type):
        if indicator is None:
            return {}

        per_indicator = indicator.get_meta_field_value(self.per_indicator_metadata_field)

        if per_indicator is not None and property_type in per_indicator:
            return per_indicator[property_type]
        else:
            return {}


    def validate(self):
        """Validate the data for the indicators."""

        status = True
        if self.data_schema is not None:
            for inid in self.indicators:
                status = status & self.data_schema.validate(self.indicators[inid])

        return status


    def get_documentation_title(self):
        return 'Data packages'


    def get_documentation_content(self, languages=None, baseurl=''):
        if languages is None:
            languages = ['']

        indicator_ids = self.get_documentation_indicator_ids()

        descriptor_endpoint = '{language}/{base_folder}/{indicator_id}/datapackage.json'
        data_endpoint = '{language}/{base_folder}/{indicator_id}/data.csv'
        all_endpoint = '{language}/{base_folder}/all.json'
        output = '<p>' + self.get_documentation_description() + ' Examples are below:<p>'
        output += '<ul>'
        for language in languages:
            for indicator_id in indicator_ids:
                descriptor_path = descriptor_endpoint.format(language=language, indicator_id=indicator_id, base_folder=self.get_base_folder())
                data_path =  data_endpoint.format(language=language, indicator_id=indicator_id, base_folder=self.get_base_folder())
                output += '<li>' + indicator_id + ':<ul>'
                output += '<li><a href="' + baseurl + descriptor_path + '">' + descriptor_path + '</a></li>'
                output += '<li><a href="' + baseurl + data_path + '">' + data_path + '</a></li>'
                output += '</ul></li>'
            all_path = all_endpoint.format(language=language, base_folder=self.get_base_folder())
            output += '<li>All indicators: <a href="' + baseurl + all_path + '">' + all_path + '</a></li>'
        output += '<li>etc...</li>'
        output += '</ul>'
        return output


    def get_documentation_description(self):
        return """This output produces <a href="https://specs.frictionlessdata.io/data-package/">
        data packages</a> for each indicator."""
