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
    
    def list_citations(self,
        text: str,
        id_forms: bool=True,
        id_break_regex: str=None,
        id_break_indices: list=[]):
        """
        Scan text and returns ordered list of all citations in it.
        
        If there's a predictable place that "id" chains should break
        where they don't already, you can use the id_break_regex
        argument to specify a string, parsed as regex, which will break
        any chain of "id" citations wherever it appears.
        
        You can also specify a list of index positions in the text where
        "id." chains should break.
        
        Or, you can use id_forms=False to disable "id"-type citations
        altogether if they are unreliable."""
        # First, get full citations:
        citations = []
        for schema in self.schemas:
            citations += schema.get_citations(text)
        shortform_cites = []
        # Then, add shortforms
        for citation in citations:
            shortform_cites += citation._get_shortform_citations(text)
        citations += shortform_cites
        citations = _sort_and_remove_overlaps(citations)
        if not id_forms: # no need to proceed
            return citations
        # determine where to break chains of id. citations
        for citation in citations: # break at full or short citations
            id_break_indices.append(citation.span[0])
        if id_break_regex: #also break at specified regexes
            matches = re.compile(id_break_regex).finditer(text)
            for match in matches:
                id_break_indices.append(match.span()[0])
        id_break_indices = sorted(set(id_break_indices))
        # loop through all citations to find their id citations
        id_citations = []
        for citation in citations:
            # find the next id break point
            i = -1
            for index in id_break_indices:
                i += 1
                if index > citation.span[1]:
                    end_point = index
                    break
            else:
                end_point = None
            id_break_indices = id_break_indices[i:]
            # get each citation's id citations until the break point
            id_citations += citation._get_id_citations(
                text, end_point=end_point
            )
        return _sort_and_remove_overlaps(citations + id_citations)
    
    def lookup(self, query, broad=True):
        """
        Check a single query against all schemas in order.
        
        Returns the first citation from the first schema matched, or
        None if no schemas are matched.
        
        Uses broadRegex and case-insensitive unless broad=False."""
        for schema in self.schemas:
            citation = next(schema.get_citations(query, broad=broad), None)
            if citation:
                return citation
        return None
    
    def insert_links(
        self,
        text,
        css_class: str='citation',
        link_rel: str=None,
        id_forms: bool=True,
        id_break_regex: str=None,
        id_break_indices: list=[]):
        """
        Process text and insert a link for each citation found.
        
        css_class and link_rel allow you to specify attributes
        of the inserted links.
        
        If there's a predictable place that "id" chains should break
        where they don't already, you can use the id_break_regex
        argument to specify a string, parsed as regex, which will break
        any chain of "id" citations wherever it appears.
        
        You can also specify a list of index positions in the text where
        "id." chains should break.
        
        Or, you can use id_forms=False to disable "id"-type citations
        altogether if they are unreliable."""
        citations = self.list_citations(
            text,
            id_forms=id_forms,
            id_break_regex=id_break_regex,
            id_break_indices=id_break_indices
        )
        offset = 0
        for c in citations:
            link = c.get_link(css_class=css_class, link_rel=link_rel)
            span = (
                c.span[0] + offset,
                c.span[1] + offset
            )
            text = ''.join([text[:span[0]], link, text[span[1]:]])
            offset += len(link) - len(c.text)
        return text
        
    def __repr__(self):
        return str(self.schemas)


class Schema:
    def __init__(self,
        name: str,
        regex: str or list,
        URL: str or list=None,
        broadRegex: str or list=None,
        idForms: list=[],
        shortForms: list=[],
        defaults: dict={},
        mutations: list=[],
        substitutions: list=[],
        parent_citation=None
    ):
        """
        Tool to recognize and process citations to a body of law.
        
        For most purposes, it is usually easier to use a
        Citator and custom YAML files, rather than use the
        Schema class directly."""
        # Mandatory values
        self.name = name
        self.regex = _join_if_list(regex)
        if URL:
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
        
    def __repr__(self):
        return self.name
    
    def lookup(self, text, broad=True, span: tuple=(0,)):
        """Returns the first citation it finds, or None"""
        try:
            return next(self.get_citations(text, broad=broad, span=span))
        except:
            return None
    
    def get_citations(self, text, broad=False, span: tuple=(0,)):
        """Generator to return all citations the schema finds in text"""
        matches = self._compiled_re(broad).finditer(text, *span)
        for match in matches:
            try:
                citation = Citation(match, self)
            # skip citations where substitution failed:
            except KeyError:
                citation = None
            if citation:
                yield citation
        return None
    
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
            output_val = None
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
    def __init__(
        self,
        match: re.Match,
        schema: Schema
    ):
        self.span = match.span()
        self.tokens = match.groupdict()
        self.schema = schema
        self.text = match.group(0)
        # idForm and shortForm citations get values from parent citation
        # except where their regexes include space for those values
        if schema.parent_citation:
            for key, val in schema.parent_citation.tokens.items():
                if key not in self.tokens:
                    self.tokens[key] = val
        
        if not hasattr(schema, 'URL'):
            self.URL = None
            return
        # Process matched tokens (i.e. named regex capture groups)
        url_tokens = dict(self.tokens)
        for key, val in schema.defaults.items():
            if key not in url_tokens or url_tokens[key] is None:
                url_tokens[key] = val
        for mut in schema.mutations:
            input_value = url_tokens.get(mut.token)
            if input_value:
                url_tokens[mut.token] = mut._mutate(input_value)
        for sub in schema.substitutions:
            url_tokens = sub._substitute(url_tokens)
        URL = """"""
        for part in schema.URL:
            for key, value in url_tokens.items():
                if not value: continue
                part = part.replace('{%s}' % key, value)
            missing_value = re.search('\{.+\}', part)
            if not missing_value:
                URL += part
        self.URL = URL
    
    def __repr__(self):
        return self.text
    
    def get_link(self, css_class='citation', link_rel=None):
        if not self.URL: # don't process linkless citations
            return self.text
        return (
            '<a href="%s" class="%s"%s>%s</a>'
            % (
                self.URL,
                css_class,
                ' rel="%s"' % link_rel if link_rel else '',
                self.text
            )
        )
    
    def original_citation(self):
        citation = self
        while citation.schema.parent_citation:
            citation = citation.schema.parent_citation
        return citation
    
    def _child_schemas(self, id_not_shortform: bool):
        schemas = []
        regex_templates = (
            self.schema.idForms if id_not_shortform
            else self.schema.shortForms
        )
        for template in regex_templates:
            # Insert context values into template to make new regex
            regex = template
            for key, value in self.tokens.items():
                if not value: continue
                regex = regex.replace('{%s}' % key, value)
            schemas.append(Schema(
                name=self.schema.name,
                regex=regex,
                idForms=self.schema.idForms,
                URL=self.schema.URL,
                mutations=self.schema.mutations,
                substitutions=self.schema.substitutions,
                parent_citation=self
            ))
        return schemas
    
    def _get_shortform_citations(self, text: str):
        schemas = self._child_schemas(False)
        for schema in schemas:
            for citation in schema.get_citations(text, span=(self.span[1], )):
                yield citation
            
    def _get_id_citations(self, text: str, end_point: int=None):
        schemas = self._child_schemas(True)
        id_citations = []
        scan_cites = [self]
        while len(scan_cites) > 0:
            citation = scan_cites.pop(0)
            if end_point:
                span = (citation.span[1], end_point)
            else:
                span = (citation.span[1],)
            potential_ids = []
            for schema in citation._child_schemas(True):
                match = schema.lookup(text, broad=False, span=span)
                if match:
                    potential_ids.append(match)
            if potential_ids:
                id_citation = sorted(potential_ids, key=_sort_key)[0]
                id_citations.append(id_citation)
                scan_cites.append(id_citation)
        return id_citations
                
        
def _join_if_list(source: list or str):
    return source if type(source) is str else ''.join(source)

def _sort_and_remove_overlaps(citations: list):
    """Sorts citations by order of appearance; deletes overlaps."""
    sorted_citations = sorted(citations, key=_sort_key)
    index = 1
    while index < len(sorted_citations):
        first = sorted_citations[index - 1]
        second = sorted_citations[index]
        if first.span[1] >= second.span[0]:
            # delete whichever citation starts later in the text, or in
            # case of a tie, the one from the schema processed first
            if first.span[0] < second.span[0]:
                sorted_citations.pop(index)
            elif first.span[0] < second.span[0]:
                sorted_citations.pop(index - 1)
            else:
                if citations.index(first) > citations.index(second):
                    sorted_citations.pop(index)
                else:
                    sorted_citations.pop(index - 1)
        else: # no overlap, continue to next comparison
            index += 1
    return sorted_citations

def _sort_key(citation):
    return citation.span[0]
