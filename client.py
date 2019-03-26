#!/usr/bin/env python

import sys
import logging
from enum import Enum
from json.decoder import JSONDecodeError

import requests
import urllib.parse
import ujson

import pprint
pp = pprint.PrettyPrinter(indent=4)


########################################
# EMAIL CONTACT: apidev@tdameritrade.com
########################################

class NoValue(Enum):
    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)

class AmeritradeURLs(NoValue):
    TOKEN = "https://api.tdameritrade.com/v1/oauth2/token"
    QUOTES = "https://api.tdameritrade.com/v1/marketdata/%s/quotes"


class RestAPI(object):
    logger = logging.getLogger('ameritrade.RestAPI')

    ############################################################
    #### Authentication
    ############################################################

    def grant_refresh_token(self):
        params = {"grant_type":"refresh_token",
                  "refresh_token":self.refresh_token,
                  "client_id": self.client_id+"@AMER.OAUTHAP"}

        headers = {'Content-Type':'application/x-www-form-urlencoded'}

        return self.post(AmeritradeURLs.TOKEN.value, params, headers)

    def grant_auth_code(self):
        pass

    ############################################################
    #### Quotes
    ############################################################

    def get_quote(self, symbol):
        return self.get(AmeritradeURLs.QUOTES.value % symbol)


class RequestError(Exception):
    logger = logging.getLogger('ameritrade.RequestError')

    def __init__(self, url, request, response):
        self.url = url
        self.request = request
        self.response = response

        #
        # In case of no params
        #
        if self.request.body:
            request = pp.pformat(ujson.loads(self.request.body))
        else:
            request = None

        #TODO clean this up
        try:
            self.message = "Got an error requesting %s\n\n%s\n\nERROR:\n%s\n\nRequest params:\n%s" % (url, self.response,  pp.pformat(self.response.json()), request)
        except JSONDecodeError:
            self.message = "Got an error requesting %s\n\n%s\nERROR:\n%s\n\nRequest params:\n%s" % (url, self.response, pp.pformat(self.response.content), request)

        self.logger.exception(self.message)
        print()
        super().__init__(self, self.response.json())


class AmeritradeItem():
    logger = logging.getLogger('ameritrade.Item')

    @classmethod
    def parse(klass, url, json, client):
        #check url to see which type of response we are expecting
        if url == AmeritradeURLs.TOKEN.value:
            return TokenItem(json, client)
        elif url == AmeritradeURLs.QUOTES.value:
            return QuoteItem(json, client)

    def __repr__(self):
        desc = "< "
        for k, v in self.__dict__.items():
            if not v: continue
            desc += "%s : %s, " % (k, v)
        desc += " >"
        return desc


class TokenItem(AmeritradeItem):
    logger = logging.getLogger('ameritrade.TokenItem')

    """
    {
        "access_token": "string",
        "refresh_token": "string",
        "token_type": "string",
        "expires_in": 0,
        "scope": "string",
        "refresh_token_expires_in": 0
    }
    """

    def __init__(self, json, client):
        self.client = client
        self.client.access_token = self.access_token = json.get('access_token')
        self.refresh_token = json.get('refresh_token')
        self.token_type = json.get('token_type')
        self.expires_in = json.get('expires_in')
        self.scope = json.get('scope')
        self.refresh_token_expires_in = json.get('refresh_token_expires_in')


    def __repr__(self):
        return '     [  '+ self.__class__.__name__ +'  ]' + "     " + AmeritradeItem.__repr__(self)

class QuoteItem(AmeritradeItem):
    logger = logging.getLogger('ameritrade.QuoteItem')
    # Several different subclasses
    # Mutual Fund
    # Future
    # Future Options
    # Index
    # Option
    # Forex
    # ETF
    # Equity


    



class AmeritradeResponse():
    logger = logging.getLogger('ameritrade.Response')

    def __init__(self, url, raw_response, client):
        self.url = url
        self.raw_response = raw_response
        self.client = client

        self.headers = raw_response.headers

        self.error = None
        if not self.raw_response.ok:
            raise RequestError(url=self.url, request=self.raw_response.request, response=self.raw_response)

        response_item = AmeritradeItem.parse(url, self.raw_response.json(), client)



class AmeritradeClient(RestAPI):
    logger = logging.getLogger('ameritrade.Client')

    # do we even need this?
    POST_HEADERS = {'Content-Type': 'application/json' }

    def __init__(self, client_id, redirect_url, refresh_token, access_token=None):
        self.client_id = client_id
        self.redirect_url = redirect_url
        self.access_token = access_token
        self.refresh_token = refresh_token


    def get(self, url, params=None, headers=None, timeout=2):
        self.logger.info('GET %s' % url)

        if not headers:
            headers = self.POST_HEADERS
            if self.access_token:
                headers.update({'Authorization':'Bearer %s' % self.access_token})

        response = requests.get(url,
                                params,
                                headers=headers
                                )

        response = AmeritradeResponse(url, response, self)
        self.logger.debug('GET response: %s' % pp.pformat(response))
        return response



    def post(self, url, params, headers=None, timeout=2):
        self.logger.info('POST %s' % url)
        #Do we even need this?
        #params.update((k, urllib.parse.unquote(v)) for k, v in params.items())

        if not headers:
            headers = self.POST_HEADERS
            if self.access_token:
                headers.update({'Authorization':'Bearer %s' % self.access_token})

        response = requests.post(url,
                                 params,
                                 headers=headers
                                )

        response = AmeritradeResponse(url, response, self)
        self.logger.debug('POST response: %s' % pp.pformat(response))
        return response


if __name__ == '__main__':
    CLIENT_ID = 'FF7C19B25AF18'
    REDIRECT_URL = 'https://10.0.1.103'
    REFRESH_TOKEN = 'F3dw4plOC2ChbUuiQFCIyGpVjggIJNfJx8z0xq7UFv5NH/aC0KUUcq23M9mXf866UqmeCmt8g9vglVre+6zWiDkcbR89pst6JO+wrbv1ZYR8uStGIp02bCDa89/T1KNyRy1bhSw0jAuFEeyU6/wmdK1B8GOrR5rF2PNThUn90/tDuJqPBGQdc9TqKp1Hg5pGNTwKsPkbog0BZsdcZhdX/w6LjooiTjW7ux4sAhr3w7JV4QBBqcLwJ+HUEy6jmlGYRSkfZQ1wrDDmj4aDwyC6DV/Ih2Owt4O3AETyJYTBJJEc+MdLI3WYYS7PwnaMdiHu94+v7a20gN9OMVfIwHGKrvCCA87TPBRO13hPGtLXdcK3Tv4yUiJ6tYzIXjmJ5xH4qF4BqAicMrwYrQ0cP471jlwK8033K7GINsCXVztymqwQcPxjrkLOksFDHm5100MQuG4LYrgoVi/JHHvl9H9TDb2kEqCev9akh6Hph9bCdPY1vLnE2pRxk9g/XNYWsXxXFmGUjFU7GhrAkmRtEFPEwGG8x4fLWgT2zBAHGqZ5tg4s7vzDH8ynvksYY7iU3TL6hHJ9esKUaNIHhsRbsPHTUqf+kpJ8w9vfoby2cANXO/qbrQVLxWlFO1hlazCZdJE82vE3bpj3YqvruGtqpopPfAQB6yK/9zIMXaYODkIaMqf4PkOF+h6+22jCWqseG/nwRCxVBSTgfNFczzzE33eGoku89u+jQ9dYLEMrGvBG0w5cy3z9RwMLfjY95u1OOMj0e7nXbrVTr7N8d7ne4EzXSoLXGu/jattWe76qzHmUZdMbKiwfmpYOiE9u+Pap0YBe7hXdPsf7oEUCvcnyb7OPYaxZBmph2Ft/Bl+KO14KnVv24bO4mccCLsP9HcbtcM77EEFG5gA11lk=212FD3x19z9sWBHDJACbC00B75E'
    client = AmeritradeClient(CLIENT_ID, REDIRECT_URL, REFRESH_TOKEN)
    #print(client.grant_refresh_token())
    print(client.get_quote('PTN'))

