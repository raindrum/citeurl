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

@APP.route('/')
def _index():
    return (
        '<h1>CiteURL</h1>'
        + '<p>This web app lets you look up legal citations with '
        + '<a href="https://raindrum.github.io/citeurl">CiteURL</a>. '
        + 'To use it, go to the following URL, where <code>CITATION</code> '
        + 'is your citation:</p>\n'
        + f'<p><code>{APP.base_url}/CITATION</code></p>\n'
    )

@APP.route('/<query>')
def _read_citation(query: str):
    cite = APP.citator.lookup(unquote(query))
    if cite and cite.URL:
        return redirect(cite.URL, code=301)
    elif cite:
        html = (
            '<h1>Missing URL</h1>\n'
            + '<p>Sorry, I don\'t have a site to send you to for '
            + f'the {cite.template}.'
        )
        return make_response(html, 501)
    else:
        html = (
            '<h1>Unrecognized Citation</h1>\n<p>Sorry, '
            +f'"{unquote(query)}" isn\'t a citation I recognize.</p>'
        )
        return make_response(html, 400)

def get_ip():
    "get local IP address. source: https://stackoverflow.com/a/28950776"
    # first, get the local IP address
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

def serve(citator, IP='localhost', port=53037):
    "Host the given Citator as a server"
    if IP == 'localhost':
        IP = get_ip()
    
    APP.base_url = f'http://{IP}:{port}'
    APP.citator = citator
    
    server = WSGIServer((IP, port), APP)
    print(f'Now hosting lookup server at {APP.base_url}...')
    server.serve_forever()
