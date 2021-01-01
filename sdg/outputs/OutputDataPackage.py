# -*- coding: utf-8 -*-

import os
import sdg
import json
from sdg.outputs import OutputBase
from sdg.data_schemas import DataSchemaInputIndicator
from pathlib import Path

class OutputDataPackage(OutputBase):
    """Output a tabular data package (https://specs.frictionlessdata.io/data-package/).
    """

    def __init__(self, inputs, schema, output_folder='_site', translations=None,
        indicator_options=None, data_schema_all=None, data_schema_per_indicator=None,
        package_properties=None, resource_properties=None):
        """Constructor for OutputDataPackage.

        Parameters
        ----------

        Inherits all the parameters from OutputBase, plus the following:

        data_schema_all : frictionless.schema
            A data schema that applies to all indicators.
        data_schema_per_indicator : dict
            A mapping of indicator IDs to schemas. If an indicator has a schema
            mapped here, it will be used instead of data_schema_all. If an
            indicator has no schema mapped here, and data_schema_all is None,
            a data schema will be inferred from the indicator data.
        package_properties : dict
            Common properties to add to all the data packages.
        """

        OutputBase.__init__(self, inputs, schema,
            output_folder=output_folder,
            translations=translations,
            indicator_options=indicator_options,
        )
        self.data_schema_all = data_schema_all
        if data_schema_per_indicator is None:
            data_schema_per_indicator = {}
        if package_properties is None:
            package_properties = {}
        if resource_properties is None:
            resource_properties = {}
        self.data_schema_per_indicator = data_schema_per_indicator
        self.package_properties = package_properties
        self.resource_properties = resource_properties


    def build(self, language=None):
        """Write the JSON output expected by Open SDG. Overrides parent."""
        status = True

        for indicator_id in self.get_indicator_ids():
            # Make sure the folder exists.
            package_folder = os.path.join(self.output_folder, 'data-packages', indicator_id)
            Path(package_folder).mkdir(parents=True, exist_ok=True)

            indicator = self.get_indicator_by_id(indicator_id).language(language)
            data_schema = self.data_schema_all
            if indicator_id in self.data_schema_per_indicator:
                data_schema = self.data_schema_per_indicator[indicator_id]
            if data_schema is None:
                data_schema = DataSchemaInputIndicator(schema_path=indicator)

            # Write the data.
            data_path = os.path.join(package_folder, 'data.csv')
            indicator.data.to_csv(data_path, index=False)
            # Write the descriptor.
            descriptor = self.package_properties.copy()
            descriptor['name'] = indicator_id
            descriptor['title'] = indicator.get_name()
            resource = self.resource_properties.copy()
            resource['schema'] = data_schema.get_descriptor()
            resource['path'] = 'data.csv'
            descriptor['resources'] = [resource]

            descriptor_path = os.path.join(package_folder, 'datapackage.json')
            with open(descriptor_path, 'w') as outfile:
                json.dump(descriptor, outfile)

        return status


    def get_documentation_title(self):
        return 'Data packages'


    def get_documentation_content(self, languages=None, baseurl=''):
        if languages is None:
            languages = ['']

        indicator_ids = self.get_documentation_indicator_ids()

        descriptor_endpoint = '{language}/data-packages/{indicator_id}/datapackage.json'
        data_endpoint = '{language}/data-packages/{indicator_id}/data.csv'
        output = '<p>' + self.get_documentation_description() + ' Examples are below:<p>'
        output += '<ul>'
        for language in languages:
            for indicator_id in indicator_ids:
                descriptor_path = descriptor_endpoint.format(language=language, indicator_id=indicator_id)
                data_path =  data_endpoint.format(language=language, indicator_id=indicator_id)
                output += '<li>'
                output += 'Descriptor: <a href="' + baseurl + descriptor_path + '">' + descriptor_path + '</a>'
                output += '<br>'
                output += 'Data: <a href="' + baseurl + data_path + '">' + data_path + '</a>'
                output += '</li>'
        output += '<li>etc...</li>'
        output += '</ul>'
        return output


    def get_documentation_description(self):
        return """This output produces <a href="https://specs.frictionlessdata.io/data-package/">
        data packages</a> for each indicator."""
