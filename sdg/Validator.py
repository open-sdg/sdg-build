import sdg

class Validator:
    """Validator for the data and metadata in Indicator objects."""

    def __init__(self, inputs, schema):
        """Constructor for the Validator instances.

        Args:
        inputs: List of InputBase objects.
        schema: SchemaInputBase object.
        """
        self.indicators = self.merge_inputs(inputs)
        self.schema = schema

    def merge_inputs(self, inputs):
        """Take the results of many inputs and merge into a single dict of indicators."""
        merged_indicators = {}
        for input in inputs:
            # Fetch the input.
            input.execute()
            # Merge the results.
            for inid in input.indicators:
                if inid not in merged_indicators:
                    merged_indicators[inid] = input.indicators[inid]
                else:
                    merged_indicators[inid].set_data(input.indicators[inid].data)
                    merged_indicators[inid].set_meta(input.indicators[inid].meta)

        return merged_indicators

    def execute(self):
        """Validate the data and metadata for the indicators."""

        status = True
        for inid in self.indicators:
            status = status & self.schema.validate(self.indicators[inid])

        return status
