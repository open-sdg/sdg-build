# -*- coding: utf-8 -*-

from frictionless import describe_schema
from sdg.data_schemas import DataSchemaInputBase
import pandas as pd

class DataSchemaInputIndicator(DataSchemaInputBase):
    """A class for inferring a data schema from an Indicator object.
    The schema_path parameter should be the Indicator object itself."""


    def load_schema(self):
        indicator = self.schema_path
        df = indicator.data
        schema = describe_schema(df)
        non_disaggregation_columns = indicator.options.get_non_disaggregation_columns()
        for column in indicator.data.columns:
            if column in non_disaggregation_columns:
                continue
            unique = df[column].unique()
            unique = unique[~pd.isnull(unique)]
            unique = unique.tolist() + ['']
            schema.get_field(column).constraints['enum'] = unique
        return schema
