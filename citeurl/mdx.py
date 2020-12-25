# python standard imports
import xml.etree.ElementTree as etree

# markdown imports
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor

# internal imports
from . import Schema_Set

DEFAULT_CSS_CLASS = 'citation'

class CitationInlineProcessor(InlineProcessor):
    ANCESTOR_EXCLUDES = ('a',)
    def __init__(self, schema, css_class, md):
        super().__init__(schema.regex.pattern, md)
        self.schema = schema
        self.css_class = css_class

    def handleMatch(self, m, data):
        try:
            url = self.schema._url_from_match(m)
        except KeyError: # return text unchanged if URL generation failed
            return m.group(0), m.start(0), m.end(0)
        el = etree.Element('a')
        el.attrib={
            'href': url,
            'class': self.css_class
        }
        el.text = m.group(0)
        return el, m.start(0), m.end(0)
        
class CiteURLExtension(Extension):
    """Detects legal citations and inserts relevant hyperlinks."""
    def __init__(self, **kwargs):
        global DEFAULT_CSS_CLASS
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
                DEFAULT_CSS_CLASS,
                'The class of <a> element to insert. - '
                + f'Default: {DEFAULT_CSS_CLASS}"'
            ]
        }
        super(CiteURLExtension, self).__init__(**kwargs)
        self.css_class = self.config['css_class'][0]
    
    def extendMarkdown(self, md):
        custom_schemas = self.config['custom_schemas'][0]
        if custom_schemas:
            schemas = Schema_Set(
                *custom_schemas,
                defaults=self.config['use_defaults'][0]
            )
        else:
            schemas = Schema_Set()
        pattern = 1
        for schema in schemas.schemas:
            md.inlinePatterns.register(
                CitationInlineProcessor(schema, self.css_class, md),
                'citeurl-pattern-' + str(pattern),
                pattern + 1037,
            )
            pattern += 1

def makeExtension(**kwargs):
    return CiteURLExtension(**kwargs)
