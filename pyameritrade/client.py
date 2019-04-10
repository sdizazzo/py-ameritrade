#!/usr/bin/env python

import sys, os
import logging

import requests
import ujson

from pyameritrade.rest_api import RestAPI
from pyameritrade.response import Response
from pyameritrade.utils import pp

###############################################
#
# WEB PAGE:  https://developer.tdameritrade.com
#
# EMAIL CONTACT: apidev@tdameritrade.com
#
###############################################



class Client(RestAPI):
    logger = logging.getLogger('ameritrade.Client')

    HEADERS = {'Content-Type': 'application/json' }

    def __init__(self, client_id, account_id, redirect_url, refresh_token, server_cert=None, access_token=None):
        self._access_token = None

        # TODO Figure out which of these can be mandatory or optional
        # I guess it depends on if we can get the access token working
        # automatically or not
        self.client_id = client_id
        self.account_id = account_id
        self.redirect_url = redirect_url
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.server_cert = os.path.abspath(server_cert)

        self.session = requests.Session()

        # NOTE Any better to store headers in the session?
        #self.session.headers = {'Content-Type': 'application/json' }

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, value):
        self._access_token = value
        if value:
            self.HEADERS.update({'Authorization':'Bearer %s' % value})
        else:
            self.HEADERS.update({'Authorization': None})
        # NOTE if None is passed in, should we remove the value?

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
        account_id = client['account_id'] # NOTE this doesn't really need to be mandatory
        redirect_url = client['redirect_url']
        refresh_token = client['refresh_token']
        server_cert = client['server_cert']

        return Client(client_id, account_id, redirect_url, refresh_token, server_cert=server_cert)


    def get(self, url, params=None, headers=None, timeout=2, **kwargs):
        self.logger.info('GET %s' % url)

        # This doesnt work how I'm expecting.
        # better to use the session object
        headers = self.HEADERS if not headers else headers.update(self.HEADERS)
        print("HEADERS: %s " % headers)
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

