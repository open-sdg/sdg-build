import pandas as pd
import sdg
import requests
from sdg.inputs import InputSdmx

class InputSdmxMl(InputSdmx):
    """Sources of SDG data that are SDMX-ML format."""

    def fetch_data(self):
        """Fetch the data from the source."""


    def execute(self):
        """Execute this input. Overrides parent."""
