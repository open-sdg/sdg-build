# -*- coding: utf-8 -*-

import os
from git import Repo
from urllib.request import urlopen

class TranslationInputBase:
    """A base class for importing translations."""


    def __init__(self, source=''):
        """Constructor for the TranslationInputBase class.

        Parameters
        ----------
        source : string
            The source of the translations (see subclass for details)
        """
        self.source = source
        self.translations = {}


    def get_translations(self):
        """Get the translation data structure for this input"""
        return self.translations


    def add_language(self, language):
        """Add a language

        Parameters
        ----------
        language : string
            The language code to add
        """
        if language not in self.translations:
            self.translations[language] = {}


    def add_group(self, language, group):
        """Add a group

        Parameters
        ----------
        language : string
            The language code to add
        group : string
            The translation group to add
        """
        self.add_language(language)
        if group not in self.translations[language]:
            self.translations[language][group] = {}


    def add_translation(self, language, group, key, value):
        """Add a translation key/value

        Parameters
        ----------
        language : string
            The language code to add
        group : string
            The translation group to add
        key : string
            The translation key to add
        value : string
            The translated text to add
        """
        self.add_group(language, group)
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


    def clone_repo(self, repo_url, folder='temp', tag=None, branch=None):
        """Clone a Git repository and optionally switch to a branch/tag.

        Parameters
        ----------
        repo_url : string
            The Git URL for the repository (usually ends in .git)
        folder : string
            The name of the folder to put the files in
        branch : string
            The name of a Git branch to use
        tag : string
            The name of a Git tag to use (overrides "branch")
        """

        repo = Repo.clone_from(repo_url, folder)
        if branch:
            repo.git.checkout(branch)
        if tag:
            repo.git.checkout(tag)


    def execute(self):
        """Fetch translations from source."""
        raise NotImplementedError
