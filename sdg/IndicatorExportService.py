import os
from zipfile import ZipFile

class IndicatorExportService:
    def __init__(self, site_directory):
        self.__site_directory = site_directory
        self.__zip_directory = "%s/zip" % site_directory
        self.__data_directory = "%s/data" % site_directory

    def export_all_indicator_data_as_zip_archive(self):
        self.__create_zip_folder_at_site_directory()
        csv_files = self.__get_all_indicator_csv_files()
        self.__create_zip_file("all_indicators.zip", csv_files)

    def __create_zip_folder_at_site_directory(self):
        os.mkdir("%s/zip" % self.__site_directory)

    def __get_all_indicator_csv_files(self):
        all_data_file_names = os.listdir(self.__data_directory)
        csv_data_file_names = []
        for each_data_file_name in all_data_file_names:
            if self.__file_is_csv(each_data_file_name):
                csv_data_file_names.append(each_data_file_name)

        csv_data_files = []
        for each_file_name in csv_data_file_names:
            csv_data_files.append({
                "file_name": each_file_name,
                "path": "%s/%s" % (self.__data_directory, each_file_name)
            })

        return csv_data_files

    def __file_is_csv(self, file_name):
        return file_name.endswith(".csv")

    def __create_zip_file(self, zip_file_name, files_to_include):
        zip_file = ZipFile("%s/%s" % (self.__zip_directory, zip_file_name), "w")

        for each_file in files_to_include:
            zip_file.write(each_file["path"], each_file["file_name"])

        zip_file.close()