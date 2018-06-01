"""Supporting scripts for sdg-indicators build"""

__version__ = "0.2.0"
__author__ = "Doug Ashton <douglas.j.ashton@gmail.com>"

# Load key components
from . import path
from . import data
from . import git
from . import edges
from . import json
from . import meta
from . import check_metadata
from . import schema
from .check_metadata import check_all_meta
from .check_csv import check_all_csv
from .build import build_data
from .reset_csvs import reset_all_csv
from .reset_metadata import reset_all_meta
