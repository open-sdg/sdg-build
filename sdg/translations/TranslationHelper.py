# -*- coding: utf-8 -*-

import os
from sdg.translations import TranslationOutputBase

class TranslationHelper(TranslationOutputBase):
    """A class for helping with translation-related activities."""


    def __init__(self, inputs):
        """Constructor for the TranslationHelper.

        Parameters
        ----------
        inputs : list
            A list of TranslationInputBase objects
        """
        TranslationOutputBase.__init__(self, inputs)
        self.generate_translation_keys()


    def generate_translation_keys(self):
        """Convert the nested dict of translations into a flat map of keys."""
        keys = {}
        translations = self.input.get_translations()
        for language in translations:
            for group in translations[language]:
                for key in translations[language][group]:
                    value = translations[language][group][key]
                    flattened = group + "." + key
                    if flattened not in keys:
                        keys[flattened] = {}
                    keys[flattened][language] = value
        self.translation_keys = keys


    def is_translation_key(self, key):
        return key in self.translation_keys


    def translate(self, text, language):
        if not is_translation_key(text):
            return text
        if not language in self.translation_keys[text]:
            return text
        return self.translation_keys[text][language]
