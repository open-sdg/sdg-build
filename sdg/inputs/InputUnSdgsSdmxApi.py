from sdg.inputs import InputSdmxMl_Structure

class InputUnSdgsSdmxApi(InputSdmxMl_Structure):
    """SDG data specifically called from the UN SDGs-SDMX API."""

    def __init__(self, reference_area='1', **kwargs):
        """ Constructor for InputSdmxMultiple.

        Parameters
        ----------
        reference_area : string
            The SDMX in the REF_AREA dimension. Defaults to '1' (world).
        kwargs
            All the other keyword parameters to be passed to the InputSdmxMl_Structure class.
        """
        self.reference_area = reference_area
        if 'source' not in kwargs:
            kwargs['source'] = 'https://data.un.org/ws/rest/data/IAEG-SDGs,DF_SDG_GLH,1.3/...' + str(reference_area) + '.........../ALL/?detail=full&dimensionAtObservation=TIME_PERIOD'
        if 'dsd' not in kwargs:
            kwargs['dsd'] = 'https://registry.sdmx.org/ws/public/sdmxapi/rest/datastructure/IAEG-SDGs/SDG/latest/?format=sdmx-2.1&detail=full&references=children'
        if 'drop_dimensions' not in kwargs:
            kwargs['drop_dimensions'] = ['DATA_LAST_UPDATE', 'TIME_DETAIL']
        InputSdmxMl_Structure.__init__(**kwargs)
