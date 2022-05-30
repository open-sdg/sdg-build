import sdg

def test_translation_input_sdmx():

    input = sdg.translations.TranslationInputSdmx(
        source='https://registry.sdmx.org/ws/public/sdmxapi/rest/datastructure/IAEG-SDGs/SDG/latest/?format=sdmx-2.1&detail=full&references=children',
    )
    input.execute()
    assert input.translations['en']['FREQ']['FREQ'] == 'Frequency of observation'
    assert input.translations['en']['FREQ']['A'] == 'Annual'
