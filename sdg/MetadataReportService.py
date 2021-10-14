import os
import sdg
import pandas as pd
from slugify import slugify
from sdg.Loggable import Loggable
import urllib.request
import json
import numpy as np

class MetadataReportService(Loggable):
    """Report generation to document metadata_fields in data."""


    def __init__(self, outputs, languages=None, translation_helper=None,
                 indicator_url=None, extra_metadata_fields=None, logging=None):
        """Constructor for the metadata_fieldReportService class.
        Parameters
        ----------
        outputs : list
            Required list of objects inheriting from OutputBase. Each output
            will receive its own documentation page (or pages).
        languages : list
            Optional list of language codes. If languages are provided, these
            languages will display as translations in additional columns.
            Defaults to [].
        translation_helper : TranslationHelper
            Instance of TranslationHelper class to perform translations.
        indicator_url : string
            Optional URL pattern to use for linking to indicators. If provided,
            the "[id]" will be replaced with the indicator id (dash-delimited).
            For example, "https://example.com/[id].html" will be replaced with
            "https://example.com/4-1-1.html".
        extra_metadata_fields : list
            Optional list of columns to include, which would not otherwise be
            included. Common choices are are units of measurement and series,
            which some users may prefer to see in the report.
        """
        Loggable.__init__(self, logging=logging)
        self.outputs = outputs
        self.indicator_url = indicator_url
        self.slugs = []
        self.languages = [] if languages is None else languages
        self.translation_helper = translation_helper
        self.extra_metadata_fields = [] if extra_metadata_fields is None else extra_metadata_fields
        self.metadata_field_store = None


    def get_metadata_field_store(self):
        """Analyzes the data in and compiles information about indicators.
        Returns
        -------
        dict
            Dict with metadata_field names keyed to dicts containing:
            - values (dict of values keyed to number of instances)
            - indicators (dict with indicator ids as keys)
            - filename (string, suitable for writing to disk)
            - name (string, the name of the metadata_field)            
        """
        
        metadata = {
                indicator_id: indicator.meta
                for (indicator_id, indicator)
                in self.get_all_indicators().items()
        }
                
        
        all_fields = {}
        allowed_fields=['reporting_status',
                'un_designated_tier'
                'computation_units',
                'data_non_statistical',
                'data_show_map',
                'graph_type',
                'national_geographical_coverage',
                'un_custodian_agency']
        boolean_fields=['data_non_statistical',
                        'data_show_map']
                        
        
        for indicator in metadata:
            fields = metadata.get(indicator)
            if "standalone" in fields:
                continue
            for field in fields:
                if field not in allowed_fields:
                    continue
                if field not in all_fields:
                    all_fields[field]= {
                        "filename": self.create_filename(field),
                        "indicators": {},
                        "name": field,
                        "values": {},
                    }
                value = fields[field]
                if field in boolean_fields:
                    if value == False:
                        value = ''
                if pd.isna(value) or value == '':
                    continue

                if value not in all_fields[field]["values"]:

                    all_fields[field]["values"][value] = {
                        "field": field,
                        "filename": self.create_filename(value, prefix='metadata-value--'),
                        "indicators": {},
                        "instances": 0,
                        "name": value
                }

                all_fields[field]["values"][value]["instances"] +=1

                if indicator not in all_fields[field]["values"][value]["indicators"]:
                    all_fields[field]['values'][value]['indicators'][indicator] = 0
                all_fields[field]['values'][value]['indicators'][indicator] +=1  

                all_fields[field]["indicators"][indicator]= value
        self.metadata_field_store = all_fields
        return self.metadata_field_store

    def get_all_indicators(self):
        indicators = {}
        for output in self.outputs:
            for indicator_id in output.get_indicator_ids():
                indicator = output.get_indicator_by_id(indicator_id)
                if not indicator.is_standalone() and not indicator.is_placeholder():
                    indicators[indicator_id] = indicator
        return indicators


    def create_filename(self, title, prefix='metadata--'):
        """Convert a title into a unique filename.
        Parameters
        ----------
        title : string
            A title representing the output
        Returns
        -------
        string
            The title converted into a unique *.html filename
        """
        slug = prefix + slugify(str(title))
        if slug in self.slugs:
            slug = slug
        if len(slug) > 100:
            slug = slug[0:100]
        self.slugs.append(slug)
        return slug + '.html'


    def group_metadata_field_store_by_indicator(self):
        store = self.get_metadata_field_store()
        grouped = {}
        for metadata_field in store:
            for indicator in store[metadata_field]['indicators']:
                if indicator not in grouped:
                    grouped[indicator] = {}
                grouped[indicator][metadata_field] = store[metadata_field]
        return grouped


    def get_metadata_field_link(self, metadata_field_info):
        return '<a href="{}">{}</a>'.format(
            metadata_field_info['filename'],
            metadata_field_info['name'],
        )


    def get_metadata_field_value_link(self, metadata_field_value_info):
        return '<a href="{}">{}</a>'.format(
            metadata_field_value_info['filename'],
            metadata_field_value_info['name'],
        )


    def translate(self, text, language, group=None):
        if self.translation_helper is None:
            return text
        else:
            default_group = 'data' if group is None else [group, 'data']
            return self.translation_helper.translate(text, language, default_group)


    def get_metadata_fields_dataframe(self):
        store = self.get_metadata_field_store()
        rows = []
        for metadata_field in store:

            num_indicators = len(store[metadata_field]['indicators'].keys())
            num_values = len(store[metadata_field]['values'].keys())

            # In some cases, a metadata_field may exist as a column but will have
            # no values. In these cases, we skip it.
            if num_values == 0:
                continue

            row = {
                'metadata_field': self.get_metadata_field_link(store[metadata_field]),
                'Number of indicators':  num_indicators,
                'Number of values': num_values,
            }
            for language in self.get_languages():
                row[language] = self.translate(metadata_field, language, metadata_field)
            rows.append(row)

        columns = ['metadata_field']
        columns.extend(self.get_languages())
        columns.extend(['Number of indicators', 'Number of values'])

        df = pd.DataFrame(rows, columns=columns)
        if not df.empty:
            df.sort_values(by=['metadata_field'], inplace=True)
        return df


    def get_languages(self):
        return self.languages


    def get_indicators_dataframe(self):
        grouped = self.group_metadata_field_store_by_indicator()
        store = self.get_metadata_field_store()
        rows = []
        for indicator in grouped:
            metadata_field_links = [self.get_metadata_field_link(metadata_field) for metadata_field in grouped[indicator].values()]
            if len(metadata_field_links) == 0:
                continue
            rows.append({
                'Indicator': self.get_indicator_link(indicator),
                'Reporting status': self.get_metadata_field_value_link(store['reporting_status']['values'][store['reporting_status']['indicators'][indicator]]) if indicator in store['reporting_status']['indicators'] else '',
                'UN designated tier': self.get_metadata_field_value_link(store['un_designated_tier']['values'][store['un_designated_tier']['indicators'][indicator]]) if indicator in store['un_designated_tier']['indicators'] else '',
                'Computation units': self.get_metadata_field_value_link(store['computation_units']['values'][store['computation_units']['indicators'][indicator]]) if indicator in store['computation_units']['indicators'] else '',
                'Data non-statistical': self.get_metadata_field_value_link(store['data_non_statistical']['values'][store['data_non_statistical']['indicators'][indicator]]) if indicator in store['data_non_statistical']['indicators'] else '',
                'Data show map': self.get_metadata_field_value_link(store['data_show_map']['values'][store['data_show_map']['indicators'][indicator]]) if indicator in store['data_show_map']['indicators'] else '',
                'Graph type': self.get_metadata_field_value_link(store['graph_type']['values'][store['graph_type']['indicators'][indicator]]) if indicator in store['graph_type']['indicators'] else '',
                'National geographical coverage': self.get_metadata_field_value_link(store['national_geographical_coverage']['values'][store['national_geographical_coverage']['indicators'][indicator]]) if indicator in store['national_geographical_coverage']['indicators'] else '',
                'UN custodian agency': self.get_metadata_field_value_link(store['un_custodian_agency']['values'][store['un_custodian_agency']['indicators'][indicator]]) if indicator in store['un_custodian_agency']['indicators'] else ''
            })
                
        df = pd.DataFrame(rows, columns=['Indicator', 'Reporting status', 'UN designated tier', 'Computation units', 'Data non-statistical', 'Data show map', 'Graph type', 'National geographical coverage', 'UN custodian agency'])
        if not df.empty:
            df.sort_values(by=['Indicator'], inplace=True)
        return df


    def get_metadata_field_dataframe(self, info):
        rows = []
        for value in info['values']:
            row = {
                'Value': self.get_metadata_field_value_link(info['values'][value]),
                'Number of indicators': len(info['values'][value]['indicators'].keys()),
            }
            for language in self.get_languages():
                row[language] = self.translate(value, language, info['name'])
            rows.append(row)

        columns = ['Value']
        columns.extend(self.get_languages())
        columns.extend(['Number of indicators'])

        df = pd.DataFrame(rows, columns=columns)
        if not df.empty:
            df.sort_values(by=['Value'], inplace=True)
        return df


    def get_metadata_field_indicator_dataframe(self, info):
        rows = []
        for indicator_id in info['indicators']:
            rows.append({
                'Indicator': self.get_indicator_link(indicator_id)
            })
        df = pd.DataFrame(rows)
        if not df.empty:
            df.sort_values(by=['Indicator'], inplace=True)
        return df


    def get_metadata_field_value_dataframe(self, info):
        rows = []
        for indicator_id in info['indicators']:
            rows.append({
                'Indicator': self.get_indicator_link(indicator_id)
            })
        df = pd.DataFrame(rows, columns=['Indicator'])
        if not df.empty:
            df.sort_values(by=['Indicator'], inplace=True)
        return df


    def get_metadata_field_report_template(self):
        return """
        <div role="navigation" aria-describedby="contents-heading">
            <h2 id="contents-heading">On this page</h2>
            <ul>
                <li><a href="#by-metadata_field">By metadata field</a></li>
                <li><a href="#by-indicator">By indicator</a></li>
            </ul>
        </div>
        <div>
            <h2 id="by-metadata_field" tabindex="-1">By metadata field</h2>
            {metadata_field_download}
            {metadata_field_table}
        </div>
        <div>
            <h2 id="by-indicator" tabindex="-1">By indicator</h2>
            {indicator_download}
            {indicator_table}
        </div>
        """


    def get_metadata_field_detail_template(self):
        return """
        <div role="navigation" aria-describedby="contents-heading">
            <h2 id="contents-heading">On this page</h2>
            <ul>
                <li><a href="#values-used">Values used in metadata field</a></li>
                <li><a href="#indicators-using">Indicators using metadata_field</a></li>
            </ul>
        </div>
        <div>
            <h2 id="values-used" tabindex="-1">Values used in metadata field</h2>
            {values_download}
            {values_table}
        </div>
        <div>
            <h2 id="indicators-using" tabindex="-1">Indicators using metadata field</h2>
            {indicators_download}
            {indicators_table}
        </div>
        """


    def get_metadata_field_value_detail_template(self):
        return """
        <div>
            {download}
            {table}
        </div>
        """


    def get_indicator_link(self, indicator_id):
        indicator_label = '#' + indicator_id
        if self.indicator_url is None:
            return indicator_label
        link = '<a href="{href}">{label}</a>'
        href = self.indicator_url.replace('[id]', indicator_id)
        return link.format(href=href, label=indicator_label)


    def remove_links_from_dataframe(self, df):
        return df.replace('<[^<]+?>', '', regex=True)
