import pandas as pd
import sdg
from sdg.inputs import InputFiles
from sdg.inputs import InputSdmxMl_Structure
from sdg.inputs import InputSdmxMl_StructureSpecific
from sdg.Indicator import Indicator
import lxml.etree as ET

class InputSdmxMl_Multiple(InputFiles):
    """Sources of SDG data that are multiple SDMX-ML files - one per indicator."""


    def __init__(self, path_pattern='', **kwargs):
        """ Constructor for InputSdmxMultiple.

        Parameters
        ----------
        path_pattern : string
            path (glob) pattern describing where the files are
        kwargs
            All the other keyword parameters to be passed to InputSdmx classes
        """
        InputFiles.__init__(self, path_pattern)


    def execute(self):
        """Scan the SDMX files and create indicators."""
        indicator_map = self.get_indicator_map()
        for indicator_id in indicator_map:
            input_instance = None

            # Figure out which type of SDMX-ML we have.
            file_type = self.get_sdmx_file_type(indicator_map[indicator_id])
            if file_type == 'StructureSpecificData':
                input_instance = InputSdmxMl_StructureSpecific(**kwargs)
            elif file_type == 'GenericData':
                input_instance = InputSdmxMl_Structure(**kwargs)

            # Execute the input and copy the resulting indicator to here.
            input_instance.execute()
            self.indicators[indicator_id] = input_instance.indicators[indicator_id]


    def get_sdmx_file_type(file):
        return ET.parse(file).getroot().tag.split('}')[1]
