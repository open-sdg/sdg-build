class OutputBase:
    """Base class for destinations of SDG data/metadata."""

    def __init__(self, inputs, output_folder=''):
        """Constructor for OutputBase."""
        self.indicators = self.merge_inputs(inputs)
        self.output_folder = output_folder
        self.write_output()

    def write_output():
        """Write the SDG output to disk."""
        raise NotImplementedError

    def merge_inputs(self, inputs):
        """Take the results of many inputs and merge into a single dict of indicators."""
        merged_indicators = {}
        for input in inputs:
            merged_indicators.update(inputs[input].indicators)
        return merged_indicators
