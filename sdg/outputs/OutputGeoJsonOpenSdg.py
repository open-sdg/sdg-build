from sdg.outputs import OutputGeoJson

class OutputGeoJsonOpenSdg(OutputGeoJson):
    """Output SDG data/metadata in GeoJson disaggregated by region."""


    def validate(self):
        """Perform specific map-related validation for Open SDG platforms.
        """

        status = OutputGeoJson.validate(self)

        # Loop through each indicator and make sure that it has GeoCodes if
        # if has "data_show_map" set to true.
        validated = True
        for indicator_id in self.get_indicator_ids():
            indicator = self.get_indicator_by_id(indicator_id)
            data_show_map = indicator.get_meta_field_value('data_show_map')
            if data_show_map:
                has_geocodes = self.indicator_has_geocodes(indicator)
                if not has_geocodes:
                    print('Indicator ' + indicator_id + ' should not have "data_show_map" set to true, because it does not contain GeoCode data.')
                    validated = False

        return status and validated
