# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 13:32:52 2019

@author: dashton

Aggregate information for reporting statistics
"""
import pandas as pd


def reporting_status(schema, all_meta, extra_fields=None):
    """
    Args:
        schema: An object of class "Schema" containing the metadata schema
        all_meta: A dictionary containing all metadata items
        extra_fields: List of fields to group stats by, in addition to goal

    Returns:
        Dictionary of reporting statuses at goal (plus any extra fields) and
        total level
    """

    # Make sure 'sdg_goal' is in the list of fields.
    grouping_fields = extra_fields if extra_fields is not None else []
    if 'sdg_goal' not in grouping_fields:
        grouping_fields.append('sdg_goal')

    # Generate a report of the possible statuses, both value and translations.
    status_values = schema.get_values('reporting_status')
    value_translation = schema.get_value_translation('reporting_status')
    status_report = [{'value': status,
                      'translation_key': value_translation[status]}
                    for status in status_values]

    # Omit any standalone indicators.
    indicators = {k: v for (k, v) in all_meta.items() if 'standalone' not in v or v['standalone'] == False }

    # Pick out only the fields we want from each indicators metadata
    fields = ['reporting_status'] + grouping_fields
    rows = [
        {k: meta.get(k) for k in fields}
        for (key, meta) in indicators.items()
    ]
    # Convert that into a dataframe.
    meta_df = pd.DataFrame(rows, index=indicators.keys())
    meta_df.fillna('status.not_specified', inplace=True)

    # Make sure that numeric columns are numeric.
    def value_is_numeric(value):
        return value if isinstance(value, int) else (isinstance(value, str) and value.isnumeric())
    for field in grouping_fields:
        if all(value_is_numeric(x) for x in meta_df[field]):
            meta_df[field] = meta_df[field].apply(pd.to_numeric)

    # Create a separate dataframe for each grouping field.
    grouped_dfs = {}
    for grouping_field in grouping_fields:
        grouped_df = meta_df.pivot_table(
            index=grouping_field,
            columns='reporting_status',
            aggfunc='size',
            fill_value=0,
            dropna=False)
        grouped_df['total'] = grouped_df.sum(axis=1)
        grouped_dfs[grouping_field] = grouped_df

    # Helper function for putting together one status report.
    def one_status_report(g, status):
        count = g.get(status, 0)  # If status is missing use 0
        return {'status': status,
                'translation_key': value_translation[status],
                'count': count,
                'percentage': round(100 * count / g['total'],3)}

    # For a "totals" report, arbitrarily use one of the grouping fields (They
    # are all the same, when it comes to the totals.)
    tot_series = grouped_dfs[grouping_fields[0]].apply(lambda x: x.sum())
    total_report = {
        'statuses': [one_status_report(tot_series, status)
                        for status in status_values],
        'totals': {'total': tot_series['total']}
    }

    # Start to build our output.
    output = {
        'statuses': status_report,
        'overall': total_report,
        'extra_fields': {},
    }

    # Add on a report for each of our grouping fields.
    for field in grouped_dfs:
        grouped_report = list()
        for index, g in grouped_dfs[field].reset_index().iterrows():
            # Because the goals report is treated differently, standardize on
            # the key of "goal" instead of "sdg_goals".
            fixed_field_name = field.replace('sdg_goal', 'goal')
            grouped_report.append(
                {
                    fixed_field_name: g[field],
                    'statuses': [one_status_report(g, status)
                                for status in status_values],
                    'totals': {'total': g['total']}
                })
        output['extra_fields'][field] = grouped_report

    # Treat goals specially, by putting it outside of "extra_fields".
    output['goals'] = output['extra_fields']['sdg_goal']
    del output['extra_fields']['sdg_goal']

    return output
