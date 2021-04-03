from sdg.helpers import files
import sdmx
import os
from xml.etree import ElementTree as ET
from io import StringIO

cache = {}

def get_dsd_url():
    """Returns the remote URL to the global SDMX DSD for the SDGs."""
    return 'https://registry.sdmx.org/ws/public/sdmxapi/rest/datastructure/IAEG-SDGs/SDG/latest/?format=sdmx-2.1&detail=full&references=children'


def get_dsd(path=None, request_params=None):
    if path is None:
        path = get_dsd_url()
    if path in cache and 'get_dsd' in cache[path]:
        print('using cache')
        return cache[path]['get_dsd']
    if path.startswith('http'):
        filename = 'SDG_DSD.xml'
        files.download_remote_file(path, filename)
        msg = sdmx.read_sdmx(filename)
        os.remove(filename)
    else:
        msg = sdmx.read_sdmx(path)
    dsd_object = msg.structure[0]
    if path not in cache:
        cache[path] = {}
    cache[path]['get_dsd'] = dsd_object
    return dsd_object


def parse_xml(path=None, request_params=None):
    if path is None:
        path = get_dsd_url()
    if path in cache and 'parse_xml' in cache[path]:
        return cache[path]['parse_xml']

    xml = files.read_file(path, request_params=request_params)
    it = ET.iterparse(StringIO(xml))
    for _, el in it:
        if '}' in el.tag:
            el.tag = el.tag.split('}', 1)[1]
        # Strip namespaces from attributes too.
        for at in list(el.attrib.keys()):
            if '}' in at:
                newat = at.split('}', 1)[1]
                el.attrib[newat] = el.attrib[at]
                del el.attrib[at]
    if path not in cache[path]:
        cache[path] = {}
    cache[path]['parse_xml'] = it.root
    return it.root


def normalize_indicator_id(indicator_id):
    """Indicator ids sometimes have dashes or dots - standardize around dots."""
    return indicator_id.replace('-', '.')


def __get_series_from_series_code(series, dsd):
    try:
        dimension = next(item for item in dsd.dimensions if item.id == 'SERIES')
        code = next(item for item in dimension.local_representation.enumerated if item.id == series)
        return code
    except:
        return None


def __get_annotation_text(concept, annotation_title):
    try:
        annotation = next(item for item in concept.annotations if item.title == annotation_title)
        return str(annotation.text)
    except:
        return None


def get_indicator_id_from_series_code(series_code, dsd_path=None, request_params=None):
    """Convert a series code to an indicator ID (eg, "1.1.1")."""
    dsd = get_dsd(dsd_path, request_params=request_params)
    series = __get_series_from_series_code(series_code, dsd)
    return __get_annotation_text(series, 'Indicator')


def get_indicator_code_from_series_code(series_code, dsd_path=None, request_params=None):
    """Convert a series code to an indicator code (eg, "C010101")."""
    dsd = get_dsd(dsd_path, request_params=request_params)
    series = __get_series_from_series_code(series_code, dsd)
    return __get_annotation_text(series, 'IndicatorCode')


def get_indicator_title_from_series_code(series_code, dsd_path=None, request_params=None):
    """Convert a series code to an indicator title (eg, "Proportion of the...")."""
    dsd = get_dsd(dsd_path, request_params=request_params)
    series = __get_series_from_series_code(series_code, dsd)
    return __get_annotation_text(series, 'IndicatorTitle')


def __get_series_from_indicator_id(indicator_id, dsd):

    indicator_id = normalize_indicator_id(indicator_id)
    try:
        dimension = next(item for item in dsd.dimensions if item.id == 'SERIES')
        for code in dimension.local_representation.enumerated:
            candidate = normalize_indicator_id(__get_annotation_text(code, 'Indicator'))
            if candidate == indicator_id:
                return code
    except:
        return None


def __get_series_by_annotation_text(annotation_title, annotation_text, dsd):
    try:
        dimension = next(item for item in dsd.dimensions if item.id == 'SERIES')
        for code in dimension.local_representation.enumerated:
            candidate = __get_annotation_text(code, annotation_title)
            if candidate == annotation_text:
                return code
    except:
        return None


def get_series_code_from_indicator_id(indicator_id, dsd_path=None, request_params=None):
    """Convert an indicator ID (eg, "1.1.1") into a series code."""
    dsd = get_dsd(dsd_path, request_params=request_params)
    series = __get_series_from_indicator_id(indicator_id, dsd)
    try:
        return series.id
    except:
        return None


def get_series_code_from_indicator_code(indicator_code, dsd_path=None, request_params=None):
    """Convert an indicator code (eg, "C010101") into a series code."""
    dsd = get_dsd(dsd_path, request_params=request_params)
    series = __get_series_by_annotation_text('IndicatorCode', indicator_code, dsd)
    try:
        return series.id
    except:
        return None


def get_series_code_from_indicator_title(indicator_title, dsd_path=None, request_params=None):
    """Convert an indicator title (eg, "Proportion of the...") into a series code."""
    dsd = get_dsd(dsd_path, request_params=request_params)
    series = __get_series_by_annotation_text('IndicatorTitle', indicator_title, dsd)
    try:
        return series.id
    except:
        return None
