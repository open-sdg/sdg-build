from sdg.helpers import files
import sdmx
import os
from xml.etree import ElementTree as ET
from io import StringIO
import pandas as pd

cache = {}

def get_dsd_url():
    """Returns the remote URL to the global SDMX DSD for the SDGs."""
    return 'https://registry.sdmx.org/ws/public/sdmxapi/rest/datastructure/IAEG-SDGs/SDG/latest/?format=sdmx-2.1&detail=full&references=children'


def get_sdmx_message(path=None, request_params=None):
    if path is None:
        path = get_dsd_url()
    if path in cache and 'get_sdmx_message' in cache[path]:
        return cache[path]['get_sdmx_message']
    if path.startswith('http'):
        filename = 'SDG_MESSAGE.xml'
        files.download_remote_file(path, filename)
        msg = sdmx.read_sdmx(filename)
        os.remove(filename)
    else:
        msg = sdmx.read_sdmx(path)
    if path not in cache:
        cache[path] = {}
    cache[path]['get_sdmx_message'] = msg
    return msg


def get_dsd(path=None, request_params=None):
    if path is None:
        path = get_dsd_url()
    if path in cache and 'get_dsd' in cache[path]:
        return cache[path]['get_dsd']
    msg = get_sdmx_message(path=path, request_params=request_params)
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
    if path not in cache:
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
    matches = []
    try:
        for item in concept.annotations:
            if item.title == annotation_title:
                matches.append(str(item.text))
    except:
        pass
    return matches


def get_indicator_id_from_series_code(series_code, dsd_path=None, request_params=None):
    """Convert a series code to an indicator ID (eg, "1.1.1")."""
    dsd = get_dsd(dsd_path, request_params=request_params)
    series = __get_series_from_series_code(series_code, dsd)
    matches = __get_annotation_text(series, 'Indicator')
    return matches[0] if len(matches) > 0 else None


def get_indicator_code_from_series_code(series_code, dsd_path=None, request_params=None):
    """Convert a series code to an indicator code (eg, "C010101")."""
    dsd = get_dsd(dsd_path, request_params=request_params)
    series = __get_series_from_series_code(series_code, dsd)
    matches = __get_annotation_text(series, 'IndicatorCode')
    return matches[0] if len(matches) > 0 else None


def get_indicator_title_from_series_code(series_code, dsd_path=None, request_params=None):
    """Convert a series code to an indicator title (eg, "Proportion of the...")."""
    dsd = get_dsd(dsd_path, request_params=request_params)
    series = __get_series_from_series_code(series_code, dsd)
    matches = __get_annotation_text(series, 'IndicatorTitle')
    return matches[0] if len(matches) > 0 else None


def __get_series_from_indicator_id(indicator_id, dsd):

    indicator_id = normalize_indicator_id(indicator_id)
    try:
        dimension = next(item for item in dsd.dimensions if item.id == 'SERIES')
        for code in dimension.local_representation.enumerated:
            matches = __get_annotation_text(code, 'Indicator')
            for annotation_text in matches:
                candidate = normalize_indicator_id(annotation_text)
                if candidate == indicator_id:
                    return code
    except:
        return None


def __get_all_series_from_indicator_id(indicator_id, dsd):

    indicator_id = normalize_indicator_id(indicator_id)
    codes = []
    try:
        dimension = next(item for item in dsd.dimensions if item.id == 'SERIES')
        for code in dimension.local_representation.enumerated:
            matches = __get_annotation_text(code, 'Indicator')
            for annotation_text in matches:
                candidate = normalize_indicator_id(annotation_text)
                if candidate == indicator_id:
                    codes.append(code)
    except:
        pass
    return codes


def __get_series_by_annotation_text(annotation_title, annotation_text, dsd):
    try:
        dimension = next(item for item in dsd.dimensions if item.id == 'SERIES')
        for code in dimension.local_representation.enumerated:
            matches = __get_annotation_text(code, annotation_title)
            for candidate in matches:
                if candidate == annotation_text:
                    return code
    except:
        return None


def __get_all_series_by_annotation_text(annotation_title, annotation_text, dsd):
    codes = []
    try:
        dimension = next(item for item in dsd.dimensions if item.id == 'SERIES')
        for code in dimension.local_representation.enumerated:
            matches = __get_annotation_text(code, annotation_title)
            for candidate in matches:
                if candidate == annotation_text:
                    codes.append(code)
    except:
        pass
    return codes


def get_series_code_from_indicator_id(indicator_id, dsd_path=None, request_params=None):
    """Convert an indicator ID (eg, "1.1.1") into a series code."""
    dsd = get_dsd(dsd_path, request_params=request_params)
    series = __get_series_from_indicator_id(indicator_id, dsd)
    try:
        return series.id
    except:
        return None


def get_all_series_codes_from_indicator_id(indicator_id, dsd_path=None, request_params=None):
    """Convert an indicator ID (eg, "1.1.1") into a multiple series codes."""
    dsd = get_dsd(dsd_path, request_params=request_params)
    serieses = __get_all_series_from_indicator_id(indicator_id, dsd)
    try:
        return [series.id for series in serieses]
    except:
        return []


def get_series_code_from_indicator_code(indicator_code, dsd_path=None, request_params=None):
    """Convert an indicator code (eg, "C010101") into a series code."""
    dsd = get_dsd(dsd_path, request_params=request_params)
    series = __get_series_by_annotation_text('IndicatorCode', indicator_code, dsd)
    try:
        return series.id
    except:
        return None


def get_all_series_codes_from_indicator_code(indicator_code, dsd_path=None, request_params=None):
    """Convert an indicator code (eg, "C010101") into a multiple series codes."""
    dsd = get_dsd(dsd_path, request_params=request_params)
    serieses = __get_all_series_by_annotation_text('IndicatorCode', indicator_code, dsd)
    try:
        return [series.id for series in serieses]
    except:
        return []


def get_series_code_from_indicator_title(indicator_title, dsd_path=None, request_params=None):
    """Convert an indicator title (eg, "Proportion of the...") into a series code."""
    dsd = get_dsd(dsd_path, request_params=request_params)
    series = __get_series_by_annotation_text('IndicatorTitle', indicator_title, dsd)
    try:
        return series.id
    except:
        return None


def get_all_series_codes_from_indicator_title(indicator_title, dsd_path=None, request_params=None):
    """Convert an indicator title (eg, "Proportion of the...") into a multiple series codes."""
    dsd = get_dsd(dsd_path, request_params=request_params)
    serieses = __get_all_series_by_annotation_text('IndicatorTitle', indicator_title, dsd)
    try:
        return [series.id for series in serieses]
    except:
        return []


def get_unit_code_from_series_code(series_code, dsd_path=None, request_params=None, fallback='NUMBER'):
    """Perform a best-effort imprecise conversion of a series code into a unit code."""
    dsd = get_dsd(dsd_path, request_params=request_params)
    try:
        series = __get_series_from_series_code(series_code, dsd)
        series_name = str(series.name).lower()
        unit_attribute = next(item for item in dsd.attributes if item.id == 'UNIT_MEASURE')
    except:
        return fallback
    percent_code = None

    for unit in unit_attribute.local_representation.enumerated:
        unit_name = str(unit.name).lower()
        if unit_name == fallback.lower():
            # Skip the fallback in case it appears in other unit names and causes
            # a false match (as "NUMBER" does).
            continue
        if 'percent' in unit_name:
            percent_code = unit.id
        if unit_name in series_name:
            return unit.id

    # Some additional fallbacks.
    if 'proportion' in series_name and percent_code is not None:
        return percent_code

    # Finally a default fallback.
    return fallback


# Remove rows of data that do not comply with the global SDMX content constraints.
def enforce_global_content_constraints(rows):
    constraints_path = os.path.join(os.path.dirname(__file__), 'sdmx_global_content_constraints.csv')
    constraints = pd.read_csv(constraints_path)
    series_constraints = {}
    matching_rows = []
    for _, row in rows.iterrows():
        series = row['SERIES']
        if series in series_constraints:
            series_constraint = series_constraints[series]
        else:
            series_constraint = constraints.loc[constraints['SERIES'] == series]
            series_constraints[series] = series_constraint
        if series_constraint.empty:
            print('SERIES not found in constraints: ' + series)
            continue
        row_matches = True
        skip_reasons = []
        ignore_columns = ['SERIES', 'Name']
        for column in series_constraint.columns.to_list():
            if column in ignore_columns:
                continue
            column_constraint = series_constraint[column].iloc[0]
            if column_constraint == 'ALL':
                continue
            allowed_values = column_constraint.split(';') if ';' in column_constraint else [column_constraint]
            if column not in row:
                row_matches = False
                skip_reasons.append('Column "' + column + '" is missing.')
            elif row[column] not in allowed_values:
                row_matches = False
                skip_reasons.append('Column "' + column + '" has invalid value "' + row[column] + '". Allowed values are: ' + ', '.join(allowed_values))
        if not row_matches:
            print('A row was dropped because of the following reasons:')
            for reason in skip_reasons:
                print('- ' + reason)
        else:
            matching_rows.append(row)

    empty_df = pd.DataFrame(columns=rows.columns)
    return empty_df.append(matching_rows)
