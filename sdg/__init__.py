"""Supporting scripts for sdg-indicators build"""

__version__ = "0.1.0"
__author__ = "Doug Ashton <douglas.j.ashton@gmail.com>"

# Load key components
from . import path
from . import data
from . import git
from . import edges
from . import json
from . import meta
from . import check_metadata
from .check_metadata import check_all_meta
from .check_csv import check_all_csv
