# Changes

Might become "release notes"

### 0.4.0

* Add support for SDMX-ML and SDMX-JSON input
* Drop support for Python 3.4

### 0.3.1

Minor release to ignore columns used in SDMX

## 0.3.0

Adding the `stats` endpoint which is where reporting statistics will live. This
also raises the importance of the schema.

* Reporting Status page is computed here. Allowed statuses and their names come
from the schema, which is the `_prose.yml` file in the data repo.

### 0.2.1

Bug fix for edges json file which was being overwritten by headline data.

## 0.2.0

Generalising beyond UK

* Support `binary` chart type
* Allow flexible data directories
* Multi-lingual support

## 0.1.0

Initial release from UK version at ONSdigital
