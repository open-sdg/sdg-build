import os
import sdg
import pandas as pd
from slugify import slugify
from sdg.Loggable import Loggable
import json

class DisaggregationReportService(Loggable):
    """Report generation to document disaggregations in data."""


    def __init__(self, outputs, languages=None, translation_helper=None,
                 indicator_url=None, extra_disaggregations=None, logging=None):
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
        """
        Loggable.__init__(self, logging=logging)
        self.outputs = outputs
        self.indicator_url = indicator_url
        self.slugs = []
        self.languages = [] if languages is None else languages
        self.translation_helper = translation_helper
        self.indicator_store = None


    def get_indicator_store(self):
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

        all_properties = {}
        indicators = self.get_all_indicators()
        print(indicators)
        for indicator_id in indicators:
            for series in indicators[indicator_id].get_all_series():
                properties = ['data_non_statistical']
                for property in properties:
                    if property not in all_properties:
                        all_properties[property] = {
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
        print(all_disaggregations)
        a_file = open("all_disaggregations.json", "w")
        json.dump(all_disaggregations, a_file)
        a_file.close()
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
