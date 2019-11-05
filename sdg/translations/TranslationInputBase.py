# -*- coding: utf-8 -*-

import os
from urllib.request import urlopen
from git import Repo

class TranslationInputBase:
    """A base class for importing translations."""


    def __init__(self, source=''):
        self.source = source
        self.translations = {}


    def add_language(self, language):
        if language not in self.translations:
            self.translations[language] = {}


    def add_group(self, language, group):
        self.add_language(language)
        if group not in self.translations[language]:
            self.translations[language][group] = {}


    def add_translation(self, language, group, key, value):
        self.add_group(language, group)
        if key not in self.translations[language][group]:
            self.translations[language][group][key] = value


    def fetch_file(self, location):
        """Fetch a file, either on disk, or on the Internet.

        Parameters
        ----------
        location : String
            Either an http address, or a path on disk
        """
        file = None
        data = None
        if location.startswith('http'):
            file = urlopen(location)
            data = file.read().decode('utf-8')
        else:
            file = open(location)
            data = file.read()
        file.close()
        return data


    def clone_repo(self, git_url):
        repo = Repo.clone_from(git_url, 'temp')


    def execute(self):
        """Fetch translations from source."""
        raise NotImplementedError
