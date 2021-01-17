# python standard imports
import xml.etree.ElementTree as etree

# markdown imports
from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor

# internal imports
from . import Citator

class CitationPostprocessor(Postprocessor):
    def __init__(self, citator, css_class='citation', use_id_forms=False):
        super().__init__()
        self.citator = citator
        self.css_class = css_class
        self.use_id_forms = use_id_forms
    def run(self, text):
        return self.citator.insert_links(
            text,
            css_class=self.css_class,
            id_forms=self.use_id_forms)

class CiteURLExtension(Extension):
    """Detects legal citations and inserts relevant hyperlinks."""
    def __init__(self, **kwargs):
        self.config = {
            'custom_schemas': [
                [],
                'List of paths to YAML files containing additional citation'
                + 'schemas to load. - Default: []',
            ],
            'use_defaults': [
                True,
                "Load CiteURL's default citation schemas? - Default: True"
            ],
            'use_id_forms': [
                True,
                "Recognize 'id.' shortform citations. - Default: True"
            ],
            'css_class': [
                'citation',
                'The class of <a> element to insert. - Default: citation'
            ]
        }
        super(CiteURLExtension, self).__init__(**kwargs)
    
    def extendMarkdown(self, md):
        custom_schemas = self.config['custom_schemas'][0] or []
        citator = Citator(
            *custom_schemas,
            defaults=self.config['use_defaults'][0]
        )
        md.postprocessors.register(
            CitationPostprocessor(
                citator,
                self.config['css_class'][0],
                self.config['use_id_forms'][0]
            ),
            "CiteURL",
            1
        )

def makeExtension(**kwargs):
    return CiteURLExtension(**kwargs)
