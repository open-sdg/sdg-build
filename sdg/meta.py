# -*- coding: utf-8 -*-
"""
Created on Mon May 21 22:29:02 2018
@author: dashton
"""

import os
# Local modules
import yamlmd
import sdg
from sdg.path import input_path, output_path  # local package

def read_meta(inid, path_pattern='', git=True, src_dir='', git_data_dir=None):
    """Perform pre-processing for the metadata files"""
    status = True
    # Read and write paths may be different
    if path_pattern == '':
        meta_folder = 'meta'
        extension='.md'
    else:
        meta_folder = os.path.split(path_pattern)[0]
        extension='.'+path_pattern.split(".")[1]
    if inid is not None:
        fr = os.path.join(src_dir, meta_folder, inid + extension)
    else:
        fr = os.path.join(src_dir, meta_folder)
    meta_md = yamlmd.read_yamlmd(fr)
    meta = dict(meta_md[0])
    if git:
        git_update = sdg.git.get_git_updates(inid, src_dir=src_dir, git_data_dir=git_data_dir)
        for k in git_update.keys():
            meta[k] = git_update[k]
            
    meta['page_content'] = ''.join(meta_md[1])

    # Now look for all subfolders of the meta folder, which may contain
    # multilingual metadata, and add them as well.
    languages = next(os.walk(os.path.join(src_dir, meta_folder)))[1]
    for language in languages:
        i18n_fr = os.path.join(src_dir, meta_folder, language, inid + extension)
        if os.path.isfile(i18n_fr):
            i18n_meta_md = yamlmd.read_yamlmd(i18n_fr)
            i18n_meta = dict(i18n_meta_md[0])
            meta[language] = i18n_meta
            meta[language]['page_content'] = ''.join(i18n_meta_md[1])

    return meta
