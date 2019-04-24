#!/usr/bin/env python

import sys, os
import logging
import webbrowser

import requests
import ujson

from pyameritrade.rest_api import RestAPI
from pyameritrade.response import Response
from pyameritrade.urls import URLs
from pyameritrade.exception import RequestError
from pyameritrade.utils import pp


###############################################
#
# WEB PAGE:  https://developer.tdameritrade.com
#
# EMAIL CONTACT: apidev@tdameritrade.com
#
###############################################



class Client(RestAPI):
    logger = logging.getLogger('pyameritrade.Client')

    HEADERS = {'Content-Type': 'application/json' }

    def __init__(self, client_id, redirect_url, server_cert=False, access_code=None):
        self.client_id = client_id
        self.redirect_url = redirect_url
        self.server_cert = server_cert
        self.access_code = access_code

        self.session = requests.Session()

        self.auth_token = None

    def authenticate(self):
        try:
            self.auth_token = self.get_auth_token()
        except RequestError as e:
            #if the response if 409 Conflict,
            # Open the browser to their auth page for now
            if e.response.status_code == 409:
                webbrowser.open(URLs.USER_AUTH.value % (self.redirect_url, self.client_id+'@AMER.OAUTHAP'), new=1)

                #lol...reminds me of my Apple IIe
                input("Once authenticated, hit a key to continue...")
                self.auth_token = self.get_auth_token()
            else:
                raise

        # NOTE Any better to store headers in the session?
        #self.session.headers = {'Content-Type': 'application/json'}


    @classmethod
    def from_config(klass, path):
        with open(path, 'r') as fo:
            try:
                config = ujson.load(fo)
            except ValueError:
                klass.logger.critical("Error parsing config file: %s.  Please review for errors and try again." % path)
                sys.exit(1)

        client = config['client']

        client_id = client['client_id']
        redirect_url = client['redirect_url']
        server_cert = client.get('server_cert', False)

        return Client(client_id, redirect_url, server_cert)


    def get(self, url, params=None, headers=None, timeout=2, **kwargs):
        self.logger.info('GET %s' % url)

        # This doesnt work how I'm expecting.
        # better to use the session object
        headers = self.HEADERS if not headers else headers.update(self.HEADERS)
        response = self.session.get(url, params=params, headers=headers, timeout=timeout, **kwargs)

        # a 401 will trigger a request to refresh our token 
        if response.status_code == 401:
            self.logger.info('Refreshing token')
            self.grant_refresh_token()
            self.logger.info('Sending GET request again after refreshing token')
            response = self.session.get(url, params=params, headers=headers, timeout=timeout, **kwargs)

        response = Response(url, response, self)
        self.logger.debug('GET response: %s' % pp.pformat(response.items))
        return response.items


    def post(self, url, params, headers=None, timeout=2, **kwargs):
        self.logger.info('POST %s' % url)

        headers = self.HEADERS if not headers else headers.update(self.HEADERS)

        # Do we need to check for 401 token expired errors on POST?
        # Maybe only once we get to the access_token itself expiring
        response = self.session.post(url,
                                 data=params,
                                 headers=headers,
                                 **kwargs
                                )

        response = Response(url, response, self)
        self.logger.debug('POST response: %s' % pp.pformat(response.items))
        return response.items


if __name__ == '__main__':
    client = Client.from_config('client.config')
    client.grant_refresh_token()
    print(client.get_quotes('PTN'))

