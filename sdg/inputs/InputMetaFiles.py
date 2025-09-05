import os
import re
import git
import pandas as pd
from sdg.inputs import InputFiles

class InputMetaFiles(InputFiles):
    """Sources of SDG metadata that are local files."""

    def __init__(self, path_pattern='', git=True, git_data_dir='data',
                 git_data_filemask='indicator_*.csv', metadata_mapping=None,
                 logging=None, column_map=None, code_map=None):
        """Constructor for InputMetaFiles.

        Keyword arguments:
        path_pattern -- path (glob) pattern describing where the files are
        git -- whether to use git information for dates in the metadata
        git_data_dir -- location of folder containing git data for dates
        git_data_filemask -- a pattern for data filenames, where "*" is the
          indicator id. Alternatively, each indicator can contain a metadata
          field called "data_filename" with the name of the data file for
          that indicator.
        metadata_mapping -- a dict mapping human-readable labels to machine keys
          or a path to a CSV file
        """
        InputFiles.__init__(self, path_pattern, logging=logging,
            column_map=column_map, code_map=code_map)
        self.git = git
        self.git_data_dir = git_data_dir
        self.git_data_filemask = git_data_filemask
        self.metadata_mapping = metadata_mapping


    def execute(self, indicator_options):
        InputFiles.execute(self, indicator_options)
        """Get the metadata from the files."""
        self.load_metadata_mapping()
        indicator_map = self.get_indicator_map()
        for inid in indicator_map:
            meta = self.read_meta(indicator_map[inid])
            self.apply_metadata_mapping(meta)
            self.fix_booleans(meta)
            name = meta['indicator_name'] if 'indicator_name' in meta else None
            self.add_indicator(inid, name=name, meta=meta, options=indicator_options)


    def read_meta(self, filepath):
        meta = self.read_meta_at_path(filepath)
        self.add_language_folders(meta, filepath)
        if self.git:
            self.add_git_dates(meta, filepath)
        return meta


    def read_meta_at_path(self, filepath):
        """This must be implemented by child classes."""
        raise NotImplementedError


    def add_language_folders(self, meta, filepath):
        meta_folder = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        languages = next(os.walk(meta_folder))[1]
        for language in languages:
            translated_filepath = os.path.join(meta_folder, language, filename)
            if os.path.isfile(translated_filepath):
                translated_meta = self.read_meta_at_path(translated_filepath)
                self.apply_metadata_mapping(translated_meta)
                self.fix_booleans(translated_meta)
                meta[language] = translated_meta
                if meta[language]:
                    for field in meta[language]:
                        if (not meta[language][field]) and (field in meta):
                            # Fallback to source language for missing values.
                            meta[language][field] = meta[field]


    def fix_booleans(self, meta):
        for key in meta:
            value = meta[key]
            if isinstance(value, str):
                if value.lower() == 'true':
                    meta[key] = True
                elif value.lower() == 'false':
                    meta[key] = False


    def add_git_dates(self, meta, filepath):
        git_update = self.get_git_dates(meta, filepath)
        for k in git_update.keys():
            meta[k] = git_update[k]


    def get_git_dates(self, meta, filepath):
        updates = {}
        updates['national_metadata_updated_date'] = self.get_git_date(filepath)
        if 'data_filename' in meta:
            data_filename = meta['data_filename']
        else:
            indicator_id = self.convert_path_to_indicator_id(filepath)
            data_filename = self.git_data_filemask.replace('*', indicator_id)
        src_dir = os.path.dirname(os.path.dirname(self.path_pattern))
        data_filepath = os.path.join(src_dir, self.git_data_dir, data_filename)
        if os.path.isfile(data_filepath):
            updates['national_data_updated_date'] = self.get_git_date(data_filepath)

        return updates


    def get_git_date(self, filepath):
        """Change into the working directory of the file (it might be a submodule)
        and get the latest git history"""
        folder = os.path.split(filepath)[0]

        repo = git.Repo(folder, search_parent_directories=True)
        # Need to translate relative to the repo root (this may be a submodule)
        repo_dir = os.path.relpath(repo.working_dir, os.getcwd())
        filepath = os.path.relpath(filepath, repo_dir)
        commit = next(repo.iter_commits(paths=filepath, max_count=1))
        return str(commit.committed_datetime.date())


    def load_metadata_mapping(self):
        mapping = None
        if self.metadata_mapping is None:
            mapping = {}
        elif isinstance(self.metadata_mapping, dict):
            mapping = self.metadata_mapping
        # Otherwise assume it is a path to a file.
        else:
            extension = os.path.splitext(self.metadata_mapping)[1]
            if extension.lower() == '.csv':
                mapping = pd.read_csv(self.metadata_mapping, header=None, index_col=0, squeeze=True).to_dict()

        if mapping is None:
            raise Exception('Format of metadata_mapping should be a dict or a path to a CSV file.')

        self.metadata_mapping = mapping


    def apply_metadata_mapping(self, metadata):
        for human_key in self.metadata_mapping:
            machine_key = self.metadata_mapping[human_key]
            if human_key in metadata and human_key != machine_key:
                metadata[machine_key] = metadata[human_key]
                del metadata[human_key]
