"strings and functions that are used by both server.py and makejs.py"

# python standard imports
from urllib.parse import quote_plus, urlsplit
from importlib.metadata import version
from re import sub
from pathlib import Path

########################################################################
# External Files
########################################################################

_dir = Path(__file__).parent.absolute()
CSS_PATH = _dir / 'style.css'
LOGO_PATH = _dir / 'logo.svg'

########################################################################
# HTML Templates
########################################################################

PAGE_TEMPLATE = """
<head>
  <meta content="width=device-width, initial-scale=1" name="viewport"/>
  {head}
</head>
<body>
<div class="content">
  {content}
</div>
<footer>{relation}
<a href="https://raindrum.github.io/citeurl">CiteURL</a>
{version} and subject to absolutely no warranty.</footer>
</body>"""

SOURCES_INTRO = """
<p>Below, you'll find the sources of law that this instance of CiteURL
supports. If you want to know what citation formats each one will
recognize, you can click "view regex" to see a diagram.</p>"""

SOURCES_TABLE = """
<div class="table-wrapper">
  <table>
    <thead>
      <th>Source of Law</th>
      <th>Website</th>
      <th>Citation Format</th>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
</div>"""

SOURCES_TABLE_ROW = """
      <tr>
        <td>{name}</td>
        <td><a href="{domain_URL}">{domain_name}</a></td>
        <td><a href="https://regexper.com#{escaped_regex}">view regex</a></td>
      </tr>"""

VERSION = f"v{version('citeurl')}"

########################################################################
# Functions
########################################################################

def format_page(
    text: str,
    js: str='',
    inline_css: bool=False,
    inline_logo: bool=False,
    relation_to_citeurl: str='Powered by',
    **kwargs
):
    """
    Returns PAGE_TEMPLATE with the given text inserted into the body.
    All placeholders (in curly braces) in the given text must be filled
    via keyword arguments. In addition to those mandatory keywords, you
    may provide any of the following:
    
    Arguments:
        js: JavaScript to be inserted directly into the page head
        inline_css: whether the CSS styling should be embedded in the
            instead of an outside link. Default: False
        inline_logo: whether the logo SVG should be embedded in the page
            instead of an outside link. Default: False
        relation_to_citeurl: a string that will be inserted into the
            page footer, just before the link to CiteURL and the
            subsequent disclaimer. Default: 'Powered by'.
        title: the HTML page title
    """
    for k, v in kwargs.items():
        text = text.replace('{' + k + '}', v)
    #text = text.format(**kwargs)
    if inline_logo:
        logo = LOGO_PATH.read_text()
    else:
        logo = '<img src="logo.svg" alt="CiteURL logo">'
    if inline_css:
        css_section = f'<style>{CSS_PATH.read_text()}</style>'
    else:
        css_section = '<link rel="stylesheet" href="style.css">'
    if not inline_logo: # add favicon to header
        favicon = '<link rel="icon" href="logo.svg">\n'
    else:
        favicon = ''
    js_section = f"<script>{js}</script>" if js else ''
    return PAGE_TEMPLATE.format(
        head=favicon + css_section + '\n' + js_section,
        content=logo + '\n' + text,
        version=VERSION,
        relation=kwargs.get('relation') or 'Powered by',
    )

def sources_table(citator):
    """
    Return the content for an HTML table listing every template that the 
    citator can link to.
    """ 
    rows = []
    for template in citator.templates:
        # skip templates that can't make URLs
        if not template.__dict__.get('URL'):
            continue
        
        URL = urlsplit(''.join(template.URL))
        domain_URL = f'{URL.scheme}://{URL.netloc}'
        domain_name = URL.hostname
        regex = unify_regex(template, simplify_for_regexper=True)

        rows.append(SOURCES_TABLE_ROW.format(
            name=template.name,
            domain_URL=domain_URL,
            domain_name=domain_name,
            escaped_regex=quote_plus(regex).replace('+', '%20')
        ))
    
    return SOURCES_TABLE.format(rows=''.join(rows))

def unify_regex(template, simplify_for_regexper: bool=False):
    """
    Combine the given template's regexes (if there are multiple) into
    one long regex that matches any one of them. Wherever possible,
    insert any mandatory lookups from the template's operations, so that
    the resulting regex will be restricted to each option from the
    lookups.
    
    Arguments:
        template: the template object to get a regex for
        simplify_for_regexper: whether to strip lookbehinds, lookaheads,
            and the names of capture groups so that the resulting URL is
            compatible with regexper.com. Note that if this is false,
            duplicated capture groups will be renamed to avoid conflict.
    """
    regexes = template.regexes.copy()
    # append numbers to repeated capture group names to prevent conflict
    for i, regex in enumerate(regexes[1:]):
        regexes[i+1] = sub(r'\?P<(.+?)>', '?P<\1' + f'{i}>', regex)
    regex = '|'.join(regexes)
    
    # whenever a template operation uses a token for a mandatory lookup,
    # and that token hasn't been modified by another operation yet,
    # insert the lookup's regexes where the token goes, to make the
    # final regex more specific.
    for i, operation in enumerate(template.operations):
        # only lookup operations are used here
        if 'lookup' not in operation:
            continue
        
        # don't bother if the lookup's input token is modified before
        # the lookup
        already_modified = False
        for prior_op in template.operations[:i-1]:
            if prior_op == operation:
                continue
            prior_op_output = prior_op.get('output') or prior_op['token']
            if prior_op_output == operation['token']:
                already_modified = True
                break
        if already_modified:
            continue
        
        # modify the regex
        pattern = '\(\?P<' + operation['token'] + '\d*>.+?(?<!\\\)\)'
        repl = '(' + '|'.join(operation['lookup'].keys()) + ')'
        regex = sub(pattern, 'PlAcEhOlDeR122360', regex)
        regex = regex.replace('PlAcEhOlDeR122360', repl)
    
    if simplify_for_regexper:
        # remove lookaheads and lookbehinds
        regex = sub(r'\(\?(<!|<=|!|=).+?\)', '', regex)
        
        # escape slashes
        regex = regex.replace('/', r'\/')

        # remove capture group names
        regex = sub(r'\?P<.+?>', '', regex)
    
    return regex
