from sdg.inputs import InputMetaFiles
import yamlmd

class InputYamlMdMeta(InputMetaFiles):
    """Sources of SDG metadata that are local .md files containing Yaml."""

    def read_meta_at_path(self, filepath):
        meta_md = yamlmd.read_yamlmd(filepath)
        meta = dict(meta_md[0])
        meta['page_content'] = ''.join(meta_md[1])
        return meta
