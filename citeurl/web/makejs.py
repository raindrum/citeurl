#!/usr/bin/python

# python standard imports
from argparse import ArgumentParser
from json import dumps
from pathlib import Path

# internal imports
from .. import Citator

COPYRIGHT_MESSAGE = """
// This script was made with CiteURL, an extensible framework to turn
// legal references into URLs.
//
// The "templates" variable directly below holds the data necessary to 
// turn each kind of citation into a URL. Some or all of the templates may
// have been made by a third party and are not part of CiteURL itself.
//
// CiteURL is copyright of Simon Raindrum Sherred under the MIT License.
// See https://raindrum.github.io/citeurl for more info.
"""

_dir = Path(__file__).parent.absolute()
BASE_JS_PATH =  _dir / 'citeurl.js'
CSS_PATH = _dir / 'style.css'
LOGO_PATH = _dir / 'logo.svg'

PAGE = """
<head>
  <meta content="width=device-width, initial-scale=1" name="viewport"/>
</head>
<script>{JS}</script>
<style>{CSS}</style>
<body><div class="content">
  {LOGO}
  <h1>Law Search</h1>
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
<footer>
  Powered by <a href="https://raindrum.github.io/citeurl">CiteURL</a>,
  and subject to absolutely no warranty.
</footer>
</body>
"""

def makejs(
    citator: Citator,
    entire_page: bool = False,
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
    Returns:
        a string containing JavaScript or HTML
    """
    # translate each template to json
    json_templates = []
    for template in citator.templates:
        # skip templates without URL templates
        if 'URL' not in template.__dict__:
            continue
        
        json = {}
        
        # some parts of a template can be copied over easily
        for key in ['name', 'defaults', 'URL']:
            json[key] = template.__dict__[key]
        regexes_source = (
            (template.broadRegexes + template.regexes) if template.broadRegexes
            else template.regexes
        )
        json['regexes'] = list(map(
            lambda x: x.replace('?P<', '?<'),
            regexes_source
        ))
        # only add the relevant information from each operation
        if template.operations:
            json['operations'] = []
        for operation in template.operations:
            json_op = {}
            for key, value in operation.items():
                if key == 'output' and value == 'token':
                    continue
                json_op[key] = value
            json['operations'].append(json_op)

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
    
    # optionally embed the javascript into an HTML page
    if entire_page:
        output = PAGE.format(
            JS=javascript,
            CSS=CSS_PATH.read_text(),
            LOGO=LOGO_PATH.read_text(),
        )
    else:
        output = javascript
    
    return output
