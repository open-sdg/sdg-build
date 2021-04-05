# SDG Build

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
* Metadata in YAML files
* Metadata in CSV files
* Metadata in Excel files

## Ouputs

SDG Build can **output** SDG data in the following formats:

* A particular JSON structure for data and metadata, expected by the [Open SDG](https://open-sdg.org) reporting platform.
* GeoJSON for mapping (there is not a global standard for SDG GeoJSON at this time, so this is our best guess at a useful structure)
* SDMX-ML output

## Alterations of data, metadata, indicator ID, and indicator name

Sometimes you may need to alter each indicator's data/metadata/id/name before importing into this library. This can be done after instantiating the input objects, with `add_data_alteration`, `add_meta_alteration`, `add_indicator_id_alteration`, and `add_indicator_name_alteration`. Each of these takes a callback function as a parameter.

In these callback functions, the thing to be altered is passed as the first parameter, followed by the an optional "context" dict, containing the other three items. These
"context" dicts contain:

* data : Pandas Dataframe (or None)
* meta : dict (or None)
* indicator_id : string
* indicator_name : string (or None)

Here are some examples of using these:

```
def my_indicator_id_alteration(indicator_id, context):
  # Control a particular indicator id by checking the name.
  if context['indicator_name'] == 'My particular indicator name':
    return 'my-particular-indicator-id'
  else:
    return indicator_id

def my_indicator_name_alteration(indicator_name, context):
  # Maybe we need to use a particular metadata field for the name.
  return context['meta']['my_name_field']

def my_data_alteration(data, context):
  # Maybe we need to drop an unnecessary column in the data.
  return df.drop('unnecessary_column', axis='columns')

def my_meta_alteration(meta, context):
  # Maybe we need to set the indicator ID as a particular field.
  meta['my_id_field'] = context['indicator_id']
  return meta

my_input.add_indicator_id_alteration(my_indicator_id_alteration)
my_input.add_indicator_name_alteration(my_indicator_name_alteration)
my_input.add_data_alteration(my_data_alteration)
my_input.add_meta_alteration(my_meta_alteration)
```

### Order of alterations

The order of the alterations may be important to know. They can't all be simultaneous, so here is the order they will happen in:

1. Indicator ID
2. Indicator name
3. Data
4. Metadata

The reason this may be important is, for example, when the indicator name is being altered, the data has not be altered yet; but when the metadata is being altered, the data *has* been altered.

## Schemas

SDG Build requires a schema for any metadata. Currently the following formats are supported:

* YAML schema intended for Prose.io

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

## Upcoming integrations

Other inputs and outputs are either under development or planned for the future:

* Output to SDMX, both SDMX-JSON and SDMX-ML
* Input and output from/to CSV-W

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
