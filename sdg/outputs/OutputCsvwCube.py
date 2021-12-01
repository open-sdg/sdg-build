# -*- coding: utf-8 -*-

# Probably not needed once you've cleaned up
import datetime
import glob
from pathlib import Path
import yaml

from sdg.outputs import OutputDataPackage
from sdg.Indicator import Indicator
from sdg.inputs.InputYamlMdMeta import InputYamlMdMeta
from frictionless.package import Package

from csvcubed.models.cube.qb.catalog import CatalogMetadata
from csvcubed.models.cube.qb import (
    Cube,
    QbColumn,
    ExistingQbDimension,
    NewQbAttribute,
    NewQbAttributeValue,
    ExistingQbMeasure,
    QbSingleMeasureObservationValue,
    ExistingQbUnit
)
from csvcubed.writers.qbwriter import QbWriter


class OutputCsvwCube(OutputDataPackage):
    """Output a CSVW package (CSV and JSON file).
    """

    def __init__(self, inputs, schema, **kwargs):
        """ Constructor for OutputCsvw.

        Parameters
        ----------
        inputs : inherit
        schema : inherit
        """
        self.inputs = inputs
        OutputDataPackage.__init__(self, inputs, schema, **kwargs)


    def get_base_folder(self):
        return 'csvw'

    def write_indicator_package(self, package, descriptor_path, indicator, language=None):
        self.write_csvw_package(package, descriptor_path, indicator, language=language)


    def write_top_level_package(self, path, language=None):
        # TODO, investigate - this self.top_level_pacakge is likely the "_site/csvw/all.json"
        self.write_csvw_package(self.top_level_package, path, None, language=language)


    def write_csvw_package(self, package: Package, path: str, indicator: Indicator, language=None):

        output_dir = Path(path).parent

        # If it's the summary skip it (for now), it's a summary level resource 
        # not a dataset defining an indicator
        if indicator is not None:

            source_metadata: dict = self._get_metadata_as_dict(indicator.meta["indicator"])
            catalog: CatalogMetadata = map_metadata_to_catalog(source_metadata)
            
            cube = Cube(catalog)
            cube.data = indicator.data # pandas.DataFrame
            measure_component = ExistingQbMeasure("http://gss-data.org.uk/def/measure/indicator")
            unit_component = ExistingQbUnit("http://TODO.WORK.OUT.WHAT.THIS.NEEDS.TO.BE")
            cube.columns = [
                QbColumn(
                    "Year",
                    ExistingQbDimension("http://purl.org/linked-data/sdmx/2009/dimension#refPeriod"),
                    "http://reference.data.gov.uk/id/year/{year}",
                    ),
                QbColumn(
                    "Value",
                    QbSingleMeasureObservationValue(
                        measure=measure_component,
                        unit=unit_component,
                        data_type="integer",
                    )
                )]

            # If it's not period or value then (for now) I'm specifying it as
            # an attribute.... it'll be a lot more complicated than that.
            # TODO - are the Value/Year naming conventions absolute/written in stone?
            for column_label in [x for x in cube.data.columns if x not in ["Value", "Year"]]:
                cube.columns.append(

                    # TODO - no idea what the attribute uri for an arbitrary QbAttribute would be
                    QbColumn(
                        column_label,
                        NewQbAttribute(
                            column_label,
                            "http://www.not-a-real-url/but-pretened-to-be#whatever",
                            [NewQbAttributeValue(x) for x in list(cube.data[column_label].unique())
                            if str(x) != "nan"]
                        )
                    )
                )

            qb_writer = QbWriter(cube)
            qb_writer.cube.data = None # csv is already output
            qb_writer.write(output_dir)

        else:
            # TODO: figure this out
            # this is the all.json appearing one level up from the indicators,
            # it's likely a necessary component for frontend navigation.
            pass

    def _get_metadata_as_dict(self, indicator_id: str) -> (dict):
        """
        Given an indicator ID, retirns a dictionary of the Yaml metadata
        input resource for that indicator
        """

        yaml_inputs = [x for x in self.inputs if isinstance(x, InputYamlMdMeta)]
        for yaml_input in yaml_inputs:

            # Note: its .yml not the implied .md
            path_pattern = f'{yaml_input.path_pattern.rstrip(".md")}.yml'
            globbed = glob.glob(path_pattern)
            for meta_file in globbed:
                metadata_indicator_file_name = Path(meta_file).name.rstrip(".yml")

                # Making an assumption, so assert the assumption
                assert metadata_indicator_file_name.startswith("indicator_"), (
                    f'Aborting, file {metadata_indicator_file_name} does not '
                    'have expected "indicator_" prefix.')

                metadata_indicator_file_name = metadata_indicator_file_name.lstrip("indicator_").replace("-", ".")
                
                if metadata_indicator_file_name == indicator_id:
                    with open(Path(meta_file).absolute()) as f:
                        meta_dict = yaml.load(f, Loader=yaml.SafeLoader)
                    break

            else:
                raise FileNotFoundError('Could not find metadata file for indicator: {indicator_id}')
   
        return meta_dict


    def get_documentation_title(self):
        return 'CSVW'


    def get_documentation_description(self):
        return """This output produces CSVW representing 5* linked open dara cubes for each indicator."""



def map_metadata_to_catalog(source_metadata: dict) -> (CatalogMetadata):
    """
    Helper function to figure out the correct values from the metadata dict
    (taken from the /meta/<indicator>.yml) to pass into the
    CatalogMetadata constructor.
    """

    return CatalogMetadata(
                    title="data.csv",
                    summary=source_metadata["SDG_INDICATOR"],
                    description=source_metadata["STAT_CONC_DEF"],
                    creator_uri="creator",
                    publisher_uri="publisher_uri",
                    landing_page_uri="landing_page_uri",
                    theme_uris=["theme1", "theme2"],
                    keywords=[],
                    dataset_issued=datetime.datetime.now(),
                    dataset_modified=datetime.datetime.now(),
                    license_uri="https://opensource.org/licenses/mit-license.php",
                    public_contact_point_uri="contact@somesortofcontact.net"
                )