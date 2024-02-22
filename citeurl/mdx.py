"""
A Python-Markdown extension to detect citations and insert them into
the processed text as hyperlinks.
"""

# python standard imports
import re
import xml.etree.ElementTree as etree
from pathlib import Path

# markdown imports
from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor

# internal imports
from . import Citator, insert_links
from .citator import _get_default_citator

# store citator in a global variable so it isn't remade each document
CITATOR: Citator = None

class CitationPostprocessor(Postprocessor):
    def __init__(
        self,
        citator,
        attributes: dict,
        redundant_links: bool,
        URL_optional: bool,
        break_id_on_regex: str,
        ignore_markup: bool,
    ):
        super().__init__()
        self.citator = citator
        self.attributes = attributes
        self.redundant_links = redundant_links
        self.URL_optional = URL_optional
        self.ignore_markup = ignore_markup,
        
        if break_id_on_regex:
            self.id_breaks = re.compile(break_id_on_regex)
        else:
            self.id_breaks = None
    
    def run(self, text):
        return insert_links(
            text = text,
            attrs = self.attributes,
            redundant_links = self.redundant_links,
            URL_optional = self.URL_optional,
            id_breaks = self.id_breaks,
            ignore_markup = self.ignore_markup,
            citator = self.citator,
        )

class CiteURLExtension(Extension):
    """Detects legal citations and inserts relevant hyperlinks."""
    def __init__(self, **kwargs):
        self.config = {
            'custom_templates': [
                [],
                'List of paths to YAML files containing additional citation'
                + 'templates to load. - Default: []',
            ],
            'use_defaults': [
                True,
                "Load CiteURL's default citation templates? - Default: True"
            ],
            'redundant_links': [
                False,
                (
                    "Whether to insert links links whose URLs are identical "
                    "to the previous URL"
                )
            ],
            'URL_optional': [
                False,
                (
                    "Whether to add <a> elements for citations that have "
                    "no URL"
                )
            ],
            'break_id_on_regex': [
                None,
                "Anywhere this string (parsed as regex) appears in the text, "
                + "chains of citations like 'id.' will be interrupted. Note "
                + "that this is based on the output HTML, *not* the original "
                + f"Markdown text."
            ],
            'attributes': [
                {'class': 'citation'},
                ("A dictionary of attributes (besides href) that the inserted"
                + " links should have. - Default: '{'class': 'citation'}'")
            ],
            'ignore_markup': [
                True,
                (
                    "Whether to detect citations even when they are "
                    'interrupted by inline markup, like "<i>Id.</i> at 32. '
                    'Default: True'
                )
            ],
        }
        super(CiteURLExtension, self).__init__(**kwargs)
    
    def extendMarkdown(self, md):
        global CITATOR
        if not CITATOR:
            if self.config['use_defaults'][0]:
                CITATOR = _get_default_citator()
            else:
                CITATOR = Citator(defaults=None)
        for path in self.config['custom_templates'][0] or []:
            CITATOR.load_yaml(Path(path).read_text())
        
        md.postprocessors.register(
            CitationPostprocessor(
                CITATOR,
                self.config['attributes'][0],
                self.config['redundant_links'][0],
                self.config['URL_optional'][0],
                self.config['break_id_on_regex'][0],
                self.config['ignore_markup'][0],
            ),
            "CiteURL",
            1
        )

def makeExtension(**kwargs):
    return CiteURLExtension(**kwargs)
