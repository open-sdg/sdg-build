import pandas as pd
import sdg
from sdg.inputs import InputBase
from sdg.Indicator import Indicator
from sdg.helpers.px import Px
import re
import yaml

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
                if 'NOTE' in keywords:
                    note_value = px.keyword('NOTE')
                    if isinstance(note_value, str):
                        metadata['data_footnote'] = translation_group + '.data_footnote'
                        metadata['page_content'] = translation_group + '.page_content'
                if 'INFO' in keywords:
                    metadata['graph_title'] = translation_group + '.graph_title'
                    metadata['indicator_name'] = translation_group + '.indicator_name'
                for mapped_key in self.meta_map:
                    if mapped_key in keywords:
                        metadata[self.meta_map[mapped_key]] = translation_group + '.' + mapped_key
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
        if source is None:
            return {}
        elif isinstance(source, dict):
            return source
        elif isinstance(source, str):
            with open(source) as file:
                return yaml.load(file, Loader=yaml.FullLoader)
        else:
            raise Exception("The meta_map parameter is not configured correctly.")
        return {}


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
