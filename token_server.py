#!/usr/bin/env/python

import os
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import ssl

import ujson

from pyameritrade.client import Client
from pyameritrade.urls import URLs

CLIENT_ID = "**********@AMER.OAUTHAP"
REDIRECT_URL = "https://127.0.0.1"

etc_dir = os.path.join(os.path.dirname(__file__), 'etc')

logging.basicConfig(level=logging.DEBUG,
                    handlers=[logging.FileHandler("token_server.log")],
                    format='%(asctime)s %(message)s',
                    )
AUTH_TOKEN = None

class Handler(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()


    def do_GET(self):
        logging.info("GET %s" % self.path)

        global AUTH_TOKEN

        path, _, query_string = self.path.partition('?')

        if path == '/':
            code = parse_qs(query_string)['code']
            am_client = Client(CLIENT_ID, REDIRECT_URL, access_code=code)
            token = am_client.grant_offline_token()
            AUTH_TOKEN = token.json

            self._set_headers()
            self.wfile.write('{"message": "auth token set"}'.encode('utf-8'))

        elif path == URLs.AUTH_TOKEN.value:
            logging.info("AUTH TOKEN: '%s'" % AUTH_TOKEN)
            if not AUTH_TOKEN:
                self.send_error(409, message='{"status":"auth code is not set"}',
                                     explain='Server auth code is not set. Authorize in web browser before continuing.')
                return

            self._set_headers()
            self.wfile.write(ujson.dumps(AUTH_TOKEN).encode('utf-8'))

        else:
            self.error_content_type = 'application/json'
            self.send_error(404)

if __name__ == "__main__":
    logging.info("Listening on 0.0.0.0:443")
    httpd = HTTPServer(('0.0.0.0', 443), Handler)

    httpd.socket = ssl.wrap_socket (httpd.socket,
            keyfile=os.path.join(etc_dir, 'key.pem'),
            certfile=os.path.join(etc_dir, 'certificate.pem'), server_side=True)

    httpd.serve_forever()
