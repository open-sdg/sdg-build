# -*- coding: utf-8 -*-

import os
import json
from sdg.translations import TranslationOutputBase

class TranslationOutputJson(TranslationOutputBase):
    """A class for outputing translations in JSON format."""


    def execute(self):
        """Write the JSON translations file to disk. Overrides parent."""

        # Make sure the folder exists.
        output_folder = os.path.join(self.output_folder, 'translations')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, 'translations.json')

        output_json = json.dumps(self.input.get_translations())
        with open(output_path, 'w') as outfile:
            json.dump(output_json, outfile, sort_keys=True)
