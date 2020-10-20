import os
import sdg
import json

class DisaggregationStatusService:
    """Service to calculate to what extent the data is disaggregated."""


    def __init__(self, site_dir, indicators):
        """Constructor for the DisaggregationStatusService class.

        Parameters
        ----------
        site_dir : string
            Base folder in which to write files.
        indicators : dict
            Dict of Indicator objects keyed by indicator id.
        """
        self.site_dir = site_dir
        self.indicators = indicators
        self.expected_disaggregations = self.get_expected_disaggregations()
        self.actual_disaggregations = self.get_expected_disaggregations()


    def get_expected_disaggregations(self):
        indicators = {}
        for indicator_id in self.indicators:
            indicator = self.indicators[indicator_id]
            disaggregations = indicator.get_meta_field_value('expected_disaggregations')
            if disaggregations is None:
                disaggregations = []
            indicators[indicator_id] = disaggregations
        return indicators


    def get_actual_disaggregations(self):
        indicators = {}
        for indicator_id in self.indicators:
            indicator = self.indicators[indicator_id]
            if not indicator.has_data():
                indicators[indicator_id] = []
                continue
            non_disaggregation_columns = indicator.options.get_non_disaggregation_columns()
            disaggregations = [column for column in indicator.data.columns if column not in non_disaggregation_columns]
            indicators[indicator_id] = disaggregations
        return indicators


    def is_indicator_fully_disaggregated(self, indicator_id):
        num_expected = len(self.expected_disaggregations[indicator_id])
        num_actual = len(self.actual_disaggregations[indicator_id])
        return num_actual - num_expected >= 0


    def get_number_of_fully_disaggregated_indicators(self):
        num_disaggregated = 0
        for indicator_id in self.indicators:
            indicator = self.indicators[indicator_id]
            if indicator.is_statistical() and self.is_indicator_fully_disaggregated(indicator_id):
                num_disaggregated += 1

        return num_disaggregated


    def get_number_of_statistical_indicators(self):
        num_statistical = 0
        for indicator_id in self.indicators:
            indicator = self.indicators[indicator_id]
            if indicator.is_statistical():
                num_statistical += 1
        return num_statistical


    def get_percentage_of_full_disaggregation(self):
        num_total = self.get_number_of_statistical_indicators()
        num_disaggregated = self.get_number_of_fully_disaggregated_indicators()
        return 100 * float(num_disaggregated)/float(num_total)


    def get_stats(self):
        return {
            'num_fully_disaggregated': self.get_number_of_fully_disaggregated_indicators(),
            'num_statistical': self.get_number_of_statistical_indicators(),
            'percent_fully_disaggregated': self.get_percentage_of_full_disaggregation(),
        }


    def write_json(self):
        folder = os.path.join(self.site_dir, 'stats')
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        json_path = os.path.join(folder, 'disaggregation.json')
        with open(json_path, 'w', encoding='utf-8') as outfile:
            json.dump(self.get_stats(), outfile)
