"""
Run a build to "_site" with some sensible inputs
"""

import os
from pathlib import Path
from sdg.open_sdg import open_sdg_build

# Make sure whatwever we're passing in exists
this_dir = Path(__file__).parent
source_path = Path(this_dir / 'spike')
schema_path = Path(this_dir / 'spike/metadata_schema.yml')
config_path = Path(this_dir / 'spike/metadata_schema.yml')
assert schema_path.exists(), f'source dir {source_path.absolute()} does not exist'
assert schema_path.exists(), f'file {schema_path.absolute()} does not exist'
assert config_path.exists(), f'file {config_path.absolute()} does not exist'

spike_inputs = [
        {
            'class': 'InputCsvData',
            'path_pattern': os.path.join('data', '*-*.csv')
        },
        {
            'class': 'InputYamlMdMeta',
            'path_pattern': os.path.join('meta', '*-*.md'),
            'git': True,
            'git_data_dir': 'data',
        }
    ]
    
open_sdg_build(
        src_dir=str(source_path.absolute()),
        site_dir='_site',
        schema_file=str(schema_path.absolute()),
        languages=None,
        translations=None,
        config=str(config_path.absolute()),
        csvw={},
        csvw_cube=True,
        inputs=spike_inputs)
