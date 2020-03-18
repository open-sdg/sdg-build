"""
If you are using the Open SDG config file approach (see open_sdg_config.yml)
then you can use this "open_sdg_alter.py" to perform any alterations on the
data and metadata.

Data alteration: If this file contains a function called "alter_data", it will
be applied to each "input".

Meta alteration: If this file contains a function called "alter_meta", it will
be applied to each "input".
"""

def alter_data(df):
  # Perform any alterations to the DataFrame.
  return df

def alter_meta(meta):
  # Perform any alterations to the dict.
  return meta
