class OutputBase:
    """Base class for destinations of SDG data/metadata."""

    def __init__(self, inputs, output_folder=''):
        """Constructor for OutputBase."""
        self.indicators = self.merge_inputs(inputs)
        self.output_folder = output_folder

    def execute():
        """Write the SDG output to disk."""
        raise NotImplementedError

    def merge_inputs(self, inputs):
        """Take the results of many inputs and merge into a single dict of indicators."""
        merged_indicators = {}
        indicator_parts = ['data', 'metadata', 'headline', 'edges']
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
                    merged_indicators[inid].set_headline(input.indicators[inid].headline)
                    merged_indicators[inid].set_edges(input.indicators[inid].edges)

        return merged_indicators
