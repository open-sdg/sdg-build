import os
from sdg.open_sdg import open_sdg_build

folder = os.path.dirname(os.path.realpath(__file__))
config = os.path.join(folder, 'open_sdg_sdmx_output.yml')

open_sdg_build(config=config)
