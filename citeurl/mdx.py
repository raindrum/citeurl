# python standard imports
import xml.etree.ElementTree as etree

# markdown imports
from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor

# internal imports
from . import Citator, DEFAULT_ID_BREAKS

# store citator in a global variable so it isn't remade each document
CITATOR: Citator = None

class CitationPostprocessor(Postprocessor):
    def __init__(
        self,
        citator,
        attributes: dict,
        link_detailed_ids: bool,
        link_plain_ids: bool,
        break_id_on_regex: str
    ):
        super().__init__()
        self.citator = citator
        self.attributes = attributes
        self.link_detailed_ids = link_detailed_ids
        self.link_plain_ids = link_plain_ids
        self.id_break_regex=break_id_on_regex
    def run(self, text):
        return self.citator.insert_links(
            text,
            attrs=self.attributes,
            link_detailed_ids=self.link_detailed_ids,
            link_plain_ids=self.link_plain_ids,
            id_break_regex=self.id_break_regex
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
                "Whether to link citations like 'Id.' - Default: False"
            ],
            'break_id_on_regex': [
                DEFAULT_ID_BREAKS,
                "Anywhere this string (parsed as regex) appears in the text, "
                + "chains of citations like 'id.' will be interrupted. Note "
                + "that this is based on the output HTML, *not* the original "
                + f"Markdown text. - Default: {DEFAULT_ID_BREAKS}"
            ],
            'attributes': [
                {'class': 'citation'},
                ("A dictionary of attributes (besides href) that the inserted"
                + " links should have. - Default: '{'class': 'citation'}'")
            ]
        }
        super(CiteURLExtension, self).__init__(**kwargs)
    
    def extendMarkdown(self, md):
        global CITATOR
        if not CITATOR:
            CITATOR = Citator(
                yaml_paths = self.config['custom_schemas'][0] or [],
                defaults = self.config['use_defaults'][0]
            )
        md.postprocessors.register(
            CitationPostprocessor(
                CITATOR,
                self.config['attributes'][0],
                self.config['link_detailed_ids'][0],
                self.config['link_plain_ids'][0],
                self.config['break_id_on_regex'][0],
            ),
            "CiteURL",
            1
        )

def makeExtension(**kwargs):
    return CiteURLExtension(**kwargs)
