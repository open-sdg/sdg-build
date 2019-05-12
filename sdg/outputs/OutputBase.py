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

        for inid in merged_indicators:
            # Now that everything has been merged, we have to make sure that
            # minimum data and metadata is set.
            merged_indicators[inid].require_data()
            merged_indicators[inid].require_meta(self.minimum_metadata(merged_indicators[inid]))
            # And because this may affect data, we have to re-do headlines and
            # edges.
            merged_indicators[inid].set_headline()
            merged_indicators[inid].set_edges()

        return merged_indicators


    def validate(self):
        """Validate the data and metadata for the indicators."""

        status = True
        for inid in self.indicators:
            status = status & self.schema.validate(self.indicators[inid])

        return status


    def minimum_metadata(self, indicator):
        """Each subclass can specify it's own minimum viable metadata values."""
        return {}
