import sdg

def test_translation_input_sdmx_msd():

    input = sdg.translations.TranslationInputSdmxMsd(
        source='https://registry.sdmx.org/ws/public/sdmxapi/rest/conceptscheme/IAEG-SDGs/SDG_META_CONCEPTS/1.0',
    )
    input.execute()
    assert input.translations['en']['SDG_INDICATOR_INFO']['SDG_INDICATOR_INFO'] == '0. Indicator information'
