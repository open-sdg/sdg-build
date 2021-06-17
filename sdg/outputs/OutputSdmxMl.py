import os
import sdg
import pandas as pd
import numpy as np
import sdmx
import time
import uuid
from jinja2 import Template
from slugify import slugify
from sdmx.model import (
    SeriesKey,
    Key,
    AttributeValue,
    Observation,
    GenericTimeSeriesDataSet,
    StructureSpecificTimeSeriesDataSet,
    DataflowDefinition,
    Agency,
    PrimaryMeasureRelationship,
    DimensionRelationship,
)
from sdmx.message import (
    DataMessage,
    Header
)
from sdg.outputs import OutputBase
from sdg.schemas import SchemaInputBase
from sdg.schemas import SchemaInputSdmxMsd
from sdg import helpers
from sdg.data_schemas import DataSchemaInputSdmxDsd

class OutputSdmxMl(OutputBase):
    """Output SDG data/metadata in SDMX-ML."""


    def __init__(self, inputs, schema, output_folder='_site', translations=None,
                 indicator_options=None, dsd=None, default_values=None,
                 header_id=None, sender_id=None, structure_specific=False,
                 column_map=None, code_map=None, constrain_data=False,
                 request_params=None, constrain_meta=True, logging=None,
                 meta_ref_area=None, meta_reporting_type=None, msd=None):

        """Constructor for OutputSdmxMl.

        This output assumes the following:
        1. A DSD is already created and available
        2. All columns in the data correspond exactly to dimension IDs or a concept mapping is specified
        3. All values in the columns correspond exactly to codes in those dimensions' codelists or a code mapping is specified

        Notes on translation:
        SDMX data output does not need to be transated. Hence, data will always appear in
        an "sdmx" folder, and will never be translated in a language subfolder.
        By contrast, metadata IS language-specific to metadata will appear in
        the language folders, as with other outputs.

        Parameters
        ----------

        Inherits all the parameters from OutputBase, plus the following optional
        arguments (see above for the default values):

        dsd : string
            Remote URL of the SDMX DSD (data structure definition) or path to
            local file.
        msd : string
            Remote URL of the SDMX MSD (metadata structure definition) or path to
            local file. If omitted, the global MSD will be assumed.
        default_values : dict
            Since SDMX output is required to have a value for every dimension/attribute
            you may need to specify defaults here. If not specified here, defaults for
            attributes will be '' and defaults for dimensions will be '_T'.
        header_id : string or None
            Optional identifying string to put in the "ID" element in the header
            of the XML. If not specified, it will be "IREF" and a timestamp.
        sender_id : string or None
            Optional identifying string to put in the "id" attribut of the "Sender" element
            in the header of the XML. If not specified, it will be the current version
            of this library.
        structure_specific : boolean
            Whether to output as StructureSpecific instead of Generic data.
        column_map: string
            Remote URL of CSV column mapping or path to local CSV column mapping file
        code_map: string
            Remote URL of CSV code mapping or path to local CSV code mapping file
        constrain_data : boolean
            Whether to use the DSD to remove any rows of data that are not compliant.
            Defaults to False.
        constrain_meta : boolean
            Whether to use the MSD to remove any metadata fields that are
            not complaint. Defaults to True.
        meta_ref_area : string
            REF_AREA code to use in the metadata output. If omitted, will use
            the first available in a REF_AREA data column.
        meta_reporting_type : string
            REPORTING_TYPE code to use in the metadata output. If omitted, will use
            the first available in a REPORTING_TYPE data column.
        """
        OutputBase.__init__(self, inputs, schema, output_folder, translations,
            indicator_options, request_params=request_params, logging=logging)
        self.header_id = header_id
        self.sender_id = sender_id
        self.structure_specific = structure_specific
        self.constrain_data = constrain_data
        self.constrain_meta = constrain_meta
        self.dsd_path = dsd
        self.retrieve_dsd(dsd)
        self.msd_path = msd
        self.retrieve_msd(msd)
        self.data_schema = DataSchemaInputSdmxDsd(source=self.dsd)
        self.column_map = column_map
        self.code_map = code_map

        sdmx_folder = os.path.join(output_folder, 'sdmx')
        if not os.path.exists(sdmx_folder):
            os.makedirs(sdmx_folder, exist_ok=True)
        self.sdmx_folder = sdmx_folder
        meta_folder = os.path.join(sdmx_folder, 'meta')
        if not os.path.exists(meta_folder):
            os.makedirs(meta_folder, exist_ok=True)
        self.meta_folder = meta_folder

        self.default_values = {} if default_values is None else default_values
        self.meta_ref_area = meta_ref_area
        self.meta_reporting_type = meta_reporting_type


    def retrieve_dsd(self, dsd):
        self.dsd = helpers.sdmx.get_dsd(dsd, request_params=self.request_params)


    def retrieve_msd(self, msd):
        if msd is None:
            self.msd = SchemaInputTemporaryMsd(logging=self.logging)
        else:
            self.msd = SchemaInputSdmxMsd(schema_path=msd, logging=self.logging)


    def build(self, language=None):
        """Write the SDMX output. Overrides parent."""
        status = True

        # The SDMX output is a special case, and does not need to be
        # translated separately for each language. So we only continue
        # if this is an untranslated or language-agnostic build.
        if language is not None and language != 'untranslated':
            return status

        all_serieses = {}
        all_metadata_serieses = []
        metadata_template = Template(self.get_metadata_template())
        dfd = DataflowDefinition(id="OPEN_SDG_DFD", structure=self.dsd)
        time_period = next(dim for dim in self.dsd.dimensions if dim.id == 'TIME_PERIOD')
        header_info = self.get_header_info()
        header = self.create_header(header_info)

        metadata_base_vars = header_info.copy()

        for indicator_id in self.get_indicator_ids():
            indicator = self.get_indicator_by_id(indicator_id)
            data = indicator.data.copy()

            # Some hardcoded dataframe changes.
            data = data.rename(columns={
                'Value': 'OBS_VALUE',
                'Units': 'UNIT_MEASURE',
                'Series': 'SERIES',
                'Year': 'TIME_PERIOD',
            })
            # Any user-specified dataframe changes.
            self.apply_column_map(data)
            self.apply_code_map(data)

            if self.constrain_data:
                before = data.size
                data = indicator.get_data_matching_schema(self.data_schema, data=data)
                after = data.size
                message = '{indicator_id} - Removed {difference} rows while constraining data (out of {total}).'
                difference = str(before - after)
                self.warn(message, indicator_id=indicator_id, difference=difference, total=before)

            data = data.replace(np.nan, '', regex=True)
            if not data.empty:

                serieses = {}
                for _, row in data.iterrows():
                    series_key = self.dsd.make_key(SeriesKey, self.get_dimension_values(row, indicator))
                    series_key.attrib = self.get_series_attribute_values(row, indicator)
                    attributes = self.get_observation_attribute_values(row, indicator)
                    dimension_key = self.dsd.make_key(Key, values={
                        'TIME_PERIOD': str(row['TIME_PERIOD']),
                    })
                    observation = Observation(
                        series_key=series_key,
                        dimension=dimension_key,
                        attached_attribute=attributes,
                        value_for=self.dsd.measures[0],
                        value=row[self.dsd.measures[0].id],
                    )
                    if series_key not in serieses:
                        serieses[series_key] = []
                    serieses[series_key].append(observation)

                dataset = self.create_dataset(serieses)
                msg = DataMessage(data=[dataset], dataflow=dfd, header=header, observation_dimension=time_period)
                sdmx_path = os.path.join(self.sdmx_folder, indicator_id + '.xml')
                with open(sdmx_path, 'wb') as f:
                    status = status & f.write(sdmx.to_xml(msg))
                all_serieses.update(serieses)

            concepts = indicator.meta
            if self.constrain_meta and self.msd is not None:
                concepts = indicator.get_meta_matching_schema(self.msd)

            reporting_type = self.meta_reporting_type
            if reporting_type is None and 'REPORTING_TYPE' in data.columns and len(data) > 0:
                reporting_type = self.get_first_value_from_data_column(data, 'REPORTING_TYPE')
            ref_area = self.meta_ref_area
            if ref_area is None and 'REF_AREA' in data.columns and len(data) > 0:
                ref_area = self.get_first_value_from_data_column(data, 'REF_AREA')

            if concepts and ref_area is not None and reporting_type is not None:

                series_codes = helpers.sdmx.get_all_series_codes_from_indicator_id(indicator_id,
                    dsd_path=self.dsd_path,
                    request_params=self.request_params,
                )

                # Make sure the indicator is fully translated.
                for language in self.all_languages:
                    indicator.translate(language, self.translation_helper)

                concept_items = []
                for key in concepts:
                    translation_items = []
                    for language in self.all_languages:
                        translated_value = indicator.language(language).get_meta_field_value(key)
                        translation_items.append({
                            'language': language,
                            'value': translated_value,
                        })
                    concept_items.append({
                        'key': key,
                        'translations': translation_items,
                    })

                metadata_serieses = []
                for code in series_codes:
                    metadata_series = {
                        'set_id': uuid.uuid4(),
                        'series': code,
                        'reporting_type': reporting_type,
                        'ref_area': ref_area,
                        'concepts': concept_items,
                    }
                    metadata_serieses.append(metadata_series)

                metadata = metadata_base_vars.copy()
                metadata['serieses'] = metadata_serieses
                metadata_sdmx = metadata_template.render(metadata)
                meta_path = os.path.join(self.meta_folder, indicator_id + '.xml')
                with open(meta_path, 'w') as f:
                    status = status & f.write(metadata_sdmx)
                all_metadata_serieses = all_metadata_serieses + metadata_serieses

        dataset = self.create_dataset(all_serieses)
        msg = DataMessage(data=[dataset], dataflow=dfd, header=header, observation_dimension=time_period)
        all_sdmx_path = os.path.join(self.sdmx_folder, 'all.xml')
        with open(all_sdmx_path, 'wb') as f:
            status = status & f.write(sdmx.to_xml(msg))

        metadata = metadata_base_vars.copy()
        metadata['serieses'] = all_metadata_serieses
        metadata_sdmx = metadata_template.render(metadata)
        meta_path = os.path.join(self.meta_folder, 'all.xml')
        with open(meta_path, 'w') as f:
            status = status & f.write(metadata_sdmx)

        return status


    def create_header(self, info=None):
        if info is None:
            info = self.get_header_info()

        return Header(
            id=info['id'],
            test=info['test'],
            prepared=info['prepared'],
            sender=Agency(id=info['sender']),
        )


    def get_header_info(self):
        timestamp = time.time()
        header_id = self.header_id
        if header_id is None:
            header_id = 'IREF' + str(int(timestamp))
        else:
            header_id = slugify(header_id)
        sender_id = self.sender_id
        if sender_id is None:
            sender_id = 'open-sdg_sdg-build@' + slugify(sdg.__version__)
        else:
            sender_id = slugify(sender_id)
        return {
            'id': header_id,
            'test': True,
            'prepared': time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(timestamp)),
            'sender': sender_id,
        }


    def get_first_value_from_data_column(self, data, column):
        index = data[column].first_valid_index()
        return data[column].loc[index]


    def create_dataset(self, serieses):
        dataset_class = StructureSpecificTimeSeriesDataSet if self.structure_specific else GenericTimeSeriesDataSet
        return dataset_class(structured_by=self.dsd, series=serieses)


    def get_dimension_values(self, row, indicator):
        values = {}
        for dimension in self.dsd.dimensions:
            # Skip the TIME_PERIOD dimension because it is used as the "observation dimension".
            if dimension.id == 'TIME_PERIOD':
                continue
            if dimension.id in row and row[dimension.id] != '':
                value = row[dimension.id]
            else:
                value = self.get_dimension_default(dimension.id, indicator)
            values[dimension.id] = str(value)
        return values


    def get_observation_attribute_values(self, row, indicator):
        return self.get_attribute_values(row, indicator, 'observation')


    def get_series_attribute_values(self, row, indicator):
        return self.get_attribute_values(row, indicator, 'series')


    def get_attribute_values(self, row, indicator, relationship_type):
        values = {}
        for attribute in self.dsd.attributes:
            valid_attribute = False
            if relationship_type == 'series' and isinstance(attribute.related_to, DimensionRelationship):
                valid_attribute = True
            elif relationship_type == 'observation' and attribute.related_to is PrimaryMeasureRelationship:
                valid_attribute = True
            if valid_attribute:
                value = row[attribute.id] if attribute.id in row else self.get_attribute_default(attribute.id, indicator)
                if value != '':
                    values[attribute.id] = AttributeValue(value_for=attribute, value=str(value))
        return values


    def get_default_values(self):
        return self.default_values


    def get_dimension_default(self, dimension, indicator):
        indicator_value = indicator.get_meta_field_value(dimension)
        if indicator_value is not None:
            return indicator_value
        defaults = self.get_default_values()
        if dimension not in defaults:
            defaults = {
                'FREQ': 'A',
                'REPORTING_TYPE': 'N'
            }
        if dimension in defaults:
            return defaults[dimension]
        else:
            return '_T'


    def get_attribute_default(self, attribute, indicator):
        indicator_value = indicator.get_meta_field_value(attribute)
        if indicator_value is not None:
            return indicator_value
        defaults = self.get_default_values()
        if attribute not in defaults:
            defaults = {
                'UNIT_MULT': '0',
                'UNIT_MEASURE': 'NUMBER',
                'OBS_STATUS': 'A',
            }
        if attribute in defaults:
            return defaults[attribute]
        else:
            return ''


    def apply_column_map(self, data):
        if self.column_map is not None:
            column_map=pd.read_csv(self.column_map)
            column_dict = dict(zip(column_map['Text'], column_map['Value']))
            data.rename(columns=column_dict, inplace=True)
        return data


    def apply_code_map(self, data):
        if self.code_map is not None:
            code_map=pd.read_csv(self.code_map)
            code_dict = {}
            for _, row in code_map.iterrows():
                if row['Dimension'] not in code_dict:
                    code_dict[row['Dimension']] = {}
                code_dict[row['Dimension']][row['Text']] = row['Value']
            data.replace(to_replace=code_dict, value=None, inplace=True)
        return data


    def get_documentation_title(self):
        return 'SDMX output'


    def get_documentation_content(self, languages=None, baseurl=''):

        indicator_ids = self.get_documentation_indicator_ids()

        data_endpoint = 'sdmx/{indicator_id}.xml'
        meta_endpoint = 'sdmx/meta/{indicator_id}.xml'
        output = '<p>' + self.get_documentation_description() + ' Examples are below:<p>'

        output += '<ul>'
        data_path = data_endpoint.format(indicator_id='all')
        meta_path = meta_endpoint.format(indicator_id='all')
        output += '<li><a href="' + baseurl + data_path + '">' + data_path + ' (data)</a></li>'
        output += '<li><a href="' + baseurl + meta_path + '">' + meta_path + ' (metadata)</a></li>'
        for indicator_id in indicator_ids:
            data_path = data_endpoint.format(indicator_id=indicator_id)
            meta_path = meta_endpoint.format(indicator_id=indicator_id)
            output += '<li><a href="' + baseurl + data_path + '">' + data_path + ' (data)</a></li>'
            output += '<li><a href="' + baseurl + meta_path + '">' + meta_path + ' (metadata)</a></li>'
        output += '<li>etc...</li>'
        output += '</ul>'

        return output


    def get_documentation_description(self):
        description = (
            "This output has an SDMX file for each indicator's data, "
            "plus one SDMX file with all indicator data. This data uses "
            "numbers and codes only, so is not specific to any language."
            "The metadata is output in a 'meta' subfolder' and similarly "
            "has one per indicator plus an 'all' file. Translations of "
            "the metadata are included in each file using the 'lang' "
            "attribute."
        )
        return description


    def validate(self):
        """Validate the data for the indicators."""

        # Need to figure out SDMX validation.
        return True


    def get_metadata_template(self):
        return """<?xml version="1.0" encoding="utf-8"?>
<mes:GenericMetadata xmlns:mes="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message" xmlns:gen="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/metadata/generic" xmlns:com="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common">
  <mes:Header>
    <mes:ID>{{ id }}</mes:ID>
    <mes:Test>{{ test }}</mes:Test>
    <mes:Prepared>{{ prepared }}</mes:Prepared>
    <mes:Sender id="{{ sender }}"/>
    <mes:Structure structureID="MDS1">
      <com:Structure>
        <URN>urn:sdmx:org.sdmx.infomodel.metadatastructure.MetadataStructure=IAEG-SDGs:SDG_MSD(0.3)</URN>
      </com:Structure>
    </mes:Structure>
  </mes:Header>
  {% for series in serieses %}
  <mes:MetadataSet structureRef="MDS1" setID="{{ series.set_id }}">
    <com:Name xml:lang="en">SDG METADATA SET</com:Name>
    <gen:Report id="SDG_META_RPT">
      <gen:Target id="KEY_TARGET">
        <gen:ReferenceValue id="DIMENSION_DESCRIPTOR_VALUES_TARGET">
          <gen:DataKey>
            <com:KeyValue id="SERIES">
              <com:Value>{{ series.series }}</com:Value>
            </com:KeyValue>
            <com:KeyValue id="REPORTING_TYPE">
              <com:Value>{{ series.reporting_type }}</com:Value>
            </com:KeyValue>
            <com:KeyValue id="REF_AREA">
              <com:Value>{{ series.ref_area }}</com:Value>
            </com:KeyValue>
          </gen:DataKey>
        </gen:ReferenceValue>
        <gen:ReferenceValue id="Dataflow">
          <gen:ObjectReference>
            <URN>urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=IAEG-SDGs:DF_SDG_GLC(1.0)</URN>
          </gen:ObjectReference>
        </gen:ReferenceValue>
      </gen:Target>
      <gen:AttributeSet>
        {% for concept in series.concepts %}
        <gen:ReportedAttribute id="{{ concept.key }}">
          {% for translation in concept.translations %}
          <com:Text xml:lang="{{ translation.language }}"><![CDATA[{{ translation.value }}]]></com:Text>
          {% endfor %}
        </gen:ReportedAttribute>
        {% endfor %}
      </gen:AttributeSet>
    </gen:Report>
  </mes:MetadataSet>
  {% endfor %}
</mes:GenericMetadata>
        """

class SchemaInputTemporaryMsd(SchemaInputBase):
    """Temporary hardcoding of the MSD since it is not published yet."""
    def load_schema(self):
        schema = {
            "type": "object",
            "properties": {}
        }

        concepts = [
            {
                "id": "SDG_INDICATOR_INFO",
                "name": "0. Indicator information",
                "section": "SDG_INDICATOR_INFO"
            },
            {
                "id": "SDG_GOAL",
                "name": "0.a. Goal",
                "section": "SDG_INDICATOR_INFO"
            },
            {
                "id": "SDG_TARGET",
                "name": "0.b. Target",
                "section": "SDG_INDICATOR_INFO"
            },
            {
                "id": "SDG_INDICATOR",
                "name": "0.c. Indicator",
                "section": "SDG_INDICATOR_INFO"
            },
            {
                "id": "SDG_SERIES_DESCR",
                "name": "0.d. Series",
                "section": "SDG_INDICATOR_INFO"
            },
            {
                "id": "META_LAST_UPDATE",
                "name": "0.e. Metadata update",
                "section": "SDG_INDICATOR_INFO"
            },
            {
                "id": "SDG_RELATED_INDICATORS",
                "name": "0.f. Related indicators",
                "section": "SDG_INDICATOR_INFO"
            },
            {
                "id": "SDG_CUSTODIAN_AGENCIES",
                "name": "0.g. International organisations(s) responsible for global monitoring",
                "section": "SDG_INDICATOR_INFO"
            },
            {
                "id": "CONTACT",
                "name": "1. Data reporter",
                "section": "CONTACT"
            },
            {
                "id": "CONTACT_ORGANISATION",
                "name": "1.a. Organisation",
                "section": "CONTACT"
            },
            {
                "id": "CONTACT_NAME",
                "name": "1.b. Contact person(s)",
                "section": "CONTACT"
            },
            {
                "id": "ORGANISATION_UNIT",
                "name": "1.c. Contact organisation unit",
                "section": "CONTACT"
            },
            {
                "id": "CONTACT_FUNCT",
                "name": "1.d. Contact person function",
                "section": "CONTACT"
            },
            {
                "id": "CONTACT_PHONE",
                "name": "1.e. Contact phone",
                "section": "CONTACT"
            },
            {
                "id": "CONTACT_MAIL",
                "name": "1.f. Contact mail",
                "section": "CONTACT"
            },
            {
                "id": "CONTACT_EMAIL",
                "name": "1.g. Contact email",
                "section": "CONTACT"
            },
            {
                "id": "IND_DEF_CON_CLASS",
                "name": "2. Definition, concepts, and classifications",
                "section": "IND_DEF_CON_CLASS"
            },
            {
                "id": "STAT_CONC_DEF",
                "name": "2.a. Definition and concepts",
                "section": "IND_DEF_CON_CLASS"
            },
            {
                "id": "UNIT_MEASURE",
                "name": "2.b. Unit of measure",
                "section": "IND_DEF_CON_CLASS"
            },
            {
                "id": "CLASS_SYSTEM",
                "name": "2.c. Classifications",
                "section": "IND_DEF_CON_CLASS"
            },
            {
                "id": "SRC_TYPE_COLL_METHOD",
                "name": "3. Data source type and collection method",
                "section": "SRC_TYPE_COLL_METHOD"
            },
            {
                "id": "SOURCE_TYPE",
                "name": "3.a. Data sources",
                "section": "SRC_TYPE_COLL_METHOD"
            },
            {
                "id": "COLL_METHOD",
                "name": "3.b. Data collection method",
                "section": "SRC_TYPE_COLL_METHOD"
            },
            {
                "id": "FREQ_COLL",
                "name": "3.c. Data collection calendar",
                "section": "SRC_TYPE_COLL_METHOD"
            },
            {
                "id": "REL_CAL_POLICY",
                "name": "3.d. Data release calendar",
                "section": "SRC_TYPE_COLL_METHOD"
            },
            {
                "id": "DATA_SOURCE",
                "name": "3.e. Data providers",
                "section": "SRC_TYPE_COLL_METHOD"
            },
            {
                "id": "COMPILING_ORG",
                "name": "3.f. Data compilers",
                "section": "SRC_TYPE_COLL_METHOD"
            },
            {
                "id": "INST_MANDATE",
                "name": "3.g. Institutional mandate",
                "section": "SRC_TYPE_COLL_METHOD"
            },
            {
                "id": "OTHER_METHOD",
                "name": "4. Other methodological considerations",
                "section": "OTHER_METHOD"
            },
            {
                "id": "RATIONALE",
                "name": "4.a. Rationale",
                "section": "OTHER_METHOD"
            },
            {
                "id": "REC_USE_LIM",
                "name": "4.b. Comment and limitations",
                "section": "OTHER_METHOD"
            },
            {
                "id": "DATA_COMP",
                "name": "4.c. Method of computation",
                "section": "OTHER_METHOD"
            },
            {
                "id": "DATA_VALIDATION",
                "name": "4.d. Validation",
                "section": "OTHER_METHOD"
            },
            {
                "id": "ADJUSTMENT",
                "name": "4.e. Adjustments",
                "section": "OTHER_METHOD"
            },
            {
                "id": "IMPUTATION",
                "name": "4.f. Treatment of missing values (i) at country level and (ii) at regional level",
                "section": "OTHER_METHOD"
            },
            {
                "id": "REG_AGG",
                "name": "4.g. Regional aggregations",
                "section": "OTHER_METHOD"
            },
            {
                "id": "DOC_METHOD",
                "name": "4.h. Methods and guidance available to countries for the compilation of the data at the national level",
                "section": "OTHER_METHOD"
            },
            {
                "id": "QUALITY_MGMNT",
                "name": "4.i. Quality management",
                "section": "OTHER_METHOD"
            },
            {
                "id": "QUALITY_ASSURE",
                "name": "4.j. Quality assurance",
                "section": "OTHER_METHOD"
            },
            {
                "id": "QUALITY_ASSMNT",
                "name": "4.k. Quality assessment",
                "section": "OTHER_METHOD"
            },
            {
                "id": "COVERAGE",
                "name": "5. Data availability and disaggregation",
                "section": "COVERAGE"
            },
            {
                "id": "COMPARABILITY",
                "name": "6. Comparability/deviation from international standards",
                "section": "COMPARABILITY"
            },
            {
                "id": "OTHER_DOC",
                "name": "7. References and Documentation",
                "section": "OTHER_DOC"
            }
        ]
        for concept in concepts:
            self.add_item_to_field_order(concept['id'])
            jsonschema_field = {
                'type': ['string', 'null'],
                'title': concept['name'],
                'translation_key': concept['section'] + '.' + concept['id'],
            }
            schema['properties'][concept['id']] = jsonschema_field

        self.schema = schema
