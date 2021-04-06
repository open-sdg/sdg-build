from urllib.request import urlopen
import json
from sdg.inputs import InputBase

class InputOpenDataPlatform(InputBase):


    def __init__(self, source=None, logging=None, unit_key='unit',
                 unit_multiplier_key='scale', indicator_key='indicator'):
        InputBase.__init__(self, logging=logging)
        self.unit_key = unit_key
        self.unit_multiplier_key = unit_multiplier_key
        self.indicator_key = indicator_key
        self.source = source


    def execute(self, indicator_options):
        payload = self.fetch_file(self.source)
        parsed = json.loads(payload)
        indicators = {}
        names = {}
        for item in parsed['data']:
            indicator_id = self.normalize_indicator_id(self.get_indicator_id(item))
            indicator_name = self.normalize_indicator_name(self.get_indicator_name(item), indicator_id)
            indicator_name = indicator_name.strip(':').strip('.').strip()
            if indicator_id not in indicators:
                indicators[indicator_id] = []
            dimensions = self.get_dimensions(item)

            idx = 0
            for year in self.get_years(item):
                value = item['values'][idx]
                if value is not None:
                    disaggregations = dimensions.copy()
                    disaggregations[self.unit_key] = self.get_unit(item)
                    disaggregations[self.unit_multiplier_key] = self.get_unit_multiplier(item)
                    row = self.get_row(year, value, disaggregations)
                    indicators[indicator_id].append(row)
                idx += 1

        for indicator_id in indicators:
            df = self.create_dataframe(indicators[indicator_id])
            self.add_indicator(indicator_id, name=indicator_name, data=df, options=indicator_options)


    def get_dimensions(self, row):
        dimensions = {}
        non_dimension_props = ['goal', 'target', 'indicator']
        for prop in row:
            if prop in non_dimension_props:
                continue
            try:
                dimensions[prop] = row[prop]['id']
            except:
                pass
        return dimensions


    def get_years(self, row):
        start = int(row['startDate'][0:4])
        end = int(row['endDate'][0:4])
        if start == end:
            return [start]
        return list(range(start, end))


    def get_unit(self, row):
        return row[self.unit_key]


    def get_unit_multiplier(self, row):
        return row[self.unit_multiplier_key]


    def get_indicator_id(self, row):
        return row[self.indicator_key]['id']


    def get_indicator_name(self, row):
        return row[self.indicator_key]['name']
