"""Supporting scripts for sdg-indicators build"""

__version__ = "0.3.1"
__author__ = "Doug Ashton <douglas.j.ashton@gmail.com>"

# Load key components
from . import path
from . import data
from . import git
from . import edges
from . import json
from . import meta
from . import stats
from . import open_sdg
from . import inputs
from . import outputs
from . import schemas
from . import translations
from .Indicator import Indicator
from .IndicatorExportService import IndicatorExportService
from .Series import Series
from .build import build_data
from .check_csv import check_all_csv
from .check_metadata import check_all_meta
from .open_sdg import open_sdg_build
from .open_sdg import open_sdg_check
