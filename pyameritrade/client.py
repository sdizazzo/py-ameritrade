#!/usr/bin/env python

import sys
import logging

import requests
import ujson

import pprint
pp = pprint.PrettyPrinter(indent=4)

from pyameritrade.rest_api import RestAPI
from pyameritrade.response import Response


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

    def __init__(self, client_id, account_id, redirect_url, refresh_token, access_token=None):
        self._access_token = None

        self.client_id = client_id
        self.account_id = account_id
        self.redirect_url = redirect_url
        self.access_token = access_token
        self.refresh_token = refresh_token

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, value):
        self._access_token = value
        if value:
            self.HEADERS.update({'Authorization':'Bearer %s' % value})
        #else:
        #    del self.HEADERS['Authorization']
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

        return Client(client_id, account_id, redirect_url, refresh_token)

    def get(self, url, params=None, headers=None, timeout=2, **kwargs):
        self.logger.info('GET %s' % url)

        headers = self.HEADERS if not headers else headers.update(self.HEADERS)

        response = requests.get(url, params, headers=headers, timeout=timeout, **kwargs)

        # a 401 will trigger a request to refresh our token 
        if response.status_code == 401:
            self.logger.info('Refreshing token')
            self.grant_refresh_token()
            self.logger.info('Sending GET request again after refreshing token')
            response = requests.get(url, params, headers=headers, timeout=timeout, **kwargs)

        response = Response(url, response, self)
        self.logger.debug('GET response: %s' % pp.pformat(response.items))
        return response.items


    def post(self, url, params, headers=None, timeout=2, **kwargs):
        self.logger.info('POST %s' % url)

        headers = self.HEADERS if not headers else headers.update(self.HEADERS)

        # Do we need to check for 401 token expired errors on POST?
        # Maybe only once we get to the access_token itself expiring
        response = requests.post(url,
                                 params,
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

