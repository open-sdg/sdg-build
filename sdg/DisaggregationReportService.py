import os
import sdg
import pandas as pd
from slugify import slugify

class DisaggregationReportService:
    """Report generation to document disaggregations in data."""


    def __init__(self, outputs, languages=None, translation_helper=None,
                 indicator_url=None, extra_disaggregations=None):
        """Constructor for the DisaggregationReportService class.

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
        extra_disaggregations : list
            Optional list of columns to include, which would not otherwise be
            included. Common choices are are units of measurement and series,
            which some users may prefer to see in the report.
        """
        self.outputs = outputs
        self.indicator_url = indicator_url
        self.slugs = []
        self.languages = [] if languages is None else languages
        self.translation_helper = translation_helper
        self.extra_disaggregations = [] if extra_disaggregations is None else extra_disaggregations
        self.disaggregation_store = None


    def get_disaggregation_store(self):
        """Analyzes the data in and compiles information about disaggregations.

        Returns
        -------
        dict
            Dict with disaggregation names keyed to dicts containing:
            - values (dict of values keyed to number of instances)
            - indicators (dict with indicator ids as keys)
            - filename (string, suitable for writing to disk)
            - name (string, the name of the disaggregation)
        """
        if self.disaggregation_store is not None:
            return self.disaggregation_store

        all_disaggregations = {}
        indicators = self.get_all_indicators()
        for indicator_id in indicators:
            if not indicators[indicator_id].is_statistical():
                continue
            if not indicators[indicator_id].is_complete():
                continue
            non_disaggregation_columns = indicators[indicator_id].options.get_non_disaggregation_columns()
            non_disaggregation_columns = [col for col in non_disaggregation_columns if col not in self.extra_disaggregations]
            for series in indicators[indicator_id].get_all_series():
                disaggregations = series.get_disaggregations()
                for disaggregation in disaggregations:
                    if disaggregation in non_disaggregation_columns:
                        continue
                    if disaggregation not in all_disaggregations:
                        all_disaggregations[disaggregation] = {
                            'values': {},
                            'indicators': {},
                            'filename': self.create_filename(disaggregation),
                            'name': disaggregation,
                        }
                    value = disaggregations[disaggregation]
                    if pd.isna(value) or value == '':
                        continue
                    if value not in all_disaggregations[disaggregation]['values']:
                        all_disaggregations[disaggregation]['values'][value] = {
                            'instances': 0,
                            'indicators': {},
                            'filename': self.create_filename(value, prefix='disaggregation-value--'),
                            'name': value,
                            'disaggregation': disaggregation,
                        }
                    all_disaggregations[disaggregation]['values'][value]['instances'] += 1
                    if indicator_id not in all_disaggregations[disaggregation]['values'][value]['indicators']:
                        all_disaggregations[disaggregation]['values'][value]['indicators'][indicator_id] = 0
                    all_disaggregations[disaggregation]['values'][value]['indicators'][indicator_id] += 1

                    all_disaggregations[disaggregation]['indicators'][indicator_id] = True
        self.disaggregation_store = all_disaggregations
        return self.disaggregation_store


    def get_all_indicators(self):
        indicators = {}
        for output in self.outputs:
            for indicator_id in output.get_indicator_ids():
                indicator = output.get_indicator_by_id(indicator_id)
                if not indicator.is_standalone():
                    indicators[indicator_id] = indicator
        return indicators


    def create_filename(self, title, prefix='disaggregation--'):
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
        slug = prefix + slugify(title)
        if slug in self.slugs:
            slug = slug + '_'
        if len(slug) > 100:
            slug = slug[0:100]
        self.slugs.append(slug)
        return slug + '.html'


    def group_disaggregation_store_by_indicator(self):
        store = self.get_disaggregation_store()
        grouped = {}
        for disaggregation in store:
            for indicator in store[disaggregation]['indicators']:
                if indicator not in grouped:
                    grouped[indicator] = {}
                grouped[indicator][disaggregation] = store[disaggregation]
        return grouped


    def get_disaggregation_link(self, disaggregation_info):
        return '<a href="{}">{}</a>'.format(
            disaggregation_info['filename'],
            disaggregation_info['name'],
        )


    def get_disaggregation_value_link(self, disaggregation_value_info):
        return '<a href="{}">{}</a>'.format(
            disaggregation_value_info['filename'],
            disaggregation_value_info['name'],
        )


    def translate(self, text, language, group=None):
        if self.translation_helper is None:
            return text
        else:
            default_group = 'data' if group is None else [group, 'data']
            return self.translation_helper.translate(text, language, default_group)


    def get_disaggregations_dataframe(self):
        store = self.get_disaggregation_store()
        rows = []
        for disaggregation in store:

            num_indicators = len(store[disaggregation]['indicators'].keys())
            num_values = len(store[disaggregation]['values'].keys())

            # In some cases, a disaggregation may exist as a column but will have
            # no values. In these cases, we skip it.
            if num_values == 0:
                continue

            row = {
                'Disaggregation': self.get_disaggregation_link(store[disaggregation]),
                'Number of indicators':  num_indicators,
                'Number of values': num_values,
            }
            for language in self.get_languages():
                row[language] = self.translate(disaggregation, language, disaggregation)
            rows.append(row)

        columns = ['Disaggregation']
        columns.extend(self.get_languages())
        columns.extend(['Number of indicators', 'Number of values'])

        df = pd.DataFrame(rows, columns=columns)
        if not df.empty:
            df.sort_values(by=['Disaggregation'], inplace=True)
        return df


    def get_languages(self):
        return self.languages


    def get_indicators_dataframe(self):
        grouped = self.group_disaggregation_store_by_indicator()
        rows = []
        for indicator in grouped:
            disaggregation_links = [self.get_disaggregation_link(disaggregation) for disaggregation in grouped[indicator].values()]
            if len(disaggregation_links) == 0:
                continue
            rows.append({
                'Indicator': self.get_indicator_link(indicator),
                'Disaggregations': ', '.join(disaggregation_links),
                'Number of disaggregations': len(disaggregation_links),
            })
        df = pd.DataFrame(rows, columns=['Indicator', 'Disaggregations', 'Number of disaggregations'])
        if not df.empty:
            df.sort_values(by=['Indicator'], inplace=True)
        return df


    def get_disaggregation_dataframe(self, info):
        rows = []
        for value in info['values']:
            row = {
                'Value': self.get_disaggregation_value_link(info['values'][value]),
                'Disaggregation combinations using this value': info['values'][value]['instances'],
                'Number of indicators': len(info['values'][value]['indicators'].keys()),
            }
            for language in self.get_languages():
                row[language] = self.translate(value, language, info['name'])
            rows.append(row)

        columns = ['Value']
        columns.extend(self.get_languages())
        columns.extend(['Disaggregation combinations using this value', 'Number of indicators'])

        df = pd.DataFrame(rows, columns=columns)
        if not df.empty:
            df.sort_values(by=['Value'], inplace=True)
        return df


    def get_disaggregation_indicator_dataframe(self, info):
        rows = []
        for indicator_id in info['indicators']:
            rows.append({
                'Indicator': self.get_indicator_link(indicator_id)
            })
        df = pd.DataFrame(rows)
        if not df.empty:
            df.sort_values(by=['Indicator'], inplace=True)
        return df


    def get_disaggregation_value_dataframe(self, info):
        rows = []
        for indicator_id in info['indicators']:
            rows.append({
                'Indicator': self.get_indicator_link(indicator_id),
                'Disaggregation combinations using this value': info['indicators'][indicator_id]
            })
        df = pd.DataFrame(rows, columns=['Indicator', 'Disaggregation combinations using this value'])
        if not df.empty:
            df.sort_values(by=['Indicator'], inplace=True)
        return df


    def get_disaggregation_report_template(self):
        return """
        <div class="list-group list-group-horizontal mb-4">
            <a class="list-group-item list-group-item-action" href="#by-disaggregation">By disaggregation</a>
            <a class="list-group-item list-group-item-action" href="#by-indicator">By indicator</a>
        </div>
        <div>
            <h2 id="by-disaggregation">By disaggregation</h2>
            {disaggregation_download}
            {disaggregation_table}
        </div>
        <div>
            <h2 id="by-indicator">By indicator</h2>
            {indicator_download}
            {indicator_table}
        </div>
        """


    def get_disaggregation_detail_template(self):
        return """
        <div class="list-group list-group-horizontal mb-4">
            <a class="list-group-item list-group-item-action" href="#values-used">Values used in disaggregation</a>
            <a class="list-group-item list-group-item-action" href="#indicators-using">Indicators using disaggregation</a>
        </div>
        <div>
            <h2 id="values-used">Values used in disaggregation</h2>
            {values_download}
            {values_table}
        </div>
        <div>
            <h2 id="indicators-using">Indicators using disaggregation</h2>
            {indicators_download}
            {indicators_table}
        </div>
        """


    def get_disaggregation_value_detail_template(self):
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
