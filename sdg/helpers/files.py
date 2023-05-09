from urllib.request import urlopen, Request
from shutil import copyfileobj


def fetch_remote_file(url, request_params=None):
    if request_params is None:
        request_params = {}
    return urlopen(Request(url, **request_params))


def download_remote_file(url, destination, request_params=None):
    downloaded_file = fetch_remote_file(url, request_params=request_params)
    with open(destination, 'wb') as out_file:
        copyfileobj(downloaded_file, out_file)


def read_file(location, request_params=None):
    if location.startswith('http'):
        file = fetch_remote_file(location, request_params=request_params)
        data = file.read().decode('utf-8')
    else:
        file = open(location)
        data = file.read()
    file.close()
    return data


def get_yaml_syntax_help(file):
    return f"""
    -----
    The file {file} could not be parsed because of a syntax error.
    YAML syntax errors often involve single/double quotes and/or colon (:).
    Sometimes you can find the problem by looking at the lines/columns mentioned above by "yaml.parser.ParserError".
    -----"""
