# -*- coding: utf-8 -*-

from frictionless import describe_schema
from sdg.data_schemas import DataSchemaInputBase
import pandas as pd

class DataSchemaInputIndicator(DataSchemaInputBase):
    """A class for inferring a data schema from an Indicator object.
    The source parameter should be a map of Indicator objects,
    keyed by their dash-delimited indicator ids."""


    def load_schema(self, indicator):
        df = indicator.data
        schema = describe_schema(df)
        non_disaggregation_columns = indicator.options.get_non_disaggregation_columns()
        non_disaggregation_special_columns = [
            indicator.options.get_series_column(),
            indicator.options.get_unit_column(),
        ]
        for column in indicator.data.columns:
            if column in non_disaggregation_columns and column not in non_disaggregation_special_columns:
                continue
            unique = df[column].unique()
            unique = unique[~pd.isnull(unique)]
            unique = unique.tolist() + ['']
            schema.get_field(column).constraints['enum'] = unique
        return schema


    def load_all_schema(self):
        """Load the indicator schema."""
        return {
            indicator_id: self.load_schema(self.source[indicator_id])
            for indicator_id in self.source
        }
