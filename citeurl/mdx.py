# python standard imports
import xml.etree.ElementTree as etree

# markdown imports
from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor

# internal imports
from . import Citator

class CitationPostprocessor(Postprocessor):
    def __init__(
        self,
        citator,
        attributes: dict,
        link_detailed_ids: bool,
        link_plain_ids: bool
    ):
        super().__init__()
        self.citator = citator
        self.attributes = attributes
        self.link_detailed_ids = link_detailed_ids
        self.link_plain_ids = link_plain_ids
    def run(self, text):
        return self.citator.insert_links(
            text,
            attrs=self.attributes,
            link_detailed_ids=self.link_detailed_ids,
            link_plain_ids=self.link_plain_ids
        )

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
            'link_detailed_ids': [
                True,
                "Whether to link citations like 'Id. at 3' - Default: True"
            ],
            'link_plain_ids': [
                False,
                "Whether to link citations like 'Id.' - Defualt: False"
            ],
            'attributes': [
                {'class': 'citation'},
                ("A dictionary of attributes (besides href) that the inserted"
                + " links should have. - Default: {'class': 'citation'}")
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
                self.config['attributes'][0],
                self.config['link_detailed_ids'][0],
                self.config['link_plain_ids'][0]
            ),
            "CiteURL",
            1
        )

def makeExtension(**kwargs):
    return CiteURLExtension(**kwargs)
