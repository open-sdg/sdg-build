# -*- coding: utf-8 -*-

import os
import shutil
import yaml
from sdg.translations import TranslationInputBase

class TranslationInputYaml(TranslationInputBase):
    """This class imports translations from local YAML files.

    Assumptions about the format:
    1. There is a subfolder for each language code (eg, "en")
    2. Within each subfolder are YAML files containing translations.

    When importing, this class treats the YAML filename as the "group".
    """

    def __init__(self, source='translations'):
        """Constructor for the TranslationInputBase class.

        Parameters
        ----------
        source : string
            The folder containing the YAML files.
        """
        self.source = source
        self.translations = {}


    def parse_yaml(self, folder):
        """Walk through a folder looking for YAML files to parse.

        Parameters
        ----------
        folder : string
            The folder that contains the language subfolders.
        """
        # Safety code for missing folders.
        if not os.path.isdir(folder):
            print('Warning: Could not import translations from missing folder "%s".' % folder)
            return

        # Walk through the translation folder.
        for root, dirs, files in os.walk(folder):
            # Each subfolder is a language code.
            language = os.path.basename(root)
            if language == folder:
                continue
            # Loop through the YAML files.
            for file in files:
                # Each YAML filename is a group.
                file_parts = os.path.splitext(file)
                group = file_parts[0]
                extension = file_parts[1]
                if extension != '.yml':
                    continue
                with open(os.path.join(root, file), 'r', encoding='utf-8') as stream:
                    try:
                        yamldata = yaml.load(stream, Loader=yaml.FullLoader)
                        # Loop through the YAML data to add the translations.
                        if yamldata is not None:
                            for key in yamldata:
                                value = yamldata[key]
                                self.add_translation(language, group, key, value)
                    except Exception as exc:
                        print(exc)


    def execute(self):
        self.parse_yaml(self.source)
