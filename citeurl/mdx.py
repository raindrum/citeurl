# python standard imports
import xml.etree.ElementTree as etree

# markdown imports
from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor

# internal imports
from . import Citator

class CitationPostprocessor(Postprocessor):
    def __init__(self, citator, css_class):
        super().__init__()
        self.citator = citator
        self.css_class = css_class
    def run(self, text):
        return self.citator.insert_links(text, css_class=self.css_class)

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
            'css_class': [
                'citation',
                'The class of <a> element to insert. - Default: citation'
            ]
        }
        super(CiteURLExtension, self).__init__(**kwargs)
        self.css_class = self.config['css_class'][0]
    
    def extendMarkdown(self, md):
        custom_schemas = self.config['custom_schemas'][0] or []
        citator = Citator(
            *custom_schemas,
            defaults=self.config['use_defaults'][0]
        )
        md.postprocessors.register(
            CitationPostprocessor(citator, self.css_class),
            "CiteURL",
            1
        )

def makeExtension(**kwargs):
    return CiteURLExtension(**kwargs)
