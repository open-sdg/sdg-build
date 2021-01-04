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
        resource_properties=None):
        """Constructor for OutputDataPackage.

        Parameters
        ----------

        Inherits all the parameters from OutputBase, plus the following:

        data_schema : DataSchemaInputBase
            An optional subclass of DataSchemaInputBase
        package_properties : dict
            Common properties to add to all the data packages.
        resource_properties : dict
            Common properties to add to the resource in all data packages.
        """

        OutputBase.__init__(self, inputs, schema,
            output_folder=output_folder,
            translations=translations,
            indicator_options=indicator_options,
        )
        self.data_schema = data_schema
        if package_properties is None:
            package_properties = {}
        if resource_properties is None:
            resource_properties = {}
        self.package_properties = package_properties
        self.resource_properties = resource_properties


    def build(self, language=None):
        """Write the JSON output expected by Open SDG. Overrides parent."""
        status = True

        all_indicators = Package(self.package_properties)
        all_indicators.name = 'all'
        all_indicators.title = 'All indicators'

        backup_data_schema = DataSchemaInputIndicator(source=self.indicators)
        if self.data_schema is None:
            self.data_schema = backup_data_schema

        for indicator_id in self.get_indicator_ids():
            # Make sure the folder exists.
            package_folder = os.path.join(self.output_folder, 'data-packages', indicator_id)
            Path(package_folder).mkdir(parents=True, exist_ok=True)

            indicator = self.get_indicator_by_id(indicator_id).language(language)
            data_schema_for_indicator = self.data_schema.get_schema_for_indicator(indicator)
            if data_schema_for_indicator is None:
                data_schema_for_indicator = backup_data_schema.get_schema_for_indicator(indicator)

            if language is not None:
                # Clone the schema so that it can be translated.
                data_schema_for_indicator = Schema(dict(data_schema_for_indicator))
                self.translate_data_schema(data_schema_for_indicator, language)

            # Write the data.
            data_path = os.path.join(package_folder, 'data.csv')
            indicator.data.to_csv(data_path, index=False)
            # Write the descriptor.
            package = describe_package(data_path)
            for key in self.package_properties:
                package[key] = self.package_properties[key]
            package.name = indicator_id
            package.title = indicator.get_name()
            for key in self.resource_properties:
                package.get_resource('data')[key] = self.resource_properties[key]
            package.get_resource('data').schema = data_schema_for_indicator
            package.get_resource('data').path = 'data.csv'
            descriptor_path = os.path.join(package_folder, 'datapackage.json')
            package.to_json(descriptor_path)
            # Add to the datapackage for all resources.
            all_resource = describe_resource(data_path)
            for key in self.resource_properties:
                all_resource[key] = self.resource_properties[key]
            all_resource.schema = data_schema_for_indicator
            all_resource.path = indicator_id + '/data.csv'
            all_resource.name = indicator_id
            all_resource.title = indicator.get_name()
            all_indicators.add_resource(all_resource)

        all_indicators_path = os.path.join(self.output_folder, 'data-packages', 'all.json')
        all_indicators.to_json(all_indicators_path)

        return status


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

        descriptor_endpoint = '{language}/data-packages/{indicator_id}/datapackage.json'
        data_endpoint = '{language}/data-packages/{indicator_id}/data.csv'
        all_endpoint = '{language}/data-packages/all.json'
        output = '<p>' + self.get_documentation_description() + ' Examples are below:<p>'
        output += '<ul>'
        for language in languages:
            for indicator_id in indicator_ids:
                descriptor_path = descriptor_endpoint.format(language=language, indicator_id=indicator_id)
                data_path =  data_endpoint.format(language=language, indicator_id=indicator_id)
                output += '<li>' + indicator_id + ':<ul>'
                output += '<li><a href="' + baseurl + descriptor_path + '">' + descriptor_path + '</a></li>'
                output += '<li><a href="' + baseurl + data_path + '">' + data_path + '</a></li>'
                output += '</ul></li>'
            all_path = all_endpoint.format(language=language)
            output += '<li>All indicators: <a href="' + baseurl + all_path + '">' + all_path + '</a></li>'
        output += '<li>etc...</li>'
        output += '</ul>'
        return output


    def get_documentation_description(self):
        return """This output produces <a href="https://specs.frictionlessdata.io/data-package/">
        data packages</a> for each indicator."""
