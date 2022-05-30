import sdg
import os

def test_translation_input_csv():

    input = sdg.translations.TranslationInputCsv(
        source=os.path.join('tests', 'assets', 'translations'),
    )
    input.execute()
    assert input.translations['en']['foo']['foo'] == 'bar'
