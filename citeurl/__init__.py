# python standard imports
import re
from pathlib import Path

# external imports
from yaml import safe_load

default_yaml_path = (
    Path(__file__).parent.absolute() / 'default-schemas.yaml'
)

class Citator:
    """A list of citation schemas, and ways to match text against it."""
    def __init__(self, *yaml_paths, defaults: bool=True):
        """
        By default, makes citator using built-in schemas.
        
        To load one or more YAML files full of schemas, provide their
        filepaths as separate string arguments. To prevent loading the
        built-in schemas, set defaults to False."""
        self.schemas = []
        if defaults:
            self.load_yaml(default_yaml_path)
        for path in yaml_paths:
            self.load_yaml(path)
    
    def load_yaml(self, path: str):
        """Import schemas from the specified YAML file."""
        yaml_text = Path(path).read_text()
        yaml_nodes = safe_load(yaml_text)
        for node in yaml_nodes:
            self.schemas.append(Schema(**node))
    
    def list_citations(self, text: str, broad=False, span: tuple=(0,)):
        """Match text against all schemas and return results.
        
        Returns a list of all citatioh objects found, in order of 
        appearance. If two potential citations overlap, only the
        one that starts first will be included.
        
        Span is a tuple representing the start and end index (if any)
        that the citator should scan between."""
        # Get list of all longform citations
        citations = self._get_citations(text, broad=broad, span=span)
        
        # Filter list to remove overlapping ciations
        citations = self._sort_citations(citations)
        
        # Add shortform citations to list.
        for c in citations:
            if not c.schema.shortForms: continue
            citator = c._shortform_citator(c.schema.shortForms, False)
            citations += list(
                citator._get_citations(text, span=(c.match.span()[0],))
            )
        citations = self._sort_citations(citations)
        
        # Add "id" citations to list.
        for i, c in enumerate(citations):
            if not c.schema.idForms: continue
            citator = c._shortform_citator(c.schema.idForms, True)
            span = (c.match.span()[1],)
            if i + 1 < len(citations):
                span = (span[0], citations[i + 1].match.span()[0])
            citations += list(citator._get_citations(text, span=span))
        
        # Finally, sort and filter list once more.
        return self._sort_citations(citations)
        
    def _get_citations(self, text: str, broad=False, span: tuple=(0,)):
        """Find all top-level citations, schema by schema."""
        for s in self.schemas:
            for m in s.get_citations(text, broad=broad, span=span):
                yield m
        
    def _sort_citations(self, citations: list):
        """Sorts citations by order of appearance; deletes overlaps."""
        def sort_key(citation):
            return citation.match.span()[0]
        sorted_citations = sorted(citations, key=sort_key)
        # Delete the latter of any two overlapping citations.
        deletions = []
        for i, this_cite in enumerate(sorted_citations):
            if i == 0: continue
            last_cite_end = sorted_citations[i - 1].match.span()[1]
            this_cite_start = this_cite.match.span()[0]
            if last_cite_end > this_cite_start:
                deletions.append(this_cite)
        for d in deletions:
            sorted_citations.remove(d)
        
        return sorted_citations
        
    def lookup(self, query, broad=True):
        """
        Check a single query against all schemas in order.
        
        Uses broadRegex and case-insensitive matching by default.
        Returns the first citation from the first schema matched, or
        None if no schemas are matched."""
        try:
            return next(self._get_citations(query, broad=broad))
        except:
            return None
    
    def insert_links(self, text, css_class: str='citation'):
        """Process text and insert a link for each citation found."""
        citations = self.list_citations(text)
        spans = []
        offset = 0
        for c in citations:
            link = c.get_link(css_class=css_class)
            span = (
                c.match.span()[0] + offset,
                c.match.span()[1] + offset
            )
            text = ''.join([text[:span[0]], link, text[span[1]:]])
            offset += len(link) - len(c.match.group(0))
        return text
        
    def __repr__(self):
        return str(self.schemas)


class Schema:
    def __init__(self,
        name: str,
        regex: str or list,
        URL: str or list,
        broadRegex: str or list=None,
        idForms: list=[],
        shortForms: list=[],
        defaults: dict={},
        mutations: list=[],
        substitutions: list=[],
        parent_citation=None,
        fleeting: bool=False
    ):
        """
        Tool to recognize and process citations to a body of law.
        
        For most purposes, it is usually easier to use a
        Citator and custom YAML files, rather than use the
        Schema class directly."""
        # Mandatory values
        self.name = name
        self.regex = _join_if_list(regex)
        self.URL = URL if type(URL) is list else [URL]
        # Supplemental regexes
        self.broadRegex = _join_if_list(broadRegex) if broadRegex else None
        self.idForms = [_join_if_list(r) for r in idForms]
        self.shortForms = [_join_if_list(r) for r in shortForms]
        # String operators
        self.defaults = defaults
        try:
            self.mutations = [self._Mutation(**m) for m in mutations]
        except TypeError:
            self.mutations = mutations
        try:
            self.substitutions = [self._Substitution(**s) for s in substitutions]
        except TypeError:
            self.substitutions = substitutions
        
        # Extra data for shortform citations
        self.parent_citation = parent_citation
        self.fleeting = fleeting
        
    def __repr__(self):
        return self.name
    
    def lookup(self, text, broad=True):
        """Returns the first citation it finds, or None."""
        try:
            citation = next(self.get_citations(text, broad=broad))
        except:
            citation = None
        return citation
    
    def get_citations(self, text, broad=False, span: tuple=(0,)):
        matches = self._compiled_re(broad).finditer(text, *span)
        for match in matches:
            try:
                yield Citation(match, self)
            # skip citations where substitution failed:
            except KeyError:
                pass
    
    def _compiled_re(self, broad: bool):
        if broad:
            attr='_compiled_broadRegex'
            regex_source = self.broadRegex or self.regex
            kwargs={'flags':re.I}
        else:
            attr='_compiled_regex'
            regex_source = self.regex
            kwargs={}
        # only compile regex if it's not already present
        if not hasattr(self, attr):
            try:
                self.__dict__[attr] = re.compile(regex_source, **kwargs)
            except re.error as e:
                if not self.parent_citation:
                    raise SyntaxError(
                        "CiteURL schema for %s has an invalid %s: %s"
                        % (self.name, 'broadRegex' if broad else 'regex', e)
                    )
                else:
                    raise SyntaxError(
                        ("CiteURL schema for %s has an error in one of its"
                        + " shortForms or idForms: %s")
                        % (self.parent_citation.schema.name, e)
                    )
        return self.__dict__[attr]

    class _Mutation: 
        def __init__(self,
            token: str,
            case: str=None,
            omit: str=None,
            splitter: str=None,
            joiner: str=None
        ):
            """
            A set of text filters to modify a token in place.
        
            Mutations are applied before substitutions or URL
            generation, so they are useful for normalizing input."""
            self.token = token
            self.case = case
            self.omit = omit
            self.splitter = splitter
            self.joiner = joiner
            if splitter and not joiner:
                raise SyntaxError(
                    ("CiteURL schema mutation affecting token '%s' "
                    + "contains a splitter but no joiner.") % token
                )
    
        def _mutate(self, token: str):
            if self.omit:
                token = re.sub(re.compile(self.omit), '', token)
            if self.splitter and self.joiner:
                parts = re.split(re.compile(self.splitter), token)
                parts = list(filter(None, parts))
                token = self.joiner.join(parts)
            if self.case:
                if self.case == 'upper':
                    key = token.upper()
                elif self.case == 'lower':
                    token = token.lower()
            return token
    
    class _Substitution:
        def __init__(self,
            token: str,
            index: dict,
            outputToken: str=None,
            useRegex: bool=False,
            allowUnmatched: bool=False
        ):
            """
            Text filter to set a token's value via dictionary lookup.
            
            The token will be looked up in the index, and its value
            will be replaced by the value found. If the token is outside
            the index, it will cause the whole citation match to fail
            unless allowUnmatched is True.
            
            If an outputToken is specified, the lookup will set the
            outputToken's value instead of modifying the input token.
            
            If useRegex is True, the token will be matched to an index
            key using citation matching instead of a dictionary lookup."""
            self.token = token
            self.outputToken = outputToken or token
            self.index = index
            self.useRegex = useRegex
            self.allowUnmatched = allowUnmatched
        
        def _substitute(self, tokens: dict):
            # skip substitution if input token is unset
            input_val = tokens[self.token]
            if not input_val:
                return tokens
            # perform dict or regex lookup
            if not self.useRegex:
                output_val = self.index.get(input_val)
            else:
                for regex, value in self.index.items():
                    if re.fullmatch(regex, input_val, flags=re.I):
                        output_val = value
                        break    
            # modify token dict, throw error, or return unmodified
            if output_val:
                tokens[self.outputToken] = output_val
            elif not self.allowUnmatched:
                raise KeyError(
                    "%s '%s' is out of index" % (self.token, input_val)
                )
            return tokens

class Citation:
    def __init__(self, match: re.Match, schema: Schema):
        # Process matched tokens (i.e. named regex capture groups)
        tokens = match.groupdict()
        for key, val in schema.defaults.items():
            if key not in tokens or tokens[key] is None:
                tokens[key] = val
        for mut in schema.mutations:
            input_value = tokens.get(mut.token)
            if input_value:
                tokens[mut.token] = mut._mutate(input_value)
        for sub in schema.substitutions:
            tokens = sub._substitute(tokens)
        # Generate URL from tokens
        URL = """"""
        for part in schema.URL:
            for key, value in tokens.items():
                if not value: continue
                part = part.replace('{%s}' % key, value)
            missing_value = re.search('\{.+\}', part)
            if not missing_value:
                URL += part
        self.match = match
        self.schema = schema
        self.tokens = tokens
        self.URL = URL
    
    def __repr__(self):
        return self.match.group(0)
    
    def get_link(self, css_class='citation'):
        return (
            '<a href="%s" class="%s">%s</a>'
            % (self.URL, css_class, self.match.group(0))
        )
    
    def _shortform_citator(self, regex_templates, fleeting: bool):
        citator = Citator(defaults=False)
        if self.schema.parent_citation:
            captures = self.schema.parent_citation.match.groupdict()
        else:
            captures = self.match.groupdict()
        for template in regex_templates:
            template = _join_if_list(template)
            for key, value in captures.items():
                if not value: continue
                template = template.replace('{%s}' % key, value)
            citator.schemas.append(Schema(
                name=self.match.group(0),
                regex=template,
                idForms=self.schema.idForms if not fleeting else [],
                URL=self.schema.URL,
                defaults=captures,
                mutations=self.schema.mutations,
                substitutions=self.schema.substitutions,
                parent_citation=self,
                fleeting=fleeting
            ))
        return citator

def _join_if_list(source: list or str):
    return source if type(source) is str else ''.join(source)
