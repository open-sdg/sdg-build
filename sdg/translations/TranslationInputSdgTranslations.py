# -*- coding: utf-8 -*-

import os
import shutil
import yaml
from git import Repo
from sdg.translations import TranslationInputBase

class TranslationInputSdgTranslations(TranslationInputBase):
    """This class imports translations from SDG Translations (or similar) repos.

    The "SDG Translations" style can be described like this:
    1. A Git repository (passed as the "source" parameter)
    2. Repo contains a folder called "translations"
    3. Each subfolder of "translations" is a language code (eg, "en")
    4. Within each subfolder are YAML files containing translations.

    When importing, this class treats the YAML filename as the "group".
    """


    def execute(self):
        # For convenience, default to the official SDG Translations repository.
        if self.source == '':
            self.source = 'https://github.com/open-sdg/sdg-translations.git'
        # Clean up from past runs.
        self.clean_up()
        # Clone the repository.
        Repo.clone_from(self.source, 'sdg-translations')
        # Walk through the translation folder.
        translation_folder = os.path.join('sdg-translations', 'translations')
        for root, dirs, files in os.walk(translation_folder):
            # Each subfolder is a language code.
            language = os.path.basename(root)
            if language == 'translations':
                continue
            # Loop through the YAML files.
            for file in files:
                # Each YAML filename is a group.
                file_parts = os.path.splitext(file)
                group = file_parts[0]
                extension = file_parts[1]
                if extension != '.yml':
                    continue
                with open(os.path.join(root, file), 'r') as stream:
                    try:
                        yamldata = yaml.load(stream, Loader=yaml.FullLoader)
                        # Loop through the YAML data to add the translations.
                        for key in yamldata:
                            value = yamldata[key]
                            self.add_translation(language, group, key, value)
                    except Exception as exc:
                        print(exc)
        self.clean_up()


    def clean_up(self):
        # Remove the folder if it is there.
        try:
            shutil.rmtree('sdg-translations')
        except OSError as e:
            pass
