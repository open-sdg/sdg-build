import os
import json
import glob
import re
from shutil import copyfile
from pathlib import Path

class IndicatorDownloadService:
    def __init__(self, output_folder=None):
        """Constructor for IndicatorDownloadService."""
        self.__output_folder = output_folder
        self.__index = {}


    def write_downloads(self, button_label, source_pattern, indicator_id_pattern, output_folder):
        if indicator_id_pattern is None:
            indicator_id_pattern = 'indicator_(.*)'
        output_folder = os.path.join('downloads', output_folder)
        original_output_folder = output_folder
        if self.__output_folder is not None:
            output_folder = os.path.join(self.__output_folder, output_folder)
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        for path_from in glob.glob(source_pattern):
            filename = os.path.basename(path_from)
            indicator_id = self.__get_indicator_id(indicator_id_pattern, filename)
            if indicator_id:
                path_to = os.path.join(output_folder, filename)
                copyfile(path_from, path_to)
                if indicator_id not in self.__index:
                    self.__index[indicator_id] = {
                        button_label: {}
                    }
                self.__index[indicator_id][button_label]['href'] = os.path.join(original_output_folder, filename)


    def __get_indicator_id(self, indicator_id_pattern, filename):
        without_extension = os.path.splitext(filename)[0]
        match = re.search(indicator_id_pattern, without_extension)
        if match:
            return match.group(1).replace('-', '.')
        else:
            print('Warning - indicator id not parsed from: ' + filename)
            return None


    def write_index(self):
        index_path = 'downloads'
        if self.__output_folder is not None:
            index_path = os.path.join(self.__output_folder, index_path)
        Path(index_path).mkdir(parents=True, exist_ok=True)
        filepath = os.path.join(index_path, 'indicator-downloads.json')
        with open(filepath, 'w') as fp:
            json.dump(self.__index, fp)
