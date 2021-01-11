# Changes

### 1.2.0

* Output documentation baseurl (#178)
* Yaml meta input (#176)
* Fix default translation repo (#175)
* Disaggregation stats in Open SDG output (#174)
* Use column as a default group when translating data (#173)
* Output untranslated build along with translation builds (#172)
* Allow multiple meta file inputs from different folders (#170)
* Service to copy indicator data files to the build for direct downloads (#167)
* Handle Obs elements without ObsValue (#165)
* Fix call for base class for indicator ids (#163)
* Add a disaggregation report to automated docs (#158)
* More efficient generation of unique combinations of disaggregations (#156)
* Automatic output documentation (#153)
* Don't omit the SERIES ids from disaggregations in SDMX inputs (#150)
* Special treatment of 'Series' column (#148)
* Do not translate 'Year', 'Value', or 'Units' in data column names (#146)

### 1.0.0

* Allow normal Prose fields to be boolean too (#142)
* Print warning instead of exception when series has duplicate value (#140)
* Preserve the order of the fields in the schema input/output (#139)
* Allow translations to override existing ones (#137)
* Reporting_status also to default to complete if data_non_statistical is true (#128)
* Add Excel metadata input and make CSV metadata input consistent (#126)
* SDMX-ML multiple input (#123)
* Change the Open SDG config syntax to support non-standard inputs (#122)
* Better Windows support (#119, #124)
* Support subfolder translation in translated builds (#114)
* Fix logic of all-numeric check in stats.py (#113)
* Logic fix to give special validation to multiselects and selects (#111)
* Restore the 'git' and 'git_data_dir' functionality (#110)
* Translate nested metadata (#106)
* Set indicator_name instead of indicator_name_national (#105)
* Save json info about the zip file (#103)
* Allow CSV metadata input (#102)
* Never use [] or {} as parameter defaults (#100)
* GeoJSON output (#99)
* Only zip indicators that are complete and statistical (#98)
* Default to True for git in Yaml metadata input (#96)
* Allow SDMX to import translation keys instead of text (#91, #107)
* Fix for list index bug (#89)
* Allow translations in CSV format (#87)
* Ensure numeric values in SDMX inputs (#81, #82)
* Allow reporting stats to include extra fields (#80)
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
