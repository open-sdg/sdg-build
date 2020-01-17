# -*- coding: utf-8 -*-

import os
import shutil
import pandas as pd
from sdg.translations import TranslationInputBase

class TranslationInputCsv(TranslationInputBase):
    """This class imports translations from local CSV files.
    Assumptions about the format:
    1. There is a subfolder for each language code (eg, "en")
    2. Within each subfolder are CSV files containing translations.
    When importing, this class treats the CSV filename as the "group".
    """

    def __init__(self, source='translations'):
        """Constructor for the TranslationInputBase class.
        Parameters
        ----------
        source : string
            The folder containing the CSV files.
        """
        self.source = source
        self.translations = {}


    def parse_csv(self, folder):
        """Walk through a folder looking for CSV files to parse.
        Parameters
        ----------
        folder : string
            The folder that contains the language subfolders.
        """
        # Walk through the translation folder.
        for root, dirs, files in os.walk(folder):
            # Each subfolder is a language code.
            language = os.path.basename(root)
            if language == folder:
                continue
            # Loop through the CSV files.
            for file in files:
                # Each CSV filename is a group.
                file_parts = os.path.splitext(file)
                group = file_parts[0]
                extension = file_parts[1]
                if extension != '.csv':
                    continue
                csvdata = pd.read_csv(os.path.join(root, file), header=None)
                # Loop through the CSV data to add the translations.
                for index, row in csvdata.iterrows():
                    key=row[0]
                    value=row[1]
                    self.add_translation(language, group, key, value)

    def execute(self):
        self.parse_csv(self.source)
