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


    def add_non_disaggregation_columns(self, column):
        if column not in self.non_disaggregation_columns:
            self.non_disaggregation_columns.append(column)
        return self


    def get_non_disaggregation_columns(self):
        return self.non_disaggregation_columns
