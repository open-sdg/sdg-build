class OutputBase:
    """Base class for destinations of SDG data/metadata."""


    def __init__(self, inputs, schema, output_folder=''):
        """Constructor for OutputBase."""
        self.indicators = self.merge_inputs(inputs)
        self.schema = schema
        self.output_folder = output_folder


    def execute():
        """Write the SDG output to disk."""
        raise NotImplementedError


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
                # Make sure minimum metadata is set.
                merged_indicators[inid].require_meta()

        return merged_indicators


    def validate(self):
        """Validate the data and metadata for the indicators."""

        status = True
        for inid in self.indicators:
            status = status & self.schema.validate(self.indicators[inid])

        return status