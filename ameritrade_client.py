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
    ROOT = "https://api.tdameritrade.com/v1"
    TOKEN = ROOT + "/oauth2/token"
    GET_ACCOUNT = ROOT + "/accounts/%s"
    QUOTES = ROOT + "/marketdata/%s/quotes"
    SEARCH_INSTRUMENTS = ROOT + "/instruments"
    GET_INSTRUMENT = SEARCH_INSTRUMENTS + "/%s"


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

    ############################################################
    #### Instruments
    ############################################################

    def get_instrument(self, cusip):
        return self.get(AmeritradeURLs.GET_INSTRUMENT.value % cusip)

    def search_instruments(self, symbol, projection):
        """
        symbol:  Value to pass to the search

        projection:
        ~~~~~~~~~~~
        symbol-search: Retrieve instrument data of a specific symbol or cusip
        symbol-regex: Retrieve instrument data for all symbols matching regex. Example: symbol=XYZ.* will return all symbols beginning with XYZ
        desc-search: Retrieve instrument data for instruments whose description contains the word supplied. Example: symbol=FakeCompany will return all instruments with FakeCompany in the description.
        desc-regex: Search description with full regex support. Example: symbol=XYZ.[A-C] returns all instruments whose descriptions contain a word beginning with XYZ followed by a character A through C.
        fundamental: Returns fundamental data for a single instrument specified by exact symbol.
        """
        return self.get(AmeritradeURLs.SEARCH_INSTRUMENTS.value, {'symbol':symbol, 'projection':projection})

    ############################################################
    #### Accounts
    ############################################################

    def get_account(self, account_id=None, fields=None):
        """
        Balances displayed by default, additional fields can be added here by adding positions or orders
        Example: fields=positions,orders
        """
        if not account_id:
            account_id = self.account_id
        if fields:
            fields = {'fields': fields}
        return self.get(AmeritradeURLs.GET_ACCOUNT.value % account_id, fields)

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

    def __init__(self, json, client):
        self.json = json
        self.client = client

    @classmethod
    def parse(klass, url, json, client):
        #check url to see which type of response we are expecting,
        # hence which type of Item to return
        if url == AmeritradeURLs.TOKEN.value:
            return TokenItem(json, client)
        elif url == AmeritradeURLs.QUOTES.value:
            return QuoteItem(json, client)
        elif url in (AmeritradeURLs.GET_INSTRUMENT.value, AmeritradeURLs.SEARCH_INSTRUMENTS.value):
            return InstrumentItem(json, client)
        elif url == AmeritradeURLs.GET_ACCOUNT.value:
            return AccountItem(json, client)

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
        AmeritradeItem.__init__(self, json, client)

        #TODO Should these be dynamic?!?!
        # THERE's going to be lots of classes and attributes

        #   YES
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

    #just start with equity for now
    

class InstrumentItem(AmeritradeItem):
    logger = logging.getLogger('ameritrade.InstrumentItem')

    def __init__(self, json, client):
        AmeritradeItem.__init__(self, json, client)

    #TODO Shouldn't have to repeat this on each subclass
    def __repr__(self):
        return '     [  '+ self.__class__.__name__ +'  ]' + "     " + AmeritradeItem.__repr__(self)


class AccountItem(AmeritradeItem):
    logger = logging.getLogger('ameritrade.AccountItem')

    def __init__(self, json, client):
        AmeritradeItem.__init__(self, json, client)

    #TODO Shouldn't have to repeat this on each subclass
    def __repr__(self):
        return '     [  '+ self.__class__.__name__ +'  ]' + "     " + AmeritradeItem.__repr__(self)

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
        pp.pprint(self.raw_response.json())


class AmeritradeClient(RestAPI):
    logger = logging.getLogger('ameritrade.Client')

    # do we even need this?
    POST_HEADERS = {'Content-Type': 'application/json' }

    def __init__(self, client_id, account_id, redirect_url, refresh_token, access_token=None):
        self.client_id = client_id
        self.account_id = account_id
        self.redirect_url = redirect_url
        self.access_token = access_token
        self.refresh_token = refresh_token

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

        return AmeritradeClient(client_id, account_id, redirect_url, refresh_token)

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
    client = AmeritradeClient.from_config('client.config')
    client.grant_refresh_token()
    print(client.get_quote('PTN'))

