# -*- coding: utf-8 -*-

import os
from sdg.translations import TranslationInputBase

class TranslationOutputBase:
    """A base class for exporting translations."""


    def __init__(self, inputs, output_folder='_site'):
        """Constructor for TranslationOutputBase.

        Parameters
        ----------
        inputs : list
            A list of TranslationInputBase objects
        output_folder : string
            A folder to put the output in
        """
        self.input = self.merge_inputs(inputs)
        self.output_folder = output_folder


    def execute():
        """Write the translation output to disk."""
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
