# -*- coding: utf-8 -*-

import os
import json
from sdg.translations import TranslationOutputBase

class TranslationOutputJson(TranslationOutputBase):
    """A class for outputing translations in JSON format."""


    def write_translations(self, output_folder='translations', filename='translations.json'):
        """Write the JSON translations file to disk. Overrides parent."""

        # Make sure the folder exists.
        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, filename)

        output_json = self.input.get_translations()
        with open(output_path, 'w') as outfile:
            json.dump(output_json, outfile, sort_keys=True)
