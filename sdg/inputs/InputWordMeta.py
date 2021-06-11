import string
import re
from sdg.inputs import InputMetaFiles
import mammoth
from pyquery import PyQuery as pq

class InputWordMeta(InputMetaFiles):
    """Sources of SDG metadata that are local Word files using a standard
    template that is compliant with the SDMX MSD. This is coded to work with
    this template: https://github.com/sdmx-sdgs/metadata (currently v3.2) """

    def read_meta_at_path(self, filepath):
        meta = {}
        with open(filepath, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file, **self.get_mammoth_options())
            html = result.value

            if len(result.messages) > 0:
                self.debug('Messages while reading ' + filepath)
                for message in result.messages:
                    self.debug(str(message))
            d = pq('<body>' + html + '</body>')
            self.clean_html(d)

            concept_columns = d.find('table > tr > td:first-child > p')
            for concept_column_left in concept_columns:
                concept_name = self.parse_concept_name(concept_column_left, d)
                if self.is_concept_name_valid(concept_name):
                    concept_column_right = d(concept_column_left).parent().siblings('td')
                    footnotes = self.parse_footnotes(concept_column_right, d)
                    if self.is_concept_value_valid(concept_column_right, d):
                        concept_value = self.parse_concept_value(concept_column_right, d)
                        if len(footnotes) > 0:
                            concept_value += self.wrap_footnotes(footnotes)
                        concept_key = self.get_concept_key(concept_name)
                        meta[concept_key] = concept_value

        return meta


    def clean_html(self, d):
        d('a[id^=_]').remove()


    def get_mammoth_options(self):
        style_map = """
        p[style-name='M.Header'] => h1:fresh
        p[style-name='M.Sub.Header'] => h2:fresh
        u => u
        """
        return {
            'style_map': style_map
        }


    def is_concept_name_valid(self, concept_name):
        return self.get_concept_key(concept_name) is not None


    def is_concept_value_valid(self, node, d):
        # Microsoft Word can put in some weird stuff. This is a sanity check that
        # we actually have real content.
        text = re.sub(r'\W+', '', d(node).text()).strip()
        return len(text) > 0


    def parse_concept_name(self, node, d):
        return d(node).text()


    def parse_concept_value(self, node, d):
        return d(node).html()


    def parse_footnotes(self, node, d):
        parsed = []
        anchors = [anchor for anchor in d(node).find('a') if self.is_footnote(anchor, d)]
        footnotes = [d(d(anchor).attr('href')) for anchor in anchors]
        numbers = [self.parse_footnote_number(d(anchor).text()) for anchor in anchors]

        for idx, footnote in enumerate(footnotes):
            number = numbers[idx]
            markup = '<div><sup class="footnote-number" id="footnote-{num}">{num}</sup>{contents}</div>'
            parsed.append(markup.format(num=number, contents=d(footnote).html()))
        return parsed


    def is_footnote(self, anchor, d):
        href = d(anchor).attr('href')
        starts_with_hash = href and href.startswith('#')
        parent = d(anchor).parent()
        parent_is_sup = len(parent) > 0 and parent[0].tag == 'sup'
        return starts_with_hash and parent_is_sup


    def parse_footnote_number(self, text):
        text = text.replace('[', '').replace(']', '')
        return int(text.strip(string.ascii_letters))


    def wrap_footnotes(self, footnotes):
        return '<div class="footnotes">' + ''.join(footnotes) + '</div>'


    def get_concept_key(self, concept_name):
        fuzzy = self.normalize_concept_name(concept_name)
        for concept in self.get_concept_store():
            if fuzzy == self.normalize_concept_name(concept['name']):
                return concept['id']
        return None


    def get_concept_store(self):
        return [
            {
                "id": "SDG_INDICATOR_INFO",
                "name": "0. Indicator information",
            },
            {
                "id": "SDG_GOAL",
                "name": "0.a. Goal",
            },
            {
                "id": "SDG_TARGET",
                "name": "0.b. Target",
            },
            {
                "id": "SDG_INDICATOR",
                "name": "0.c. Indicator",
            },
            {
                "id": "SDG_SERIES_DESCR",
                "name": "0.d. Series",
            },
            {
                "id": "META_LAST_UPDATE",
                "name": "0.e. Metadata update",
            },
            {
                "id": "SDG_RELATED_INDICATORS",
                "name": "0.f. Related indicators",
            },
            {
                "id": "SDG_CUSTODIAN_AGENCIES",
                "name": "0.g. International organisations(s) responsible for global monitoring",
            },
            {
                "id": "CONTACT",
                "name": "1. Data reporter",
            },
            {
                "id": "CONTACT_ORGANISATION",
                "name": "1.a. Organisation",
            },
            {
                "id": "CONTACT_NAME",
                "name": "1.b. Contact person(s)",
            },
            {
                "id": "ORGANISATION_UNIT",
                "name": "1.c. Contact organisation unit",
            },
            {
                "id": "CONTACT_FUNCT",
                "name": "1.d. Contact person function",
            },
            {
                "id": "CONTACT_PHONE",
                "name": "1.e. Contact phone",
            },
            {
                "id": "CONTACT_MAIL",
                "name": "1.f. Contact mail",
            },
            {
                "id": "CONTACT_EMAIL",
                "name": "1.g. Contact email",
            },
            {
                "id": "IND_DEF_CON_CLASS",
                "name": "2. Definition, concepts, and classifications",
            },
            {
                "id": "STAT_CONC_DEF",
                "name": "2.a. Definition and concepts",
            },
            {
                "id": "UNIT_MEASURE",
                "name": "2.b. Unit of measure",
            },
            {
                "id": "CLASS_SYSTEM",
                "name": "2.c. Classifications",
            },
            {
                "id": "SRC_TYPE_COLL_METHOD",
                "name": "3. Data source type and collection method",
            },
            {
                "id": "SOURCE_TYPE",
                "name": "3.a. Data sources",
            },
            {
                "id": "COLL_METHOD",
                "name": "3.b. Data collection method",
            },
            {
                "id": "FREQ_COLL",
                "name": "3.c. Data collection calendar",
            },
            {
                "id": "REL_CAL_POLICY",
                "name": "3.d. Data release calendar",
            },
            {
                "id": "DATA_SOURCE",
                "name": "3.e. Data providers",
            },
            {
                "id": "COMPILING_ORG",
                "name": "3.f. Data compilers",
            },
            {
                "id": "INST_MANDATE",
                "name": "3.g. Institutional mandate",
            },
            {
                "id": "OTHER_METHOD",
                "name": "4. Other methodological considerations",
            },
            {
                "id": "RATIONALE",
                "name": "4.a. Rationale",
            },
            {
                "id": "REC_USE_LIM",
                "name": "4.b. Comment and limitations",
            },
            {
                "id": "DATA_COMP",
                "name": "4.c. Method of computation",
            },
            {
                "id": "DATA_VALIDATION",
                "name": "4.d. Validation",
            },
            {
                "id": "ADJUSTMENT",
                "name": "4.e. Adjustments",
            },
            {
                "id": "IMPUTATION",
                "name": "4.f. Treatment of missing values (i) at country level and (ii) at regional level",
            },
            {
                "id": "REG_AGG",
                "name": "4.g. Regional aggregations",
            },
            {
                "id": "DOC_METHOD",
                "name": "4.h. Methods and guidance available to countries for the compilation of the data at the national level",
            },
            {
                "id": "QUALITY_MGMNT",
                "name": "4.i. Quality management",
            },
            {
                "id": "QUALITY_ASSURE",
                "name": "4.j. Quality assurance",
            },
            {
                "id": "QUALITY_ASSMNT",
                "name": "4.k. Quality assessment",
            },
            {
                "id": "COVERAGE",
                "name": "5. Data availability and disaggregation",
            },
            {
                "id": "COMPARABILITY",
                "name": "6. Comparability/deviation from international standards",
            },
            {
                "id": "OTHER_DOC",
                "name": "7. References and Documentation",
            }
        ]


    def normalize_concept_name(self, concept_name):
        return concept_name.lower().replace('.', '').strip()
