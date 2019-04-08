#!/usr/bin/env/python

import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import ssl

import pprint
pp = pprint.PrettyPrinter(indent=4)

from pyameritrade.client import Client

CLIENT_ID = "**********@AMER.OAUTHAP"
REDIRECT_URL = "https://127.0.0.1"

etc_dir = os.path.join(os.path.dirname(__file__), 'etc')

class Handler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        path, _, query_string = self.path.partition('?')
        if path == '/favicon.ico': return

        code = parse_qs(query_string)['code']

        self.am_client = Client(CLIENT_ID, None, REDIRECT_URL, None, access_token=code)
        tokens = self.am_client.grant_offline_token()
        self.wfile.write(pp.pformat(tokens.json).encode('utf-8'))


httpd = HTTPServer(('127.0.0.1', 443), Handler)

httpd.socket = ssl.wrap_socket (httpd.socket,
        keyfile=os.path.join(etc_dir, 'key.pem'),
        certfile=os.path.join(etc_dir, 'certificate.pem'), server_side=True)

httpd.serve_forever()
