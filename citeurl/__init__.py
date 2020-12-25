# python standard imports
import re
from pathlib import Path

# external imports
from yaml import safe_load

###################################################
# define classes
###################################################

class Schema_Set:
    """A group of Schemas and the tools to collectively apply them.
    
    Loads the included citation-schemas.yml by default, unless
    initialized with defaults=False. Also loads whatever filepaths
    are included as arguments in its constructor.
    
    See https://github.com/raindrum/citeurl#schema-format for more info."""
    
    def __init__(self, *args, defaults: bool=True):
        self.schemas = []
        if defaults:
            parent_dir = Path(__file__).parent.absolute()
            yaml_path = parent_dir / 'default-schemas.yml'
            self.load_schemas(str(yaml_path))
        for path in args:
            self.load_schemas(path)
    
    def load_schemas(self, path):
        """Import schemas from the specified YAML file."""
        yaml_text = Path(path).read_text()
        yaml_nodes = safe_load(yaml_text)
        for node in yaml_nodes:
            self.schemas.append(Schema(node))
    
    def insert_links(self, text, css_class: str='citation'):
        """
        Returns a version of input text where all citations are hyperlinks.
        
        Uses case-sensitive regex matching based on each schema's default
        regex. Replaces each match with an <a> element with an href to the
        proper URL, and the class "citation".
        
        :param text: a string to scan for citations
        :param css_class: the class that each generated <a> element
            will have. Defaults to "citation".
        :return: a string with links inserted"""
        for schema in self.schemas:
            text = schema.insert_links(text, css_class)
        return text

    def lookup_query(self, query):
        """
        Look up the the appropriate URL for a single citation query.
        
        Uses case-insensitive regex matching, and uses each schema's
        more permissive ("broad") regex, if one is defined.
        
        :param query: a short string to be read as a citation
        :return: a string containing the appropriate URL"""
        for schema in self.schemas:
            url = schema.url_from_query(query)
            if url:
                return url
        raise KeyError("'%s' doesn't match a known regex." % query)


class Schema:
    """
    The information needed to turn a citation into a URL.
    
    Each schema represents a body of law. At minimum it needs a
    regex to recognize, and a set of URLParts to construct a URL
    out of capture groups from the regex. A schema may also have
    default values, mutations, and substitutions, which will be
    applied, in that order, to the specified capture groups before
    constructing the URL.
    
    For most purposes, it is more convenient to use the Schemas class
    rather than use this one directly."""
    
    def __init__(self, ydict: dict):
        self.__dict__ = ydict
        self.regex = re.compile(''.join(self.regexParts), flags=re.I)
        if not hasattr(self, 'defaults'):
            self.defaults = {}
        if hasattr(self, 'broadRegexParts'):
            self.broadRegex = re.compile(
                ''.join(self.broadRegexParts), flags=re.I
            )
        if hasattr(self, 'mutations'):
            mutation_objs = []
            for mut in self.mutations:
                mutation_objs.append(_Mutation(mut))
            self.mutations = mutation_objs
        else:
            self.mutations = []
        if hasattr(self, 'substitutions'):
            sub_objs = []
            for sub in self.substitutions:
                sub_objs.append(_Substitution(sub))
            self.substitutions = sub_objs
        else:
            self.substitutions = []

    def url_from_query(self, query):
        """Apply schema to the given query to generate a URL.
        
        Returns the URL, or None if the query does not match
        the schema.""" 
        if hasattr(self, "broadRegexParts"):
            regex_source = self.broadRegexParts
        else:
            regex_source = self.regexParts
        regex_str = "".join(regex_source)
        match = re.search(re.compile(regex_str, flags=re.I), query)
        if match:
            try:
                return self._url_from_match(match)
            except KeyError: # if substitution failed
                return None
        else:
            return None
    
    def insert_links(self, text: str, css_class: str):
        """Add <a> elements wherever the schema recognizes a citation.

        Tries to avoid modifying citations that are already inside
        <a> elements, but may not always be successful. If multiple
        schemas have overlapping regexes, it may be a problem.
        
        :param text: a string to insert links into
        :param css_class: the CSS class that each link will have
        :return: a string with links inserted"""
        regex_str = r'(?<!class="%s"\>)%s(?!\</a\>)' % (
            css_class,
            "".join(self.regexParts),
        )
        self.css_class = css_class # this is an ugly workaround
        regex = re.compile(regex_str)
        return re.sub(regex, self._get_link_element, text)

    def _url_from_match(self, match):
        keys = match.groupdict()
        for default in self.defaults:
            if default not in keys or keys[default] is None:
                keys[default] = self.defaults[default]
        for mut in self.mutations:
            for key in keys:
                if key != mut.key or keys[key] is None:
                    continue
                keys[mut.key] = mut._mutate(keys[key])
        for sub in self.substitutions:
            keys = sub._substitute(keys)
        url = """"""
        for part in self.URLParts:
            for key in keys:
                if not keys[key]:
                    continue
                part = part.replace('{%s}' % key, keys[key])
            missing_value = re.search('\{.+\}', part)
            if not missing_value:
                url += part
        return url
    
    def _get_link_element(self, match, css_class: str=''):
        if not css_class:
            css_class = self.css_class
        text = '<a href="%s" class="%s">%s</a>' % (
            self._url_from_match(match),
            css_class,
            match.group(0),
        )
        return text


class _Mutation:
    """
    Text filters to apply to an individual regex capture group.

    A mutation can be used to process the text from a capture group.
    Mutations are applied before substutions, so they can normalize
    input for substitutions as well as for URL construction."""

    def __init__(self, ydict: dict):
        self.__dict__ = ydict

    def _mutate(self, key: str):
        if hasattr(self, 'omit'):
            key = re.sub(re.compile(self.omit), '', key)
        if hasattr(self, 'splitter') and hasattr(self, 'joiner'):
            parts = re.split(re.compile(self.splitter), key)
            parts = list(filter(None, parts))
            key = self.joiner.join(parts)
        if hasattr(self, 'case'):
            if self.case == 'upper':
                key = key.upper()
            elif self.case == 'lower':
                key = key.lower()
        return key


class _Substitution:
    """
    Text filters to arbitrarily set a key's value based on an index.
    
    All substitutions look up the value of an inputKey in the included
    dictionary called "index". If an outputKey is specified, it will be
    set to the new value. Otherwise, the inputKey will be modified in
    place.
    
    If the inputKey is out of index, an error will be raised unless
    allowUnmatched is set to True.
    """
    def __init__(self, ydict: dict):
        self.__dict__ = ydict

    def _substitute(self, keys: dict):
        key = keys[self.inputKey]
        if not key:
            return
        key = self.index.get(key)
        if key:
            if hasattr(self, 'outputKey'):
                keys[self.outputKey] = key
            else:
                keys[self.inputKey] = key
        elif (
            'allowUnmatched' not in self.__dict__ or self.allowUnmatched is not True
        ):
            raise KeyError(
                "%s '%s' is out of index" % (self.inputKey, keys[self.inputKey])
            )
        return keys
