# -*- coding: utf-8 -*-

import os
from sdg.translations import TranslationInputBase

class TranslationOutputBase:
    """A base class for exporting translations."""


    def __init__(self, inputs):
        """Constructor for TranslationOutputBase.

        Parameters
        ----------
        inputs : list
            A list of TranslationInputBase objects
        """
        self.input = self.merge_inputs(inputs)


    def write_translations(self, language=None, output_folder='translations', filename='translations.json'):
        """Write the translation output to disk.

        Parameters
        ----------
        language : string
            If specified, limit the output to a particular language only.
        output_folder : string
            The folder to put the file in.
        filename : string
            The name of the file to create.
        """
        raise NotImplementedError


    def merge_inputs(self, inputs):
        """Take the results of many inputs and merge into a single input.

        Parameters
        ----------
        inputs : list
            A list of TranslationInputBase objects
        """
        merged = TranslationInputBase()
        for input in inputs:
            # Fetch the input.
            input.execute()
            # Merge the results.
            translations = input.get_translations()
            for language in translations:
                for group in translations[language]:
                    for key in translations[language][group]:
                        value = translations[language][group][key]
                        merged.add_translation(language, group, key, value)
        return merged
