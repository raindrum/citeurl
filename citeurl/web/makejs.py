# python standard imports
from argparse import ArgumentParser
from json import dumps
from pathlib import Path
from re import sub

# internal imports
from .. import Citator
from .resources import unify_regex, format_page, sources_table
from .resources import SOURCES_INTRO, VERSION

COPYRIGHT_MESSAGE = f"""
// This script was made with CiteURL {VERSION}, an extensible framework
// to turn legal references into URLs.
//
// The "templates" variable below holds the data necessary to 
// turn each kind of citation into a URL. Some or all of the templates may
// have been made by a third party and are not part of CiteURL itself.
//
// CiteURL is copyright of Simon Raindrum Sherred under the MIT License.
// See https://raindrum.github.io/citeurl for more info.
"""

_dir = Path(__file__).parent.absolute()
BASE_JS_PATH =  _dir / 'citeurl.js'

PAGE = """
<h1>CiteURL</h1><title>CiteURL</title>
<div class="narrow">
<p>Type a legal citation into the box below, and I'll try to send you
directly to the case or law that it references:</p>
<form onsubmit="handleSearch(event)">
<div class="searchbar">
  <input type="search" name="q" id="q" placeholder="Enter citation..."
  label="Citation search bar"><button type="submit">Go</button>
</div>
<p>
  <label for="q" id="explainer" class="explainer"> </label>
</p>
</form>
</div>
{sources_table}
"""

# these functions either uncomment or remove a commented-out code block
# that looks like this:
# /*blockname
# <whatever code goes here>
# */
def _uncomment(blockname: str, source_js: str):
    return sub(fr' */\*{blockname}\n([^©]+?) *\*/\n', r'\1', source_js)
def _remove(blockname: str, source_js: str):
    return sub(fr' */\*{blockname}\n[^©]+? *\*/\n', '', source_js)

def makejs(
    citator: Citator,
    entire_page: bool = False,
    include_sources_table: bool = False,
) -> str:
    """
    Generate a JavaScript implementation of a given citator's lookup
    features, so that it can be embedded in a website. Optionally
    package it as a standalone web page for end users.
    
    Arguments:
        citator: a CiteURL citator object, with any number of templates
            loaded.
        entire_page: whether to output an HTML page with a searchbar
            and styling
        include_sources_table: whether to provide a table listing each
            template that the page supports. Implies entire_page = True.
    Returns:
        a string containing JavaScript or HTML
    """
    if include_sources_table:
        entire_page = True
    
    # translate each template to json
    json_templates = []
    for template in citator.templates.values():
        if not template.URL_builder:
            continue
        
        json = {}
        
        # some parts of a template can be copied over easily
        json['name'] = template.name
        
        defaults = template.meta
        for name, token in template.tokens.items():
            if token.default:
                defaults[name] = token.default
        if defaults:
            json['defaults'] = defaults
        
        json['regexes'] = [
            r.pattern.replace('?P<', '?<') for r in template.broad_regexes
        ]

        # only add the relevant information from each operation
        
        json['operations'] = []
        
        for name, token in template.tokens.items():
            for edit in token.edits:
                edit_dict = {
                    'token': name,
                    edit.action: edit.data
                }
                if 'lookup' in edit_dict and not edit.mandatory:
                    edit_dict['optionalLookup'] = edit_dict.pop('lookup')
                json['operations'].append(edit_dict)
        
        for edit in template.URL_builder.edits:
            edit_dict = {
                'token': edit.token,
                edit.action: edit.data
            }
            if edit.output:
                edit_dict['output'] = edit.output
            if 'lookup' in edit_dict and not edit.mandatory:
                edit_dict['optionalLookup'] = edit_dict.pop('lookup')
            json['operations'].append(edit_dict)
        
        json['URL'] = [p for p in template.URL_builder.parts]

        json_templates.append(json)
    
    # write json to str
    json_str = dumps(
        json_templates,
        indent=4,
        sort_keys=False,
        ensure_ascii=False,
    )
    
    # generate javascript
    javascript = (
        COPYRIGHT_MESSAGE
        + '\nconst templates = ' 
        + json_str + ';\n\n'
        + BASE_JS_PATH.read_text()
    )
    
    # uncomment or remove browser-only features in the JS
    if entire_page:
        javascript = _uncomment('PAGEBEHAVIOR', javascript)
        javascript = _uncomment('LOGS', javascript)
    else:
        javascript = _remove('LOGS', javascript)
        javascript = _remove('PAGEBEHAVIOR', javascript)
    
    if include_sources_table:
        table = (f'{SOURCES_INTRO}\n{sources_table(citator)}')
    else:
        table = ''
    
    # optionally embed the javascript into an HTML page
    if entire_page:
        output = format_page(
            PAGE,
            sources_table=table,
            inline_logo=True,
            inline_css=True,
            js=javascript,
            relation='Static page generated with',
        )
    else:
        output = javascript
    
    return output
