import os
import sdg
import json

class DisaggregationStatusService:
    """Service to calculate to what extent the data is disaggregated."""


    def __init__(self, site_dir, indicators, extra_fields=None):
        """Constructor for the DisaggregationStatusService class.

        Parameters
        ----------
        site_dir : string
            Base folder in which to write files.
        indicators : dict
            Dict of Indicator objects keyed by indicator id.
        """
        if extra_fields is None:
            extra_fields = []
        self.site_dir = site_dir
        self.indicators = indicators
        self.extra_fields = extra_fields
        self.expected_disaggregations = self.get_expected_disaggregations()
        self.actual_disaggregations = self.get_actual_disaggregations()
        self.goals = self.get_goals()


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


    def get_goals(self):
        goals = {}
        for indicator_id in self.indicators:
            indicator = self.indicators[indicator_id]
            goal = int(indicator.get_goal_id())
            goals[goal] = True
        goal_ids = list(goals.keys())
        goal_ids.sort()
        return goal_ids


    def is_indicator_fully_disaggregated(self, indicator_id):
        expected = self.expected_disaggregations[indicator_id]
        actual = self.actual_disaggregations[indicator_id]
        if len(actual) < len(expected):
            return False
        for disaggregation in expected:
            if disaggregation not in actual:
                return False
        return True


    def get_stats(self):

        status = {
            'statuses': [{
                'value': 'fully_dissaggregated',
                'translation_key': 'Fully disaggregated',
            }],
            'overall': {
                'statuses': [],
                'totals': {
                    'total': 0,
                }
            },
        }

        goals = {}
        for goal in self.goals:
            goals[goal] = {
                'total': 0,
                'fully_disaggregated': 0,
            }

        extra_fields = {}
        for extra_field in self.extra_fields:
            extra_fields[extra_field] = {}

        overall_total = 0
        overall_fully_disaggregated = 0

        for indicator_id in self.indicators:
            indicator = self.indicators[indicator_id]
            is_statistical = indicator.is_statistical()
            is_fully_disaggregated = self.is_indicator_fully_disaggregated(indicator_id)
            goal_id = int(indicator.get_goal_id())

            if is_statistical:
                overall_total += 1
                goals[goal_id]['total'] += 1
                for extra_field in self.extra_fields:
                    extra_field_value = indicator.get_meta_field_value(extra_field)
                    if extra_field_value is not None:
                        if extra_field_value not in extra_fields[extra_field]:
                            extra_fields[extra_field][extra_field_value] = {
                                'total': 0,
                                'fully_disaggregated': 0,
                            }
                        extra_fields[extra_field][extra_field_value]['total'] += 1

            if is_statistical and is_fully_disaggregated:
                overall_fully_disaggregated += 1
                goals[goal_id]['fully_disaggregated'] += 1
                for extra_field in self.extra_fields:
                    extra_field_value = indicator.get_meta_field_value(extra_field)
                    if extra_field_value is not None:
                        extra_fields[extra_field][extra_field_value]['fully_disaggregated'] += 1

        status['overall']['totals']['total'] = overall_total
        status['overall']['statuses'].append({
            'status': 'fully_disaggregated',
            'translation_key': 'Fully disaggregated',
            'count': overall_fully_disaggregated,
            'percentage': self.get_percent(overall_fully_disaggregated, overall_total)
        })

        status['goals'] = []
        for goal_id in goals:
            num_fully_disaggregated = goals[goal_id]['fully_disaggregated']
            num_total = goals[goal_id]['total']
            status['goals'].append({
                'goal': goal_id,
                'statuses': [{
                    'status': 'fully_disaggregated',
                    'translation_key': 'Fully disaggregated',
                    'count': num_fully_disaggregated,
                    'percentage': self.get_percent(num_fully_disaggregated, num_total),
                }],
                'totals': {
                    'total': num_total
                }
            })
        status['extra_fields'] = {}
        for extra_field in extra_fields:
            status['extra_fields'][extra_field] = []
            for extra_field_value in extra_fields[extra_field]:
                num_fully_disaggregated = extra_fields[extra_field][extra_field_value]['fully_disaggregated']
                num_total = extra_fields[extra_field][extra_field_value]['total']
                status['extra_fields'][extra_field].append({
                    extra_field: extra_field_value,
                    'statuses': [{
                        'status': 'fully_dissaggregated',
                        'translation_key': 'Fully disaggregated',
                        'count': num_fully_disaggregated,
                        'percentage': self.get_percent(num_fully_disaggregated, num_total),
                    }],
                    'totals': {
                        'total': num_total
                    }
                })

        return status


    def get_percent(self, part, whole):
        return 100 * float(part) / float(whole)


    def write_json(self):
        folder = os.path.join(self.site_dir, 'stats')
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        json_path = os.path.join(folder, 'disaggregation.json')
        with open(json_path, 'w', encoding='utf-8') as outfile:
            json.dump(self.get_stats(), outfile)
