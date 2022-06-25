import pandas as pd
import inspect
from io import StringIO

def assert_input_has_correct_data(df, correct_data=None):
    if correct_data is None:
        correct_data = """
            Year,SEX,Value
            2020,,100
            2021,,120
            2020,M,50
            2021,M,60
            2020,F,70
            2021,F,80
        """
    correct_df = pd.read_csv(StringIO(inspect.cleandoc(correct_data)))
    pd.testing.assert_frame_equal(df, correct_df)

def assert_input_has_correct_headline(df):
    correct_data = """
        Year,Value
        2020,100
        2021,120
    """
    correct_df = pd.read_csv(StringIO(inspect.cleandoc(correct_data)))
    pd.testing.assert_frame_equal(df, correct_df)

def assert_input_has_correct_meta(meta):
    correct_meta = {
        'foo': 'bar',
        'page_content': 'Hello world',
    }
    assert meta == correct_meta
