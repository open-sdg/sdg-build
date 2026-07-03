# -*- coding: utf-8 -*-

import os
import shutil
import yaml
from sdg.translations import TranslationInputBase
from sdg.helpers.px import Px

class TranslationInputPx(TranslationInputBase):
    """This class imports translations from local or remote PX files."""

    def __init__(self,
        indicator_id_map=None,
        logging=None,
        request_params=None,
        indicator_options=None,
        meta_map=None,
    ):
        """Constructor for the TranslationInputPx class.

        Parameters
        ----------
        indicator_id_map : dict
            A dict of indicator ids (dot-delimited) to PX file locations.
        """
        TranslationInputBase.__init__(self,
            logging=logging,
            request_params=request_params,
            indicator_options=indicator_options,
        )
        self.indicator_id_map = self.get_indicator_id_map(indicator_id_map)
        self.meta_map = self.get_meta_map(meta_map)


    def execute(self):
        TranslationInputBase.execute(self)

        for source, indicator_ids in self.indicator_id_map.items():
            pc_axis = self.fetch_file(self.clean_remote_urls(source))
            px = Px(pc_axis)
            has_series = px.data_has_series()
            has_units = px.data_has_units()
            has_indicator_options = self.indicator_options is not None
            default_language = px.get_default_language()
            languages = px.get_languages()
            if languages is None:
                continue
            # Gather the data translations.
            variables = px.variables()
            translatable_variables = [v for v in variables if v != px.get_year_column_name()]
            for translatable_variable in translatable_variables:
                # We have to treat the unit and series column especially,
                # because they get renamed during the data input.
                renamed_variable = translatable_variable
                if has_indicator_options and has_series and translatable_variable == px.get_series_column_name():
                    renamed_variable = self.indicator_options.get_series_column()
                if has_indicator_options and has_units and translatable_variable == px.get_units_column_name():
                    renamed_variable = self.indicator_options.get_unit_column()
                for language in languages:
                    translated_variable = px.variable_get_translation_from_value(translatable_variable, language)
                    self.add_translation(language, renamed_variable, renamed_variable, translated_variable)
                    codes = px.codes(translatable_variable)
                    for code in codes:
                        value = px.value(code, translatable_variable, language)
                        self.add_translation(language, renamed_variable, code, value)
            # Gather the metadata translations.
            if not isinstance(indicator_ids, list):
                indicator_ids = [indicator_ids]
            for indicator_id in indicator_ids:
                indicator_id = indicator_id.replace('.', '-')
                translation_group = indicator_id + '-metadata'
                for language in languages:
                    try:
                        if not (px.data_has_units() and 'UNITS' in px.keywords()):
                            metadata_value = px.keyword('UNITS', language)
                            if isinstance(metadata_value, dict) and 'TABLE' in metadata_value:
                                metadata_value = metadata_value['TABLE']
                            if isinstance(metadata_value, str):
                                self.add_translation(language, translation_group, 'computation_units', metadata_value)
                    except:
                        pass
                    try:
                        if 'NOTEX' in px.keywords():
                            metadata_value = px.keyword('NOTEX', language)
                            notex_header = ''
                            notex_footer = []
                            if isinstance(metadata_value, str):
                                notex_header = metadata_value
                            elif isinstance(metadata_value, dict):
                                untranslated_value = px.keyword('NOTEX')
                                value_keys = untranslated_value.keys()
                                for value_key in value_keys:
                                    if value_key == 'TABLE':
                                        notex_header = metadata_value['TABLE']
                                    else:
                                        notex_footer.append(value_key)
                            if notex_header: 
                                self.add_translation(language, translation_group, 'page_content', notex_header)
                            if notex_footer:
                                for notex_field in notex_footer:
                                    untranslated_variable = notex_field
                                    translated_variable = px.variable_get_translation_from_value(untranslated_variable, language)
                                    self.add_translation(language, translation_group, 'footer_field_label-' + untranslated_variable, translated_variable)
                                    self.add_translation(language, translation_group, 'footer_field_value-' + untranslated_variable, metadata_value[translated_variable])
                    except:
                        pass
                    try:
                        metadata_value = px.keyword('INFO', language)
                        self.add_translation(language, translation_group, 'graph_title', metadata_value)
                        self.add_translation(language, translation_group, 'indicator_name', metadata_value)
                    except:
                        pass
                    for mapped_key in self.meta_map:
                        try:
                            metadata_value = px.keyword(mapped_key, language)
                            if isinstance(metadata_value, str):
                                self.add_translation(language, translation_group, mapped_key, metadata_value)
                            elif isinstance(metadata_value, dict):
                                untranslated_value = px.keyword(mapped_key)
                                value_keys = untranslated_value.keys()
                                for value_key in value_keys:
                                    if value_key == 'TABLE':
                                        self.add_translation(language, translation_group, mapped_key, metadata_value['TABLE'])
                                    else:
                                        # We assume this is a variable.
                                        untranslated_variable = value_key
                                        translated_variable = px.variable_get_translation_from_value(untranslated_variable, language)
                                        self.add_translation(language, translation_group, mapped_key + '-' + value_key, metadata_value[translated_variable])
                        except Exception as e:
                            print(e)
                            pass

    def get_meta_map(self, source):
        map = {}
        if isinstance(source, str):
            with open(source) as file:
                map = yaml.load(file, Loader=yaml.FullLoader)
        if isinstance(map, dict):
            # Always include NOTE mappeed to itself.
            map['NOTE'] = 'NOTE'
            return map
        else:
            raise Exception("The meta_map parameter is not configured correctly.")


    def get_indicator_id_map(self, source):
        if isinstance(source, dict):
            return source
        elif isinstance(source, str):
            with open(source) as file:
                return yaml.load(file, Loader=yaml.FullLoader)
        else:
            raise Exception("The indicator_id_map parameter is not configured correctly.")
        return {}

    def clean_remote_urls(self, location):
        if location.startswith('http'):
            # Because the PXWeb interface is known to add
            # ":443" to exported URLs, we automatically remove
            # it here, as a onvenience.
            location = location.replace(':443', '')
        return location
