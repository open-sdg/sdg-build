import os
import sdg
import json
from natsort import natsorted
from sdg.Loggable import Loggable

class DisaggregationStatusService(Loggable):
    """Service to calculate to what extent the data is disaggregated."""


    def __init__(self, site_dir, indicators, extra_fields=None, ignore_na=False, logging=None):
        """Constructor for the DisaggregationStatusService class.

        Parameters
        ----------
        site_dir : string
            Base folder in which to write files.
        indicators : dict
            Dict of Indicator objects keyed by indicator id.
        extra_fields : list
            List of strings for extra fields to generate stats by.
        ignore_na : boolean
            Whether to ignore (ie, omit) out-of-scope stats.
        """
        Loggable.__init__(self, logging=logging)
        if extra_fields is None:
            extra_fields = []
        self.site_dir = site_dir
        self.indicators = indicators
        self.extra_fields = extra_fields
        self.ignore_na = ignore_na
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
            if indicator.is_standalone() or indicator.is_placeholder():
                continue
            goal = indicator.get_goal_id()
            goals[goal] = True
        goal_ids = list(goals.keys())
        return natsorted(goal_ids)


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
                },
                {
                    'value': 'inprogress',
                },
                {
                    'value': 'notstarted',
                },
                {
                    'value': 'notapplicable',
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

            if indicator.is_standalone() or indicator.is_placeholder():
                continue

            is_notapplicable = self.is_indicator_notapplicable(indicator_id)
            is_complete = self.is_indicator_complete(indicator_id)
            is_inprogress = self.is_indicator_inprogress(indicator_id)
            goal_id = indicator.get_goal_id()

            increment = 0 if self.ignore_na and is_notapplicable else 1

            overall_total += increment
            goals[goal_id]['total'] += increment

            if is_notapplicable:
                goals[goal_id]['notapplicable'] += increment
                overall_notapplicable += increment
            elif is_complete:
                goals[goal_id]['complete'] += increment
                overall_complete += increment
            elif is_inprogress:
                goals[goal_id]['inprogress'] += increment
                overall_inprogress += increment
            else:
                goals[goal_id]['notstarted'] += increment
                overall_notstarted += increment

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
                    extra_fields[extra_field][extra_field_value]['total'] += increment
                    if is_notapplicable:
                        extra_fields[extra_field][extra_field_value]['notapplicable'] += increment
                    elif is_complete:
                        extra_fields[extra_field][extra_field_value]['complete'] += increment
                    elif is_inprogress:
                        extra_fields[extra_field][extra_field_value]['inprogress'] += increment
                    else:
                        extra_fields[extra_field][extra_field_value]['notstarted'] += increment

        status['overall']['totals']['total'] = overall_total
        status['overall']['statuses'].append({
            'status': 'complete',
            'count': overall_complete,
            'percentage': self.get_percent(overall_complete, overall_total)
        })
        status['overall']['statuses'].append({
            'status': 'inprogress',
            'count': overall_inprogress,
            'percentage': self.get_percent(overall_inprogress, overall_total)
        })
        status['overall']['statuses'].append({
            'status': 'notstarted',
            'count': overall_notstarted,
            'percentage': self.get_percent(overall_notstarted, overall_total)
        })
        if not self.ignore_na:
            status['overall']['statuses'].append({
                'status': 'notapplicable',
                'count': overall_notapplicable,
                'percentage': self.get_percent(overall_notapplicable, overall_total)
            })

        status['goals'] = []
        goal_ids_sorted = natsorted(goals.keys())
        for goal_id in goal_ids_sorted:
            num_complete = goals[goal_id]['complete']
            num_inprogress = goals[goal_id]['inprogress']
            num_notstarted = goals[goal_id]['notstarted']
            if not self.ignore_na:
                num_notapplicable = goals[goal_id]['notapplicable']
            num_total = goals[goal_id]['total']
            goal_statuses = [
                {
                    'status': 'complete',
                    'count': num_complete,
                    'percentage': self.get_percent(num_complete, num_total),
                },
                {
                    'status': 'inprogress',
                    'count': num_inprogress,
                    'percentage': self.get_percent(num_inprogress, num_total)
                },
                {
                    'status': 'notstarted',
                    'count': num_notstarted,
                    'percentage': self.get_percent(num_notstarted, num_total),
                },
            ]
            if not self.ignore_na:
                goal_statuses.append({
                    'status': 'notapplicable',
                    'count': num_notapplicable,
                    'percentage': self.get_percent(num_notapplicable, num_total)
                })
            status['goals'].append({
                'goal': goal_id,
                'statuses': goal_statuses,
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
                if not self.ignore_na:
                    num_notapplicable = extra_fields[extra_field][extra_field_value]['notapplicable']
                num_total = extra_fields[extra_field][extra_field_value]['total']
                field_statuses = [
                    {
                        'status': 'complete',
                        'count': num_complete,
                        'percentage': self.get_percent(num_complete, num_total),
                    },
                    {
                        'status': 'inprogress',
                        'count': num_inprogress,
                        'percentage': self.get_percent(num_inprogress, num_total),
                    },
                    {
                        'status': 'notstarted',
                        'count': num_notstarted,
                        'percentage': self.get_percent(num_notstarted, num_total),
                    }
                ]
                if not self.ignore_na:
                    field_statuses.append({
                        'status': 'notapplicable',
                        'count': num_notapplicable,
                        'percentage': self.get_percent(num_notapplicable, num_total),
                    })
                status['extra_fields'][extra_field].append({
                    extra_field: extra_field_value,
                    'statuses': field_statuses,
                    'totals': {
                        'total': num_total
                    }
                })

        return status


    def get_percent(self, part, whole):
        if whole == 0:
            return 0
        return 100 * float(part) / float(whole)


    def write_json(self):
        folder = os.path.join(self.site_dir, 'stats')
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        json_path = os.path.join(folder, 'disaggregation.json')
        with open(json_path, 'w', encoding='utf-8') as outfile:
            json.dump(self.get_stats(), outfile)
