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
from . import schema
from . import stats
from . import open_sdg
from . import inputs
from . import outputs
from . import schemas
from . import translations
from .Indicator import Indicator
from .IndicatorExportService import IndicatorExportService
from .open_sdg import build_data
from .open_sdg import check_all_csv
from .open_sdg import check_all_meta
