# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 13:32:52 2019

@author: dashton

Aggregate information for reporting statistics
"""
import pandas as pd


def reporting_status(schema, all_meta):
    """
    Args:
        schema: An object of class "Schema" containing the metadata schema
        all_meta: A dictionary containing all metadata items

    Returns:
        Dictionary of reporting statuses at goal and total level
    """

    fields = ['reporting_status', 'published', 'sdg_goal']

    status_values = schema.get_values('reporting_status')
    value_names = schema.get_value_names('reporting_status')

    # Pick out only the fields we want from each indicators metadata
    rows = [
        {k: meta.get(k) for k in fields}
        for (key, meta) in all_meta.items()
    ]

    meta_df = (
        pd.DataFrame(rows, index=all_meta.keys()).
        assign(sdg_goal=lambda x: x.sdg_goal.astype('int32'))
    )

    # Count each reporting status
    goal_df = meta_df.pivot_table(
            index='sdg_goal',
            columns='reporting_status',
            aggfunc='size',
            fill_value=0,
            dropna=False)

    # While we only have statuses sum across rows for the total
    goal_df['total'] = goal_df.sum(axis=1)

    def status_report(g, status):
        count = g.get(status, 0)  # If status is missing use 0
        return {'status': status,
                'status_label': value_names[status],
                'count': count,
                'percentage': round(100 * count / g['total'], None)}

    # Loop over rows and build our output
    goal_report = list()
    for index, g in goal_df.reset_index().iterrows():
        goal_report.append(
            {
                'goal': g['sdg_goal'],
                'statuses': [status_report(g, status)
                             for status in status_values],
                'totals': {'total': g['total']}
            })
    goal_report

    # Aggregate to get to the totals
    tot_df = goal_df.agg('sum').to_frame().transpose()
    row = tot_df.iloc[0]
    total_report = {
            'statuses': [status_report(g, status)
                             for status in status_values],
            'totals': {'total': row['total']}
    }

    total_report

    return {'goals': goal_report, 'overall': total_report}
