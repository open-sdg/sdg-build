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


def print_yaml_syntax_help(file):
    print('-----')
    print(f'The file at {file} could not be parsed because of a syntax error.')
    print('YAML syntax errors often involve single/double quotes and/or colons (:).')
    print('Sometimes you can find the problem by looking at the lines/columns mentioned in the following raw error message:')
    print('------')
