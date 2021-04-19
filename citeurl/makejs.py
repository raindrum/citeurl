#!/usr/bin/python

# python standard imports
from argparse import ArgumentParser
from json import dumps
from pathlib import Path

# internal imports
from . import Citator

BASE_JS_PATH =  Path(__file__).parent.absolute() / 'citeurl.js'

COPYRIGHT_MESSAGE = """
// This script was made with CiteURL, an extensible framework to turn
// legal references into URLs.
//
// The "schemas" variable directly below holds the data necessary to 
// turn each kind of citation into a URL. Some or all of the schemas may
// have been made by a third party and are not part of CiteURL itself.
//
// CiteURL is copyright of Simon Raindrum Sherred under the MIT License,
// and is available at https://github.com/raindrum/citeurl.
"""

HTML_FORM = (
    '<form class="citeurl-form" onsubmit="handleSearch(event)">\n  '
    + '<input type="search" placeholder="Enter citation..." name="q" id="q">'
    + '<input type="submit" value="Go"><br>\n  '
    + '<label for="q" id="explainer" class="citeurl-explainer"></label>\n'
    + '</form>'
)

def makejs(
    citator: Citator,
    embed_html: bool = False,
) -> str:
    """
    Generate a JavaScript implementation of a given citator's lookup
    features, so that it can be embedded in a website. Optionally
    include an HTML form so it can be directly embedded in a page
    
    Arguments:
        citator: a CiteURL citator object, with any number of schemas
            loaded.
        embed_html: whether to wrap the generated JavaScript in a
            <script> tag and follow it with an HTML form with a CiteURL
            search bar
    Returns:
        a string containing raw JavaScript or embeddable HTML
    """
    # translate each schema to json
    json_schemas = []
    for schema in citator.schemas:
        # skip schemas without URL templates
        if 'URL' not in schema.__dict__:
            continue
        
        json = {}
        
        # some parts of a schema can be copied over easily
        for key in ['name', 'defaults', 'URL']:
            json[key] = schema.__dict__[key]
        if schema.broadRegexes:
            if len(schema.broadRegexes) < len(schema.regexes):
                regexes_source = schema.broadRegexes + schema.regexes
            else:
                regexes_source = schema.broadRegexes
        else:
            regexes_source = schema.regexes
        json['regexes'] = list(map(
            lambda x: x.replace('?P<', '?<'),
            regexes_source
        ))
        # only add the relevant information from each operation
        if schema.operations:
            json['operations'] = []
        for operation in schema.operations:
            json_op = {}
            for key, value in operation.items():
                if key == 'output' and value == 'token':
                    continue
                json_op[key] = value
            json['operations'].append(json_op)

        json_schemas.append(json)
    
    # write json to str
    json_str = dumps(
        json_schemas,
        indent=4,
        sort_keys=False,
        ensure_ascii=False,
    )
    
    # generate javascript
    javascript = (
        COPYRIGHT_MESSAGE
        + '\nconst schemas = ' 
        + json_str + ';\n\n'
        + BASE_JS_PATH.read_text()
    )
    
    # optionally embed the javascript into an HTML page
    if embed_html:
        output = '<script>' + javascript + '</script>' + HTML_FORM
    else:
        output = javascript
    
    return output

def main():
    """
    Print a JavaScript implementation of CiteURL's lookup function,
    populated with the schemas from the specified YAML files, plus the
    built-in schemas by default.
    
    The JavaScript is meant to be embedded in a HTML page that contains
    a search bar with name="q", inside of a form with
    onsubmit="handleSearch(event)".
    """
    parser = ArgumentParser(description=main.__doc__)
    parser.add_argument(
        "yaml_files",
        nargs="*",
        help="files containing custom citation schemas to include. "
            + "See https://raindrum.github.io/citeurl/#schema-yamls/",
    )
    parser.add_argument(
        "-n", "--no-default-schemas",
        action="store_true",
        help="don't include CiteURL's default schemas",
    )
    parser.add_argument(
        "-e", "--embed-html",
        action="store_true",
        help="generate an embeddable HTML form instead of just JavaScript",
    )
    parser.add_argument(
        "-o", "--output",
        metavar="FILE",
        help="write output to a file instead of stdout",
    )
    args = parser.parse_args()
    
    citator = Citator(
        yaml_paths=args.yaml_files,
        defaults=False if args.no_default_schemas else True,
    )
    
    output = makejs(
        citator,
        embed_html=args.embed_html,
    )

    # save or print output
    if args.output:
        Path(args.output).write_text(output)
    else:
        print(output)
