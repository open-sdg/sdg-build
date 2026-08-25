import pandas as pd
import sdg
from sdg.inputs import InputBase
from sdg.Indicator import Indicator
from sdg.helpers.px import Px
import re
import yaml
from slugify import slugify

class InputPxFile(InputBase):
    """Sources of SDG data that are local PX files."""

    def __init__(self,
        indicator_id_map=None,
        logging=None,
        column_map=None,
        code_map=None,
        request_params=None,
        meta_suffix=None,
        meta_map=None
    ):
        """Constructor for InputPxFile.

        Keyword arguments:
        indicator_id_map: A dict mapping sources (typically remote URLs) to
        lists of indicator ids.
        """
        InputBase.__init__(self,
            logging=logging,
            column_map=column_map,
            code_map=code_map,
            request_params=request_params,
            meta_suffix=meta_suffix
        )
        self.indicator_id_map = self.get_indicator_id_map(indicator_id_map)
        self.meta_map = self.get_meta_map(meta_map)


    def execute(self, indicator_options):
        empty_data_values = ['"."', '".."', '"..."']
        def replace_value(value):
            if value == '"-"':
                return 0
            elif value in empty_data_values:
                return None
            else:
                return value
        for source, indicator_ids in self.indicator_id_map.items():
            pc_axis = self.fetch_file(self.clean_remote_urls(source))
            px = Px(pc_axis)
            # Prepare the data.
            df = pd.DataFrame(px.entries())
            value_column = px.get_value_column_name()
            if value_column in df.columns:
                df = df[~df[value_column].isin(empty_data_values)]
            non_statistical = df.empty
            if not non_statistical:
                year_column = px.get_year_column_name()
                df.rename(inplace=True, columns = {
                    year_column: 'Year',
                    value_column: 'Value',
                })
                if px.data_has_series():
                    series_column = px.get_series_column_name()
                    df.rename(inplace=True, columns = {
                        series_column: indicator_options.get_series_column(),
                    })
                if px.data_has_units():
                    units_column = px.get_units_column_name()
                    df.rename(inplace=True, columns = {
                        units_column: indicator_options.get_unit_column(),
                    })
                if px.data_has_geocodes():
                    geocode_column = px.get_geocode_column_name()
                    df['GeoCode'] = df[geocode_column]

                df = df.convert_dtypes()
                df['Value'] = df['Value'].apply(replace_value)
                df['Value'] = pd.to_numeric(df['Value'])
                df['Year'] = pd.to_numeric(df['Year'])
                df = df.dropna(subset=['Value'])
            # Prepare the metadata but only with translation keys, since
            # the actual content will be gathered in the translation input.
            keywords = px.keywords()
            if not isinstance(indicator_ids, list):
                indicator_ids = [indicator_ids]
            for indicator_id in indicator_ids:
                indicator_id = indicator_id.replace('.', '-')
                translation_group = indicator_id + '-metadata'
                metadata = {}
                if not (px.data_has_units() and 'UNITS' in keywords):
                    metadata['computation_units'] = translation_group + '.computation_units'
                if 'NOTEX' in keywords:
                    notex_value = px.keyword('NOTEX')
                    notex_header = ''
                    notex_footer = []
                    if isinstance(notex_value, str):
                        notex_header = translation_group + '.page_content'
                    elif isinstance(notex_value, dict):
                        value_keys = notex_value.keys()
                        for value_key in value_keys:
                            if value_key == 'TABLE':
                                notex_header = translation_group + '.page_content'
                            else:
                                notex_footer.append(value_key)
                    if notex_header: 
                        metadata['page_content'] = notex_header
                    if notex_footer:
                        if 'footer_fields' not in metadata:
                            metadata['footer_fields'] = []
                        for notex_field in notex_footer:
                            footer_field = {
                                "label": translation_group + '.footer_field_label-' + notex_field,
                                "value": translation_group + '.footer_field_value-' + notex_field
                            }
                            metadata['footer_fields'].append(footer_field)
                if 'INFO' in keywords:
                    metadata['graph_title'] = translation_group + '.graph_title'
                    metadata['indicator_name'] = translation_group + '.indicator_name'
                if 'VALUENOTEX' in keywords:
                    valuenotex_value = px.keyword('VALUENOTEX')
                    if isinstance(valuenotex_value, dict):
                        value_keys = valuenotex_value.keys()
                        valuenotex_footer = []
                        for value_key in value_keys:
                            valuenotex_footer.append(value_key)
                        if 'footer_fields' not in metadata:
                            metadata['footer_fields'] = []
                        for valuenotex_field in valuenotex_footer:
                            slug = slugify(valuenotex_field)
                            footer_field = {
                                "label": translation_group + '.footer_field_label-' + slug,
                                "value": translation_group + '.footer_field_value-' + slug
                            }
                            metadata['footer_fields'].append(footer_field)
                for mapped_key in self.meta_map:
                    if mapped_key in keywords:
                        mapped_value = px.keyword(mapped_key)
                        converted_key = self.meta_map[mapped_key]
                        if isinstance(mapped_value, str):
                            metadata[converted_key] = translation_group + '.' + converted_key
                        elif isinstance(mapped_value, dict):
                            value_keys = mapped_value.keys()
                            for value_key in value_keys:
                                if value_key == 'TABLE':
                                    metadata[converted_key] = translation_group + '.' + converted_key
                                elif px.is_variable(value_key):
                                    metadata[converted_key + '-' + value_key] = translation_group + '.' + converted_key + '-' + value_key
                                else:
                                    # If still here, we assume that it is a value. For now, we are
                                    # using the first-encountered value and then stopping, replacing
                                    # whatever was in the "TABLE" key and then stopping.
                                    metadata[converted_key] = translation_group + '.' + converted_key
                                    break

                # As a benefit to the Open SGD integration, if the data
                # is empty, automatically flag it as a non-statistical
                # indicator.
                if non_statistical:
                    metadata['data_non_statistical'] = True
                # Add the indicator.
                if non_statistical:
                    self.add_indicator(indicator_id, meta=metadata, options=indicator_options)
                else:
                    self.add_indicator(indicator_id, data=df, meta=metadata, options=indicator_options)


    def get_meta_map(self, source):
        map = {}
        if isinstance(source, str):
            with open(source) as file:
                map = yaml.load(file, Loader=yaml.FullLoader)
        if isinstance(map, dict):
            return map
        else:
            raise Exception("The meta_map parameter is not configured correctly.")


    def get_indicator_id_map(self, source):
        if isinstance(source, dict):
            return source
        elif isinstance(source, str):
            with open(source) as file:
                return yaml.load(file, Loader=yaml.FullLoader)
        else:
            raise Exception("The indicator_id_map parameter is not configured correctly.")
        return {}


    def clean_remote_urls(self, location):
        if location.startswith('http'):
            # Because the PXWeb interface is known to add
            # ":443" to exported URLs, we automatically remove
            # it here, as a onvenience.
            location = location.replace(':443', '')
        return location
