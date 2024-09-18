# python standard imports
import socket
from urllib.parse import unquote, urlsplit
from re import sub
from html import escape

# internal imports
from .resources import format_page, sources_table
from .. import Citator, insert_links

# third-party imports
from flask import Flask, redirect, make_response, send_file, request
# from gevent import monkey (imported in serve())
# from gevent.pywsgi import WSGIServer (imported in serve())

_APP = Flask(__name__, static_url_path='')

########################################################################
# Messages
########################################################################

INDEX_PAGE = """
<div class="narrow">
<p>Paste a <a href="citations">legal citation</a> here, and you can
go somewhere else on the Web to read what it refereneces:</p>
<form class="searchbar" method="get">
  <input type="search" required name="s" placeholder="Enter citation..."
  maxlength=400 label="citation search bar"><button type="submit">Go</button>
</form>
</div>
"""

CITATIONS_PAGE = """
<h1>Citations</h1><title>Citations</title>
<div class="left">
<p>This web app is powered by
<a href="https://raindrum.github.io/citeurl">CiteURL</a>,
an open-source tool that recognizes legal citations and generates links to
publicly-available websites where you can read the cited documents.</p>
<p>"Legal citations" here means formal references to U.S. federal and state
laws and court opinions. This is not a search engine. If you enter something
ambiguous, like the <em>name</em> of a court case, nothing will happen.</p>
<p>Instead, citations generally need to follow
<a href="https://www.legalbluebook.com/bluebook/v21/quick-style-guide">bluebook style</a>,
so that CiteURL can recognize the relevant info (volume, page number, section,
etc) and turn it into a URL. But just because you know how to cite something
doesn't mean it'll work. Below, you will find the kinds of citation this app
can recognize, along with the websites it will send you to if it does:</p>
{table}
<p>By the way, CiteURL can also detect multiple citations in a longer text,
and insert hyperlinks for each one! Feel free to try that out
<a href="parser">here</a>.</p>
</div>
<p><a href="/"><button>Go Back</button></a></p>
"""

PARSER_PAGE = """
<h1>Text Parser</h1><title>Text Parser</title>
<p>Paste some text into the box below and click "Parse" to process
the text and find every <a href="citations">supported citation</a>
it contains.</p> 
<form action="parser#output" method="post">
<textarea required cols=80 rows=16 maxlength=400000 name="text"
placeholder="Paste text here.." label="Input text for
parser">{given_text}</textarea>
<p><a href="/"><button type="button">Go Back</button></a>
<button type="submit">Parse</button></p>
</form>
{output}
"""

INFO_PAGE = """
<h1>How it Works</h1>

"""

# Errors

ERROR_400 = """
<h1>Unknown Citation</h1><title>Unknown Citation</title>
<p>Sorry, "{query}" isn't a citation I recognize.</p>
<p><a href="/"><button>Go Back</button></a></p>
"""

ERROR_501 = """
<h1>Missing URL</h1><title>Missing URL</title>
<p>Sorry, I can tell that's a {template} citation but I don't have a
link for it.</p>
<p><a href="/"><button>Go Back</button></a></p>
"""

ERROR_413 = """
<h1>Query Too Long</h1><title>Query Too Long</title>
<p>Sorry, that's too many characters for the server to process.</p>
<a href="/"><button>Go Back</button></a>
"""

########################################################################
# Routes
########################################################################

@_APP.route('/<query>')
def _handle_query(query: str):
    """
    Try to interpret query as a citation and return a 301 redirect if
    it returns a URL. Otherwise return 501 error if it matches a
    citation without a URL, or 400 if no match.
    """
    if len(query) > _APP.max_chars:
        return format_page(ERROR_501)
    
    query = escape(unquote(query))
    cite = _APP.citator.cite(query)
    if cite:
        if cite.URL:
            return redirect(cite.URL, code=301)
        else:
            return make_response(
                format_page(ERROR_501, template=cite.template.name),
                501
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

# Pregenerated Pages

@_APP.route('/citations')
def _sources():
    """
    return a page explaining what a citation is, and 
    listing the citator's templates in a table
    """
    return _APP.citations_page

@_APP.route('/parser', methods= ['POST', 'GET'])
def _linker():
    "return a page that parses user-provided text"
    if request.method == 'GET':
        return format_page(PARSER_PAGE, given_text='', output='')
        
    given_text = escape(request.form['text'])
    if _APP.max_chars and len(given_text) > _APP.max_chars:
        return format_page(ERROR_501)
    citations = _APP.citator.list_cites(given_text)
    
    if not citations:
        return format_page(
            PARSER_PAGE,
            given_text=given_text,
            output="<p>Sorry, I couldn't find any citations in that.</p>"
        )
    
    output = insert_links(
        text = given_text,
        redundant_links = True,
        ignore_markup = False,
        citator = _APP.citator,
    )
    output = '<p>' + sub(r'\n+', '</p>\n<p>', output) + '</p>'
    
    return format_page(
        PARSER_PAGE,
        given_text=given_text,
        output=(
            '<h2 id="output">Output</h2>\n'
            + f'<form><div class="output-box">{output}</div></form>'
        ),
    )

# Static Files

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

def App(citator: Citator=Citator(), name: str='CiteURL'):
    """
    Return a flask application to implement the given citator. If called
    repeatedly, it will probably overwrite earlier instances.
    """
    # store variables in the app itself
    _APP.name = name
    _APP.index_page = format_page(INDEX_PAGE, name=name)
    _APP.citator = citator
    _APP.max_chars=400000 # limit query length
    _APP.citations_page = format_page(
        CITATIONS_PAGE,
        table=sources_table(citator),
    )
    return _APP

def serve(app, localhost=True, port=53037):
    """
    Use gevent to host the app as a WSGI server at the given port. If
    not localhost, use _get_local_ip() to find the IP address to use.
    """ 
    from gevent import monkey
    from gevent.pywsgi import WSGIServer
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
