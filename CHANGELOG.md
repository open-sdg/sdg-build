# Changes

### 2.1.0

* Catch cases where the DSD is missing the indicator name #332
* Safety code in case DSD and SDMX API are not in sync #327
* Alter indicators knowing data and metadata #324
* Include class name in context for alterations #323

### 2.0.0

* Rename columns that become duplicates after translation #316
* Copy list to avoid side effects when appending to it #313
* Testing revamp #306, #307, #308, #309, #310, #311, #312
* Fix for status variable in OutputSdmxMl #305
* Use concat instead of append #304
* Avoid deprecation warning about squeeze parameter #303
* Faster git clone for InputSdgMetadata class #302
* Convert years to numbers in SDMX inputs, for consistency #301
* InputSdmxMl_Structure fix: No ID needed on ObsDimension #300
* Subclass of geojson output for extra validation with Open SDG #297
* Deprecations for 2.0.0 #296

Here is a summary of the deprecations for 2.0.0 mentioned above:

* Remove the check_all_csv function
* Remove the check_all_meta function
* Stop auto-populating some metadata fields:
    * national_metadata_update_url
    * national_metadata_update_url_text
    * national_data_update_url
    * national_data_update_url_text
* InputMetaFiles: Remove the get_git_updates and get_git_update methods
* InputSdmx: Remove the import_translation_keys parameter
* open_sdg.py: Require at least one language
* OutputDataPackage: Default to the 'default' sorting logic
* OutputOpenSdg: Rename some metadata fields:
    * indicator_number instead of indicator
    * target_number instead of target_id
    * goal_number instead of sdg_goal

### 1.8.0

* Special treatment of more SDMX-related columns #295
* Allow multiple data inputs for the same indicator #294
* Remove version number from API endpoint #293

### 1.7.0

* Fixes for code and column mapping in SDMX output #288
* Provide indicator_id when altering data/metadata #285

### 1.6.0

* Metadata report #279
* Remove translations from stats reports #278, #281
* Reporting progress MVP #278

### 1.5.0

* Keep placeholder indicators out of some calculations #275
* Make sure disaggregations are sorted as strings #274
* Fix for UNIT_MULT issue #273
* Fix encoding in constraints CSV #272
* Allow a dtype parameter in CSV data input #271
* Handle special case of id/name columns in GeoJson output #270
* Create pull_request_template.md #269
* SDMX global output #268

### 1.4.0

* Correct way to get number of dataframe rows #266
* Style updates for data service frontend #262
* SDMX metadata output #261
* Metadata input from "SDG Metadata" repositories #259
* Replace values individually to avoid exceptions #258
* Vary by language in some method caches #257
* Allow suffix on imported metadata keys #253
* Fix empty values by column to avoid datatype issues #252
* Use TIME_PERIOD instead of TIME_DETAIL in SDMX output #250
* Allow TIME_PERIOD to exist in SDMX DSD data schema #249
* Defaults for mandatory attributes in SDMX output #247
* Fallback to translation keys if names are missing #246
* Do not sort datapackage schemas that were intentionally specified #245
* New automated metadata fields for Git dates (only) #244
* SDMX and file helper functions #242
* Bugfix - structure-specific default #237
* Allow column and code mappings to be used #236, #251, #256, #264
* Improvements of SDMX output #217, #218, #231
* Metadata input for Word template files #230
* JSON-Stat and PxWeb data inputs #219

### 1.3.0

* Allow numeric disaggregaton #198
* Use only 2 segments for the auto target id #196
* Allow missing metadata to be altered #194
* Performance optimizations and logging option #192
* Allow the export filename to be configured #189
* Allow missing values in reporting status extra fields #188
* Input from the UN SDGs-SDMX API #187
* Better handling of common SDMX data fields #182
* Input for SDMX metadata #180
* Standalone indicators #179
* SDMX output for SDMX-compliant datasets #177

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
