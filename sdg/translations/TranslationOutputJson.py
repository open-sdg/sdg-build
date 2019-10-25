# -*- coding: utf-8 -*-

import os
import json
from sdg.translations import TranslationOutputBase

class TranslationOutputJson(TranslationOutputBase):
    """A class for outputing translations in JSON format."""


    def execute(self, output_folder='translations', filename='all.json'):
        """Write the JSON translations file to disk. Overrides parent.

        Parameters
        ----------
        output_folder : string
            The folder to write the translation output in
        filename : string
            The filename for writing the translation output
        """

        # Make sure the folder exists.
        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, filename)

        output = {}

        output_json = json.dumps(output)
        with open(output_path, 'w', encoding='utf-8') as outfile:
            outfile.write(output_json)
