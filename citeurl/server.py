# patch for server hosting
from gevent import monkey
monkey.patch_all()

# python standard imports
import socket
from urllib.parse import unquote

# third-party imports
from flask import Flask, redirect, abort, make_response
from gevent.pywsgi import WSGIServer

APP = Flask(__name__)
APP.base_url = APP.citator = None

############################################
# Messages
############################################

HEAD = """
<meta content="width=device-width, initial-scale=1" name="viewport" />
"""

INDEX = """
<h1>CiteURL</h1>
<p>This web app lets you look up legal citations with
<a href="https://raindrum.github.io/citeurl">CiteURL</a>.
To use it, go to the following URL, where <code>CITATION</code>
is your citation:</p>
<p><code>{base_url}/CITATION</code></p>
"""

MISSING_URL = """
<h1>Missing URL</h1>
<p>Sorry, I don't have a site to send you to for the {template}.
"""

NO_MATCH = """
<h1>Unrecognized Citation</h1>
<p>Sorry, "{query}" isn't a citation I recognize.</p>
"""

def format(text: str, **kwargs):
    text = text.format(**kwargs)
    return f"""<head>\n{HEAD}\n</head>\n{text}"""

############################################
# Routes
############################################

@APP.route('/')
def _index():
    return format(INDEX, base_url=APP.base_url)

@APP.route('/<query>')
def _read_citation(query: str):
    query = unquote(query)
    cite = APP.citator.lookup(query)
    if cite and cite.URL:
        return redirect(cite.URL, code=301)
    elif cite:
        return make_response(
            format(MISSING_URL, template=cite.template.name),
            501
        )
    else:
        return make_response(format(NO_MATCH, query=query), 400)

def get_local_ip():
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

def serve(citator, IP='auto', port=53037):
    """
    Host the given Citator as a server via HTTP. If IP is 'auto', use
    get_local_ip() to find the IP address to host at.
    """
    if IP == 'auto':
        IP = get_local_ip()
    
    APP.base_url = f'http://{IP}:{port}'
    APP.citator = citator
    
    server = WSGIServer((IP, port), APP)
    print(f'Now hosting citation lookup server at {APP.base_url}...')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopped hosting citation lookup server.")
