# python standard imports
import socket
from urllib.parse import unquote, quote_plus, urlsplit
from re import sub

# internal imports
from .resources import format_page, sources_table, SOURCES_INTRO

# third-party imports
from flask import Flask, redirect, make_response, send_file, request
from gevent import monkey
from gevent.pywsgi import WSGIServer

_APP = Flask(__name__, static_url_path='')

########################################################################
# Messages
########################################################################

PAGE_TEMPLATE = """
<head>
  <meta content="width=device-width, initial-scale=1" name="viewport"/>
  <link rel="stylesheet" href="style.css">
</head>
<body>
<div class="content">
  <img src="logo.svg" alt="CiteURL logo" class="logo">
  {content}
</div>
<footer>Powered by
<a href="https://raindrum.github.io/citeurl">CiteURL</a>,
and subject to absolutely no warranty.</footer>
</body>
"""

INDEX = """
<h1>{name}</h1>
<p>Type a legal citation into the box below, and I'll try to send you
directly to the case or law that it references:</p>
<form class="searchbar" method="get">
  <input type="search" name="s" placeholder="Enter citation..."
  label="citation search bar"><button type="submit">Go</button>
</form>
<p>Check <a href="sources">here</a> for the supported sources of law.</p>
"""

SOURCES_PAGE = """
<h1>Sources of Law</h1>
{intro}
{table}
"""

SOURCE_TABLE_ROW = """
      <tr>
        <td>{name}</td>
        <td><a href="{domain_URL}">{domain_name}</a></td>
        <td><a href="https://regexper.com#{escaped_regex}">view regex</a></td>
      </tr>
"""

ERROR_501 = """
<h1>Missing URL</h1>
<p>Sorry, I can tell that's a {template} citation but I don't have a
link for it.</p>
<a href="/"><button>Go Back</button></a>
"""

ERROR_400 = """
<h1>Unrecognized Citation</h1>
<p>Sorry, "{query}" isn't a citation I recognize.</p>
<a href="/"><button>Go Back</button></a>
"""

########################################################################
# Define APP
########################################################################

@_APP.route('/<query>')
def _handle_query(query: str):
    """
    Try to interpret query as a citation and return a 301 redirect if
    it returns a URL. Otherwise return 501 error if it matches a
    citation without a URL, or 400 if no match.
    """
    query = unquote(query)
    cite = _APP.citator.lookup(query)
    if cite and cite.URL:
        return redirect(cite.URL, code=301)
    elif cite:
        return make_response(
            format_page(ERROR_501, template=cite.template.name), 501
        )
    else:
        return make_response(format_page(ERROR_400, query=query), 400)

@_APP.route('/')
def _index():
    """
    Handle query if one is provided with the 's' parameter, otherwise
    show the main page.
    """
    query = request.args.get('s')
    if query:
        return _handle_query(query)
    else:
        return _APP.index_page

@_APP.route('/sources')
def _sources():
    "return a page listing the citator's templates in a table"
    return _APP.sources_page

@_APP.route('/logo.svg')
def _logo():
    return send_file('logo.svg')

@_APP.route('/style.css')
def _css():
    return send_file('style.css')

########################################################################
# Utility Functions
########################################################################

def _get_local_ip():
    "get local IP address. source: https://stackoverflow.com/a/28950776"
    # source: https://stackoverflow.com/a/28950776
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

########################################################################
# Public Functions
########################################################################

def App(citator, name='CiteURL'):
    """
    Return a flask application to implement the given citator. If called
    repeatedly, it will probably overwrite earlier instances.
    """
    _APP.index_page = format_page(INDEX, name=name)
    _APP.citator = citator
    _APP.sources_page = format_page(
        SOURCES_PAGE,
        intro=SOURCES_INTRO,
        table=sources_table(citator),
    )
    return _APP

def serve(app, localhost=True, port=53037):
    """
    Use gevent to host the app as a WSGI server at the given port. If
    not localhost, use _get_local_ip() to find the IP address to use.
    """ 
    monkey.patch_all()
    
    if localhost:
        IP = 'localhost'
    else:
        IP = _get_local_ip()
    
    base_URL = f'http://{IP}:{port}'

    server = WSGIServer((IP, port), app)
    print(f'Now hosting citation lookup server at {base_URL}...')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopped hosting citation lookup server.")
