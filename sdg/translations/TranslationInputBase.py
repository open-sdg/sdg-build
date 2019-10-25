# -*- coding: utf-8 -*-

import os

class TranslationInputBase:
    """A base class for importing translations."""


    def __init__(self, schema_path=''):
        """Create a new TranslationInputBase object

        Parameters
        ----------
        tbd : string
            Some description
        """

        some_stuff = 'foo'


    def execute(self):
        """Fetch translations from source."""
        raise NotImplementedError
