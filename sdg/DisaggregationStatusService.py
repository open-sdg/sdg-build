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
            if indicator.is_standalone():
                continue
            goal = int(indicator.get_goal_id())
            goals[goal] = True
        goal_ids = list(goals.keys())
        goal_ids.sort()
        return goal_ids


    def is_indicator_complete(self, indicator_id):
        expected = self.expected_disaggregations[indicator_id]
        actual = self.actual_disaggregations[indicator_id]
        if len(actual) < len(expected):
            return False
        for disaggregation in expected:
            if disaggregation not in actual:
                return False
        return True


    def is_indicator_inprogress(self, indicator_id):
        expected = self.expected_disaggregations[indicator_id]
        actual = self.actual_disaggregations[indicator_id]
        if len(actual) == 0:
            return False
        for disaggregation in expected:
            if disaggregation in actual:
                return True
        return False


    def is_indicator_notapplicable(self, indicator_id):
        expected = self.expected_disaggregations[indicator_id]
        return len(expected) == 0


    def get_stats(self):

        status = {
            'statuses': [
                {
                    'value': 'complete',
                    'translation_key': 'status.disaggregation_status_complete',
                },
                {
                    'value': 'inprogress',
                    'translation_key': 'status.disaggregation_status_inprogress',
                },
                {
                    'value': 'notstarted',
                    'translation_key': 'status.disaggregation_status_notstarted',
                },
                {
                    'value': 'notapplicable',
                    'translation_key': 'status.disaggregation_status_notapplicable',
                },
            ],
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
                'complete': 0,
                'inprogress': 0,
                'notstarted': 0,
                'notapplicable': 0,
            }

        extra_fields = {}
        for extra_field in self.extra_fields:
            extra_fields[extra_field] = {}

        overall_total = 0
        overall_complete = 0
        overall_inprogress = 0
        overall_notstarted = 0
        overall_notapplicable = 0

        for indicator_id in self.indicators:
            indicator = self.indicators[indicator_id]

            if indicator.is_standalone():
                continue

            is_notapplicable = self.is_indicator_notapplicable(indicator_id)
            is_complete = self.is_indicator_complete(indicator_id)
            is_inprogress = self.is_indicator_inprogress(indicator_id)
            goal_id = int(indicator.get_goal_id())

            overall_total += 1
            goals[goal_id]['total'] += 1

            if is_notapplicable:
                goals[goal_id]['notapplicable'] += 1
                overall_notapplicable += 1
            elif is_complete:
                goals[goal_id]['complete'] += 1
                overall_complete += 1
            elif is_inprogress:
                goals[goal_id]['inprogress'] += 1
                overall_inprogress += 1
            else:
                goals[goal_id]['notstarted'] += 1
                overall_notstarted += 1

            for extra_field in self.extra_fields:
                extra_field_value = indicator.get_meta_field_value(extra_field)
                if extra_field_value is not None:
                    if extra_field_value not in extra_fields[extra_field]:
                        extra_fields[extra_field][extra_field_value] = {
                            'total': 0,
                            'complete': 0,
                            'inprogress': 0,
                            'notstarted': 0,
                            'notapplicable': 0,
                        }
                    extra_fields[extra_field][extra_field_value]['total'] += 1
                    if is_notapplicable:
                        extra_fields[extra_field][extra_field_value]['notapplicable'] += 1
                    elif is_complete:
                        extra_fields[extra_field][extra_field_value]['complete'] += 1
                    elif is_inprogress:
                        extra_fields[extra_field][extra_field_value]['inprogress'] += 1
                    else:
                        extra_fields[extra_field][extra_field_value]['notstarted'] += 1

        status['overall']['totals']['total'] = overall_total
        status['overall']['statuses'].append({
            'status': 'complete',
            'translation_key': 'status.disaggregation_status_complete',
            'count': overall_complete,
            'percentage': self.get_percent(overall_complete, overall_total)
        })
        status['overall']['statuses'].append({
            'status': 'inprogress',
            'translation_key': 'status.disaggregation_status_inprogress',
            'count': overall_inprogress,
            'percentage': self.get_percent(overall_inprogress, overall_total)
        })
        status['overall']['statuses'].append({
            'status': 'notstarted',
            'translation_key': 'status.disaggregation_status_notstarted',
            'count': overall_notstarted,
            'percentage': self.get_percent(overall_notstarted, overall_total)
        })
        status['overall']['statuses'].append({
            'status': 'notapplicable',
            'translation_key': 'status.disaggregation_status_notapplicable',
            'count': overall_notapplicable,
            'percentage': self.get_percent(overall_notapplicable, overall_total)
        })

        status['goals'] = []
        for goal_id in goals:
            num_complete = goals[goal_id]['complete']
            num_inprogress = goals[goal_id]['inprogress']
            num_notstarted = goals[goal_id]['notstarted']
            num_notapplicable = goals[goal_id]['notapplicable']
            num_total = goals[goal_id]['total']
            status['goals'].append({
                'goal': goal_id,
                'statuses': [
                    {
                        'status': 'complete',
                        'translation_key': 'status.disaggregation_status_complete',
                        'count': num_complete,
                        'percentage': self.get_percent(num_complete, num_total),
                    },
                    {
                        'status': 'inprogress',
                        'translation_key': 'status.disaggregation_status_inprogress',
                        'count': num_inprogress,
                        'percentage': self.get_percent(num_inprogress, num_total)
                    },
                    {
                        'status': 'notstarted',
                        'translation_key': 'status.disaggregation_status_notstarted',
                        'count': num_notstarted,
                        'percentage': self.get_percent(num_notstarted, num_total),
                    },
                    {
                        'status': 'notapplicable',
                        'translation_key': 'status.disaggregation_status_notapplicable',
                        'count': num_notapplicable,
                        'percentage': self.get_percent(num_notapplicable, num_total)
                    },
                ],
                'totals': {
                    'total': num_total
                }
            })
        status['extra_fields'] = {}
        for extra_field in extra_fields:
            status['extra_fields'][extra_field] = []
            for extra_field_value in extra_fields[extra_field]:
                num_complete = extra_fields[extra_field][extra_field_value]['complete']
                num_inprogress = extra_fields[extra_field][extra_field_value]['inprogress']
                num_notstarted = extra_fields[extra_field][extra_field_value]['notstarted']
                num_notapplicable = extra_fields[extra_field][extra_field_value]['notapplicable']
                num_total = extra_fields[extra_field][extra_field_value]['total']
                status['extra_fields'][extra_field].append({
                    extra_field: extra_field_value,
                    'statuses': [
                        {
                            'status': 'complete',
                            'translation_key': 'status.disaggregation_status_complete',
                            'count': num_complete,
                            'percentage': self.get_percent(num_complete, num_total),
                        },
                        {
                            'status': 'inprogress',
                            'translation_key': 'status.disaggregation_status_inprogress',
                            'count': num_inprogress,
                            'percentage': self.get_percent(num_inprogress, num_total),
                        },
                        {
                            'status': 'notstarted',
                            'translation_key': 'status.disaggregation_status_notstarted',
                            'count': num_notstarted,
                            'percentage': self.get_percent(num_notstarted, num_total),
                        },
                        {
                            'status': 'notapplicable',
                            'translation_key': 'status.disaggregation_status_notapplicable',
                            'count': num_notapplicable,
                            'percentage': self.get_percent(num_notapplicable, num_total),
                        },
                    ],
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
