class IndicatorOptions:
    def __init__(self):
        """Constructor for IndicatorOptions.

        All "add_*" or "set_*" methods should return self, to allow chaining.

        All "get_*" methods return whatever is being requested.
        """
        self.non_disaggregation_columns = [
            'Year',
            'Value',
        ]
        self.series_column = 'Series'
        self.unit_column = 'Units'


    def add_non_disaggregation_columns(self, column):
        if column not in self.non_disaggregation_columns:
            self.non_disaggregation_columns.append(column)
        return self


    def get_non_disaggregation_columns(self):
        return self.non_disaggregation_columns


    def set_series_column(self, column):
        self.series_column = column
        return self


    def get_series_column(self):
        return self.series_column


    def set_unit_column(self, column):
        self.unit_column = column
        return self


    def get_unit_column(self):
        return self.unit_column
