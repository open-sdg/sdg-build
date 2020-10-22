# -*- coding: utf-8 -*-

import os
import stat
import shutil
import yaml
from sdg.translations import TranslationInputYaml

class TranslationInputSdgTranslations(TranslationInputYaml):
    """This class imports translations from SDG Translations (or similar) repos.

    The "SDG Translations" style can be described like this:
    1. A Git repository (passed as the "source" parameter)
    2. Repo contains a folder called "translations"
    3. Each subfolder of "translations" is a language code (eg, "en")
    4. Within each subfolder are YAML files containing translations.

    When importing, this class treats the YAML filename as the "group".
    """

    def __init__(self, tag=None, branch=None, source='https://github.com/open-sdg/sdg-translations.git'):
        """Constructor for the TranslationInputBase class.

        Parameters
        ----------
        source : string
            The source of the translations (see subclass for details)
        """
        self.source = source
        self.tag = tag
        self.branch = branch
        self.translations = {}


    def execute(self):
        # Clean up from past runs.
        self.clean_up()
        # Clone the repository.
        self.clone_repo(repo_url=self.source, tag=self.tag, branch=self.branch)
        # Walk through the translation folder.
        translation_folder = os.path.join('temp', 'translations')
        self.parse_yaml(translation_folder)
        # Clean up afterwards.
        self.clean_up()


    def clean_up(self):
        # See https://stackoverflow.com/a/1889686/2436822
        def remove_readonly(func, path, excinfo):
            os.chmod(path, stat.S_IWRITE)
            func(path)

        # Remove the folder if it is there.
        try:
            shutil.rmtree('temp', onerror=remove_readonly)
        except OSError as e:
            pass
