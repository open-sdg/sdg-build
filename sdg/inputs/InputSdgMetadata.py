# -*- coding: utf-8 -*-

import os
import stat
import shutil
import yaml
from git import Repo
from sdg.inputs import InputBase

class InputSdgMetadata(InputBase):
    """This class imports metadata from SDG Metadata (or similar) repos.

    The "SDG Metadata" style can be described like this:
    1. A Git repository (passed as the "source" parameter)
    2. Repo contains a folder called "translations" (can be configured)
    3. Each subfolder of "translations" is a language code (eg, "en")
    4. Within each subfolder are YAML files containing metadata.
    5. The metadata files are named according to the indicator (eg, 1-1-1.yml).

    Here is the "canonical" SDG Metadata repo, for reference, which is the
    Worldbank project to translate the global SDG Metadata:
    https://github.com/worldbank/sdg-metadata
    """

    def __init__(self, tag=None, branch=None, source='https://github.com/worldbank/sdg-metadata.git',
                 folder='translations', default_language='en', logging=None):
        """Constructor for the InputSdgMetadata class.

        Parameters
        ----------
        tag : string
            The tag to use on the remote Git repository
        branch : string
            The branch to use on the remote Git repository (alias for 'tag')
        source : string
            The Git URL for cloning the repository (should end with .git)
        folder : string
            The subfolder inside the repository to use
        default_language : string
            The language which should be considered the default.
        """
        InputBase.__init__(self, logging=logging)
        self.tag = tag
        self.branch = branch
        self.source = source
        self.folder = folder
        self.default_language = default_language


    def execute(self, indicator_options):
        self.debug('Starting metadata input: {class_name}')
        # Clean up from past runs.
        self.clean_up()
        # Clone the repository.
        self.clone_repo(repo_url=self.source, tag=self.tag, branch=self.branch)
        # Walk through the translation folder.
        translation_folder = os.path.join('temp', self.folder)
        indicators = self.parse_yaml(translation_folder)
        for inid in indicators:
            self.add_indicator(inid, meta=indicators[inid], options=indicator_options)
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


    def parse_yaml(self, folder):
        """Walk through a folder looking for YAML files to parse.

        Parameters
        ----------
        folder : string
            The folder that contains the language subfolders.
        """
        # Safety code for missing folders.
        if not os.path.isdir(folder):
            self.warn('Warning: Could not import metadata from missing folder "{folder}".', folder=folder)
            return

        indicators = {}

        # Walk through the translation folder.
        for root, dirs, files in os.walk(folder):
            # Each subfolder is a language code.
            language = os.path.basename(root)
            if language == folder:
                continue
            # Loop through the YAML files.
            for file in files:
                # Each YAML filename is an indicator id.
                file_parts = os.path.splitext(file)
                indicator_id = file_parts[0]
                extension = file_parts[1]
                if extension != '.yml':
                    continue
                if indicator_id not in indicators:
                    indicators[indicator_id] = {}
                with open(os.path.join(root, file), 'r', encoding='utf-8') as stream:
                    try:
                        yamldata = yaml.load(stream, Loader=yaml.FullLoader)
                        for key in yamldata:
                            value = yamldata[key]
                            if language == self.default_language:
                                indicators[indicator_id][key] = value
                            else:
                                if language not in indicators[indicator_id]:
                                    indicators[indicator_id][language] = {}
                                indicators[indicator_id][language][key] = value
                    except Exception as exc:
                        print(exc)

        return indicators
