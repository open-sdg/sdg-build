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
        """Check to see if a particular string of text can be translated.

        Parameters
        ----------
        key : string
            The string of text that may be a translation key (or may not).

        Returns
        -------
        boolean
            True/False depending on whether the string is a translation key.
        """
        return key in self.translation_keys


    def translate(self, text, language, default_group=None):
        """Translate (if possible) a string of text into the given language.

        Parameters
        ----------
        text : string
            The string of text that may be a translation key (or may not).
        language : string
            The language code to translate into.
        default_group : None or string or List
            An optional "group" to add (if needed) to the text. For example, if
            text = "bar" and default_group = "foo", this function will first
            try "bar", and if nothing is found, try "foo.bar". Can also be a list
            of groups, which will all be attempted.

        Returns
        -------
        string
            Either the original text or a translated version of it.
        """
        # If the text is not a string, just return it.
        if not isinstance(text, str):
            return text
        # Add the default_group if necessary.
        key = text
        if not self.is_translation_key(key):
            if default_group is not None:
                if isinstance(default_group, str):
                    key = default_group + "." + key
                elif isinstance(default_group, list):
                    for group in default_group:
                        potential_key = group + "." + key
                        if self.is_translation_key(potential_key):
                            key = potential_key
                            break

        # If it is not translated, return the original.
        if not self.is_translation_key(key):
            return text
        # If it is not translated in this particular language, return original.
        if not language in self.translation_keys[key]:
            return text
        # If still here, return the translation.
        return self.translation_keys[key][language]
