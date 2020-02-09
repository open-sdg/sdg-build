"""
This is an example of converting CSV data into GeoJSON output suitable for use
on a regional map.
"""

import os
import sdg

# Input data from CSV files matching this pattern: tests/data/*-*.csv
data_pattern = os.path.join('tests', 'data', '*-*.csv')
data_input = sdg.inputs.InputCsvData(path_pattern=data_pattern)

# Input metadata from YAML files matching this pattern: tests/meta/*-*.md
meta_pattern = os.path.join('tests', 'meta', '*-*.md')
meta_input = sdg.inputs.InputYamlMdMeta(path_pattern=meta_pattern)

inputs = [data_input, meta_input]

# Use a Prose.io file for the metadata schema.
schema_path = os.path.join('tests', '_prose.yml')
schema = sdg.schemas.SchemaInputOpenSdg(schema_path=schema_path)

# GeoJSON parameters.
# The base GeoJSON file containing the regional geometries (borders).
geojson_file = 'https://geoportal1-ons.opendata.arcgis.com/datasets/4fcca2a47fed4bfaa1793015a18537ac_4.geojson'
# The property of the features in the geometry file representing a region's name.
name_property = 'rgn17nm'
# The property of the features in the geometry file representing a region's id.
id_property = 'rgn17cd'
# The column in the source data representing some data's regional id. This
# "joins" the source data with the geometry file.
id_column = 'GeoCode'
# The subfolder to put all the geojson files in.
output_subfolder = 'regions'

# Create an "output" from these inputs/schema/translations, for GeoJSON output.
geojson_output = sdg.outputs.OutputGeoJson(
    inputs=inputs,
    schema=schema,
    output_folder='_site',
    geojson_file=geojson_file,
    name_property=name_property,
    id_property=id_property,
    id_column=id_column,
    output_subfolder=output_subfolder)

# Validate the indicators.
validation_successful = geojson_output.validate()

# If everything was valid, perform the build.
if validation_successful:
    # Here are several ways you can generate the build:
    # 1. Translated into a single language, like English: geojson_output.execute('en')
    #    (the build will appear in '_site/en')
    # 2. Translated into several languages: geojson_output.execute_per_language(['es', 'ru', 'en'])
    #    (three builds will appear in '_site/es', '_site/ru', and '_site/en')
    # 3. Untranslated: geojson_output.execute()
    #    (the build will appear in '_site')
    geojson_output.execute_per_language(['es', 'ru', 'en'])
else:
    raise Exception('There were validation errors. See output above.')
