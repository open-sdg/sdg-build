# Changes

### 1.0.0-rc1

* Allow decimals in metadata (#72)
* Remove references to 'published' field (#76)
* Default to the object-oriented API (#77)
* Support configuration via a "config.yml" file for Open SDG usage (#77)
* Add dataframe checks to object-oriented validation (#79)

### 0.5.0

* Add an input for CKAN instances (#51)
* Add ability to alter data and metadata during input (#51)
* Add inputs for YAML/SDMX translation data and JSON output (#60)
* Add optional fully-translated builds (#63)
* Add zips of data to builds (#64)
* More helpful validation errors (#66)
* Automated tests for object-oriented builds (#67)
* More lenient validation rules (#69, #70, #71)

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
