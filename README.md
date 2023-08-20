# SDG Build

[![codecov](https://codecov.io/gh/open-sdg/sdg-build/branch/2.0.0-dev/graph/badge.svg?token=coUSWbb1Ou)](https://codecov.io/gh/open-sdg/sdg-build)

SDG Build is a Python package for converting data on the Sustainable Development Goals (SDG) from one format into another. This is mainly useful to an SDG reporting platform, by providing these benefits:

1. Input of SDG data from various machine-readable formats, for human-friendly visualisation and display
2. Output of SDG data to various machine-readable formats, for interoperability with other systems
3. Validation of the data and metadata for quality control

## Dependencies

* Python 3.7 or higher

## Inputs

SDG Build can **input** SDG data in the following formats:

* Data in CSV files (long/tidy format)
* Data (and minimal metadata) from SDMX-JSON and SDMX-ML
* Data from a CKAN instance
* Data in JSON-Stat format from an API
* Data from a PxWeb API instance
* Metadata in YAML files
* Metadata in CSV files
* Metadata in Excel files
* Metadata in SDMX files
* Metadata in Microsoft Word templates

## Ouputs

SDG Build can **output** SDG data in the following formats:

* A particular JSON structure for data and metadata, expected by the [Open SDG](https://open-sdg.org) reporting platform.
* GeoJSON for mapping (there is not a global standard for SDG GeoJSON at this time, so this is our best guess at a useful structure)
* SDMX-ML output (data and metadata)
* Datapackages
* CSVW

## Alterations of data and metadata

Sometimes you may need to alter data and/or metadata before importing into this library. This can be done after instantiating the input objects, with `add_data_alteration` and `add_meta_alteration` to add callback functions.

In these callback functions, the thing to be altered is passed as the first parameter, followed by a "context" dict, containing other information. These "context" dicts currently contain:

* indicator_id : string - The id of the indicator, if known
* class : string - The name of the particular input class that is being altered

For example:

```
def my_data_alteration(df, context):
    # Target a particular input class.
    if context['class'] != 'InputCsvData':
      return df
    # Drop an unnecessary column in the data.
    df = df.drop('unnecessary_column', axis='columns')
    # Drop an unnecessary column for one particular indicator.
    if context['indicator_id'] == '1-1-1':
      df = df.drop('another_column', axis='columns')
    return df
def my_meta_alteration(meta, context):
    # Target a particular input class.
    if context['class'] != 'InputYamlMeta':
      return meta
    # Drop an unecessary field in the metadata.
    del meta['unnecessary_field']
    # Set a metadata field for one particular indicator.
    if context['indicator_id'] == '1-1-1':
      meta['another_field'] = 'My hardcoded value for indicator 1.1.1'
    return meta
my_data_input.add_data_alteration(my_data_alteration)
my_meta_input.add_meta_alteration(my_meta_alteration)
```

## Alterations of full indicator

Sometime you may want to alter the metadata based on the data, or vice versa, to alter the data based on the metadata. The above-mentioned `add_data_alteration` and `add_meta_alteration` are not reliable for this, because they act on each individual input. So to accomplish this, there is an `add_indicator_alteration` method on all output classes, which can be used to set a callback function which runs on each indicator, after it has been fully compiled from all the inputs.

In these callback functions, the indicator to be altered is passed as the first parameter, and it is an Indicator object (see `sdg/Indicator.py`). The second parameter is a "context" dict, containing other information. These "context" dicts currently contain:

* indicator_id : string - The id of the indicator, if known
* class : string - The name of the particular output class containing the indicator

The callback function must return the Indicator object.

For example:

```
def my_indicator_alteration(indicator, context):
    # If the number of years is 2 or less, use a bar chart.
    if indicator.data.Year.nunique() <= 2:
      indicator.meta['graph_type'] = 'bar'
    return indicator
my_output.add_indicator_alteration(my_indicator_alteration)
```

## Metadata schemas

SDG Build requires a schema for any metadata. Currently the following formats are supported:

* YAML schema intended for Prose.io
* SDMX MSD

## Data schemas

A data schema can be provided to control the sorting and validation of data. Currently the following formats are supported:

* Table Schema (YAML)
* SDMX DSD

## Translations

SDG Build can also import translations and use them to produce fully-translated builds. The translations can also be exported as well. Input formats include:

* SDMX DSD
* YAML local files
* YAML Git repository

The export formats include:

* JSON

### Metadata "subfolder" translations

Indicator metadata is expected to be simple key/value pairs, but translations can also be structured using a "subfolder" approach. With this approach, a full set of pre-translated key/value pairs can be placed in the metadata under the appropriate language code. For example, the following structure could be used to provide a Spanish translation of an indicator's name:

```
indicator_name: My English indicator name
es:
  indicator_name: My Spanish indicator name
```

When using the InputYamlMdMeta class, this can be accomplished by creating subfolders for each language code, and adding pre-translated versions of the YAML files there.

## Usage

Usage examples are available in `docs/examples`. In each of these examples, the output is generated in a `_site` folder. Before running these examples, make sure to run:

```
pip install -r docs/examples/requirements.txt
```

### Example #1: CSV + YAML to Open SDG - simple

An example conversion from CSV data and YAML metadata into JSON suitable for the Open SDG platform. This example uses a [configuration file](https://github.com/open-sdg/sdg-build/blob/master/docs/examples/open_sdg_config.yml) and helper functions (`open_sdg_check` and `open_sdg_build`) for the greatest simplicity:

```
python docs/examples/open_sdg_simple.py
```

### Example #2: CSV + YAML to Open SDG

An example conversion from CSV data and YAML metadata into JSON suitable for the Open SDG platform. This example (in contrast to the "simple" example above) uses no helper functions, in order to demonstrate how to use the various Python classes:

```
python docs/examples/open_sdg.py
```

### Example #3: SDMX-JSON to Open SDG

An example conversion from SDMX-JSON (from an API endpoint) into JSON suitable for the Open SDG platform:

```
python docs/examples/sdmx_json.py
```

### Example #4: SDMX-ML to Open SDG

An example conversion from SDMX-ML into JSON suitable for the Open SDG platform:

```
python docs/examples/sdmx_ml.py
```

### Example #5: CKAN instance to Open SDG

An example conversion from CKAN data to JSON suitable for the Open SDG platform:

```
python docs/examples/ckan.py
```

### Example #6: CSV to GeoJSON

An example conversion from CSV data to GeoJSON suitable for mapping:

```
python docs/examples/geojson.py
```

## Additional documentation

See the `docs` folder for additional documentation.

## License

MIT © Office for National Statistics

