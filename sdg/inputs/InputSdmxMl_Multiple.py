import pandas as pd
import sdg
from sdg.inputs import InputFiles
from sdg.inputs import InputSdmxMl_Structure
from sdg.inputs import InputSdmxMl_StructureSpecific
from sdg.Indicator import Indicator
from xml.etree import ElementTree as ET

class InputSdmxMl_Multiple(InputFiles):
    """Sources of SDG data that are multiple SDMX-ML files - one per indicator."""


    def __init__(self, path_pattern='', data_alterations=None,
                 meta_alterations=None, **kwargs):
        """ Constructor for InputSdmxMultiple.

        Parameters
        ----------
        path_pattern : string
            path (glob) pattern describing where the files are
        data_alterations : list
            A list of alteration callback functions to apply to all data
        meta_alterations : list
            A list of alteration callback functions to apply to all metadata
        kwargs
            All the other keyword parameters to be passed to InputSdmx classes
        """
        InputFiles.__init__(self, path_pattern)
        if data_alterations is None:
            data_alterations = []
        if meta_alterations is None:
            meta_alterations = []
        self.data_alterations = data_alterations
        self.meta_alterations = meta_alterations
        self.kwargs = kwargs


    def execute(self, indicator_options):
        """Scan the SDMX files and create indicators."""
        indicator_map = self.get_indicator_map()
        kwargs = self.kwargs
        for indicator_id in indicator_map:
            input_instance = None
            source_file = indicator_map[indicator_id]
            kwargs['source'] = source_file

            # Figure out which type of SDMX-ML we have.
            file_type = self.get_sdmx_file_type(source_file)
            if file_type == 'StructureSpecificData':
                input_instance = InputSdmxMl_StructureSpecific(**kwargs)
            elif file_type == 'GenericData':
                input_instance = InputSdmxMl_Structure(**kwargs)

            # Apply any alterations.
            for alteration in self.data_alterations:
                input_instance.add_data_alteration(alteration)
            for alteration in self.meta_alterations:
                input_instance.add_meta_alteration(alteration)

            # Execute the input and copy the resulting indicator to here.
            input_instance.execute(indicator_options)
            self.indicators.update(input_instance.indicators)


    def get_sdmx_file_type(self, file):
        return ET.parse(file).getroot().tag.split('}')[1]
