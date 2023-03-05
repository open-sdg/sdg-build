import sdg
import os
import pytest

def test_translation_input_yaml():

    input = sdg.translations.TranslationInputYaml(
        source=os.path.join('tests', 'assets', 'translations', 'yaml'),
    )
    input.execute()
    assert input.translations['en']['foo']['foo'] == 'bar'

def test_translation_input_yaml_with_problems():

    input = sdg.translations.TranslationInputYaml(
        source=os.path.join('tests', 'assets', 'translations', 'yaml-with-problems'),
    )
    with pytest.raises(Exception) as e_info:
        input.execute()
