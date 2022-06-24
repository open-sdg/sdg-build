import sdg
import os
import inputs_common

def test_csv_input():

    data_pattern = os.path.join('tests', 'assets', 'data', 'csv', '*.csv')
    data_input = sdg.inputs.InputCsvData(path_pattern=data_pattern)
    indicator_options = sdg.IndicatorOptions()
    data_input.execute(indicator_options=indicator_options)

    inputs_common.assert_input_has_correct_data(data_input.indicators['1-1-1'].data)

def test_csv_input_with_duplicates():

    translation_input = sdg.translations.TranslationInputYaml(
        source=os.path.join('tests', 'assets', 'translations', 'yaml'),
    )
    translation_helper = sdg.translations.TranslationHelper([translation_input])

    data_pattern = os.path.join('tests', 'assets', 'data', 'csv-with-duplicates', '*.csv')
    data_input = sdg.inputs.InputCsvData(path_pattern=data_pattern)
    indicator_options = sdg.IndicatorOptions()
    data_input.execute(indicator_options=indicator_options)

    indicator = data_input.indicators['1-1-1']
    indicator.translate('en', translation_helper)

    correct_data = """
        Year,SEX,SEX.1,Value
        2020,,,100
        2021,,,120
        2020,M,M,50
        2021,M,M,60
        2020,F,F,70
        2021,F,F,80
    """
    print(indicator.language('en').data)
    inputs_common.assert_input_has_correct_data(indicator.language('en').data, correct_data)
