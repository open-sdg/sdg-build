# -*- coding: utf-8 -*-

import os
import shutil
import yaml
from sdg.translations import TranslationInputBase
from sdg.helpers.px import Px

class TranslationInputPx(TranslationInputBase):
    """This class imports translations from local or remote PX files."""

    def __init__(self, indicator_id_map=None, logging=None, request_params=None):
        """Constructor for the TranslationInputPx class.

        Parameters
        ----------
        indicator_id_map : dict
            A dict of indicator ids (dot-delimited) to PX file locations.
        """
        TranslationInputBase.__init__(self, logging=logging, request_params=None)
        self.indicator_id_map = self.get_indicator_id_map(indicator_id_map)


    def execute(self):
        TranslationInputBase.execute(self)
        for source, indicator_ids in self.indicator_id_map.items():
            pc_axis = self.fetch_file(source)
            px = Px(pc_axis)
            default_language = px.get_default_language()
            languages = px.get_languages()
            if languages is None:
                continue
            # Gather the data translations.
            variables = px.variables()
            translatable_variables = [v for v in variables if v != px.get_year_column_name()]
            for translatable_variable in translatable_variables:
                for language in languages:
                    suffix = ''
                    if language != default_language:
                        suffix = '[' + language + ']'
                    translated_variable = px.variable_get_translation_from_value(translatable_variable, language)
                    self.add_translation(language, translatable_variable, translatable_variable, translated_variable)
                    codes = px.codes(translatable_variable)
                    for code in codes:
                        value = px.value(code, translatable_variable, language)
                        self.add_translation(language, translatable_variable, code, value)
            # Gather the metadata translations.
            if not isinstance(indicator_ids, list):
                indicator_ids = [indicator_ids]
            for indicator_id in indicator_ids:
                indicator_id = indicator_id.replace('.', '-')
                translation_group = indicator_id + '-metadata'
                for language in languages:
                    try:
                        metadata_value = px.keyword('UNITS', language)
                        self.add_translation(language, translation_group, 'computation_units', metadata_value)
                    except:
                        pass
                    try:
                        metadata_value = px.keyword('NOTE', language)
                        self.add_translation(language, translation_group, 'data_footnote', metadata_value)
                    except:
                        pass
                    try:
                        metadata_value = px.keyword('TITLE', language)
                        self.add_translation(language, translation_group, 'graph_title', metadata_value)
                        self.add_translation(language, translation_group, 'indicator_name', metadata_value)
                    except:
                        pass


    def get_indicator_id_map(self, source):
        if isinstance(source, dict):
            return source
        elif isinstance(source, str):
            with open(source) as file:
                return yaml.load(file, Loader=yaml.FullLoader)
        else:
            raise Exception("The indicator_id_map parameter is not configured correctly.")
        return {}
