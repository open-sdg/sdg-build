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

def read_meta(inid, git=True, src_dir=''):
    """Perform pre-processing for the metadata files"""
    status = True
    # Read and write paths may be different
    fr = input_path(inid, ftype='meta', src_dir=src_dir)

    meta_md = yamlmd.read_yamlmd(fr)
    meta = dict(meta_md[0])
    if git:
        git_update = sdg.git.get_git_updates(inid, src_dir=src_dir)
        for k in git_update.keys():
            meta[k] = git_update[k]
            
    meta['page_content'] = ''.join(meta_md[1])

    # Now look for all subfolders of the meta folder, which may contain
    # multilingual metadata, and add them as well.
    meta_folder = input_path(None, ftype='meta', src_dir=src_dir)
    languages = next(os.walk(meta_folder))[1]
    for language in languages:
        i18n_fr = os.path.join(meta_folder, language, inid + '.md')
        if os.path.isfile(i18n_fr):
            i18n_meta_md = yamlmd.read_yamlmd(i18n_fr)
            i18n_meta = dict(i18n_meta_md[0])
            meta[language] = i18n_meta
            meta[language]['page_content'] = ''.join(i18n_meta_md[1])

    return meta