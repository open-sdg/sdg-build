from sdg.inputs import InputSdmxMl_Structure

class InputSdmxMl_UnitedNationsApi(InputSdmxMl_Structure):
    """SDG data specifically called from the UN SDGs-SDMX API."""

    def __init__(self, reference_area='1', dimension_query=None, **kwargs):
        """ Constructor for InputSdmxMultiple.

        Parameters
        ----------
        reference_area : string
            The SDMX in the REF_AREA dimension. Defaults to '1' (world).
        dimension_query : dict
            A dict of SDMX dimensions to use in generating the query. For details see:
            https://unstats.un.org/sdgs/files/SDMX_SDG_API_MANUAL.pdf
        kwargs
            All the other keyword parameters to be passed to the InputSdmxMl_Structure class.
        """
        self.reference_area = reference_area
        if dimension_query is None:
            dimension_query = {}
        self.dimension_query = dimension_query
        if 'source' not in kwargs:
            kwargs['source'] = self.get_api_query()
        if 'dsd' not in kwargs:
            kwargs['dsd'] = 'https://registry.sdmx.org/ws/public/sdmxapi/rest/datastructure/IAEG-SDGs/SDG/latest/?format=sdmx-2.1&detail=full&references=children'
        if 'drop_dimensions' not in kwargs:
            kwargs['drop_dimensions'] = ['DATA_LAST_UPDATE', 'TIME_DETAIL']
        InputSdmxMl_Structure.__init__(self, **kwargs)


    def get_api_query(self):
        params = [
            'FREQ',
            'REPORTING_TYPE',
            'SERIES',
            'REF_AREA',
            'SEX',
            'AGE',
            'URBANISATION',
            'INCOME_WEALTH_QUANTILE',
            'EDUCATION_LEV',
            'OCCUPATION',
            'CUST_BREAKDOWN',
            'COMPOSITE_BREAKDOWN',
            'DISABILITY_STATUS',
            'ACTIVITY',
            'PRODUCT',
        ]
        dimension_query = self.dimension_query
        if 'REF_AREA' not in dimension_query and self.reference_area is not None:
            dimension_query['REF_AREA'] = str(self.reference_area)

        prefix = 'https://data.un.org/ws/rest/data/IAEG-SDGs,DF_SDG_GLH,1.3/'
        suffix = '/ALL/?detail=full&dimensionAtObservation=TIME_PERIOD'
        values = map(lambda x: self.dimension_query[x] if x in self.dimension_query else '', params)
        query = '.'.join(values)

        return prefix + query + suffix
