import sdg
import os

def test_translation_input_csv():

    input = sdg.translations.TranslationInputYaml(
        source=os.path.join('tests', 'assets', 'translations', 'yaml'),
    )
    input.execute()
    assert input.translations['en']['foo']['foo'] == 'bar'
