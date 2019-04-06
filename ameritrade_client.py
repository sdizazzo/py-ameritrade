#!/usr/bin/env python

import sys
import logging
from datetime import datetime
from enum import Enum
from functools import partial
from json.decoder import JSONDecodeError

import requests
import urllib.parse
import ujson

import pprint
pp = pprint.PrettyPrinter(indent=4)


########################################
# EMAIL CONTACT: apidev@tdameritrade.com
########################################

#CONSTANTS
EPOCH = datetime.utcfromtimestamp(0)

VALID_PERIOD_TYPES = {'day':   (1,2,3,4,5,10),
                      'month': (1,2,3,6),
                      'year':  (1,2,3,5,10,15,20),
                      'ytd':   (1,)
                      }

VALID_FREQUENCY_TYPES = {'minute':  (('day',),                 (1,5,10,15,30)),
                         'daily':   (('month', 'year', 'ytd'), (1,)),
                         'weekly':  (('month', 'year', 'ytd'), (1,)),
                         'monthly': (('monthly'),              (1,))
                        }


class NoValue(Enum):
    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)

class AmeritradeURLs(NoValue):
    ROOT = "https://api.tdameritrade.com/v1"
    TOKEN = ROOT + "/oauth2/token"
    GET_ACCOUNT = ROOT + "/accounts/%s"
    GET_LINKED_ACCOUNTS = ROOT + "/accounts"
    QUOTES = ROOT + "/marketdata/quotes"
    PRICE_HISTORY = ROOT + "/marketdata/%s/pricehistory"
    SEARCH_INSTRUMENTS = ROOT + "/instruments"
    GET_INSTRUMENT = SEARCH_INSTRUMENTS + "/%s"


class RestAPI():
    logger = logging.getLogger('ameritrade.RestAPI')

    ############################################################
    #### Authentication
    ############################################################

    def grant_refresh_token(self):
        """
            https://developer.tdameritrade.com/content/simple-auth-local-apps
            https://developer.tdameritrade.com/authentication/apis/post/token-0
        """

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

    def get_quotes(self, symbol):
        """
            https://developer.tdameritrade.com/quotes/apis/get/marketdata/quotes
        """

        return self.get(AmeritradeURLs.QUOTES.value, {'symbol':symbol.upper()})

    ###########################################################
    #### Price History
    ############################################################

    def get_price_history(self, symbol, period_type=None, period=None, frequency_type=None, frequency=None,
                            end_date=None, start_date=None, need_extended_hours_data=True):
        """
            https://developer.tdameritrade.com/price-history/apis/get/marketdata/%7Bsymbol%7D/pricehistory
        """
        params = dict()

        for k, v in locals().items():

            # BUG needExtendedHoursData when False will never be set
            if not v or k in ('self', 'symbol'):
                continue

            if k == 'period_type':
                if not v in VALID_PERIOD_TYPES.keys():
                    raise TypeError("Invalid period_type '%s'.  Must be in '%s'" % (v, VALID_PERIOD_TYPES.keys()))
                params['periodType'] = v

            if k == 'period':
                # verify the period against the periodType
                period = int(v)
                period_type = params.get('periodType', 'day')
                if not period in VALID_PERIOD_TYPES[period_type]:
                    raise TypeError("Invalid period '%s' for period_type '%s'.  Must be in '%s'" % (period, period_type, VALID_PERIOD_TYPES[period_type]))
                params['period'] = period

            if k == 'frequency_type':
                period_type = params.get('periodType', 'day')

                frequency_type_validator = VALID_FREQUENCY_TYPES.get(v)
                if not frequency_type_validator:
                    raise TypeError("Invalid frequncy_type '%s'. Must be in %s" % (v, VALID_FREQUENCY_TYPES.keys()))

                #verify frequecy_type for period_type
                if not period_type in frequency_type_validator[0]:
                    raise TypeError("Invalid frequncy_type '%s' for period_type '%s'. Must be in '%s'" % (v, period_type, frequency_type_validator[0]))

                params['frequencyType'] = v

            if k == 'frequency':
                frequency_type = params.get('frequencyType')
                if frequency_type:
                    frequency_type_validator = VALID_FREQUENCY_TYPES.get(frequency_type)
                    if not v in frequency_type_validator[1]:
                        raise TypeError("Invalid frequency '%s' for frequency_type '%s'. Must be in '%s'" % (v, frequency_type, frequency_type_validator[1]))
                params['frequency'] = int(v)

            if k == 'end_date':
                assert isinstance(v, datetime)
                #End date as milliseconds since epoch
                params['endDate'] = int((v-EPOCH).total_seconds()*1000.0)

            if k == 'start_date':
                assert isinstance(v, datetime)
                #End date as milliseconds since epoch
                params['startDate'] = int((v-EPOCH).total_seconds()*1000.0)

            if k == 'need_extended_hours_data':
                params['needExtendedHoursData'] = v

            # If startDate and endDate are provided, period should not be provided. 
            if all((params.get('startDate'), params.get('endDate'), params.get('period'))):
                raise TypeError("If 'start_date' and 'end_date' are provided, 'period' should not be provided.")

        return self.get(AmeritradeURLs.PRICE_HISTORY.value % symbol.upper(), params=params)

    ############################################################
    #### Instruments
    ############################################################

    def get_instrument(self, cusip):
        """
            https://developer.tdameritrade.com/instruments/apis/get/instruments/%7Bcusip%7D
        """
        return self.get(AmeritradeURLs.GET_INSTRUMENT.value % cusip)

    def search_instruments(self, symbol, projection):
        """
            https://developer.tdameritrade.com/instruments/apis/get/instruments
        """
        return self.get(AmeritradeURLs.SEARCH_INSTRUMENTS.value, {'symbol':symbol, 'projection':projection})


    ############################################################
    #### Accounts
    ############################################################

    def get_account(self, account_id=None, fields=None):
        """
            https://developer.tdameritrade.com/account-access/apis/get/accounts/%7BaccountId%7D-0
        """
        if not account_id:
            account_id = self.account_id
        if fields:
            fields = {'fields': fields}
        return self.get(AmeritradeURLs.GET_ACCOUNT.value % account_id, fields)


    def get_linked_accounts(self, fields=None):
        """
            https://developer.tdameritrade.com/account-access/apis/get/accounts-0
        """
        # NOTE: QUESTION:  How is it linked?  By the App?
        if fields:
            fields = {'fields': fields}
        return self.get(AmeritradeURLs.GET_LINKED_ACCOUNTS.value, fields)


    ############################################################
    #### Orders
    ############################################################

    #TODO


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
            self.message = "Got an error requesting %s\n\n%s\n\nERROR:\n%s\n\nRequest params:\n%s\n\nRequest headers:\n%s" % (url, self.response,  pp.pformat(self.response.json()), request, self.request.headers)
        except JSONDecodeError:
            self.message = "Got an error requesting %s\n\n%s\nERROR:\n%s\n\nRequest params:\n%s" % (url, self.response, pp.pformat(self.response.content), request)

        self.logger.exception(self.message)
        print()
        super().__init__(self, self.response.json())


class AmeritradeFee():
    logger = logging.getLogger('ameritrade.Fee')
    #https://www.tdameritrade.com/pricing.page
    #Stock commision $6.95
    #ETF commision $0 or $6.95
    #Options $6.95, plus $0.75 per contract
    #Options exercises and assignments $19.99
    #Futures and options on futures $2.25 per contract Plus exchange and regulatory fees

    # NOTE Some fees are variable, so we might want to make them
    # configurable via the config file
    # or perhaps they can be grabbed from the Account object


    ## Futures Options / contract
    ## comission = 2.25
    ## exchange_fee = 1.45
    ## NFA_fee = .02

    # Not sure if this matters or not
    ## TAX_RATE = ??


class AmeritradeItem():
    logger = logging.getLogger('ameritrade.Item')

    def __init__(self, json, client):
        self.json = json
        self.client = client

        for k, v in self.json.items():
            setattr(self, k, v)


    def __repr__(self):
        # This isn't very useful as is
        desc = "< "
        for k, v in self.__dict__.items():
            if not v or k in ('json', 'client'): continue
            desc += "%s : %s, " % (k, v)
        desc += " >"
        return pp.pformat(desc)


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

        self.client.access_token = self.access_token

    def __repr__(self):
        return '     [  '+ self.__class__.__name__ +'  ]' + "     " + AmeritradeItem.__repr__(self)


class QuoteItem(AmeritradeItem):
    logger = logging.getLogger('ameritrade.QuoteItem')

    def __init__(self, symbol, json, client):
        AmeritradeItem.__init__(self, json, client)

        self.symbol = symbol


    #TODO Shouldn't have to repeat this on each subclass
    def __repr__(self):
        return '     [  '+ self.__class__.__name__ +'  ]' + "     " + AmeritradeItem.__repr__(self)


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


class PriceHistoryItem(AmeritradeItem):
    logger = logging.getLogger('ameritrade.PriceHistoryItem')

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

        self.items = None
        self.headers = raw_response.headers

        self.error = None
        if not self.raw_response.ok:
            raise RequestError(url=self.url, request=self.raw_response.request, response=self.raw_response)

        self.items = self.parse(url, self.raw_response.json(), client)

    def parse(self, url, json, client):
        # check url to see which type of response we are expecting,
        # hence which type of items to return

        if url == AmeritradeURLs.TOKEN.value:
            return TokenItem(json, client)

        elif url == AmeritradeURLs.QUOTES.value:
            quotes = list()
            for symbol, quote_json in json.items():
                quotes.append(QuoteItem(symbol, quote_json, client))
            return quotes

        elif url in (AmeritradeURLs.GET_INSTRUMENT.value, AmeritradeURLs.SEARCH_INSTRUMENTS.value):
            #This needs to look for multiple items and split them out
            return InstrumentItem(json, client)

        elif url == (AmeritradeURLs.GET_ACCOUNT.value, AmeritradeURLs.GET_LINKED_ACCOUNTS.value):
            #This needs to look for multiple items and split them out
            return AccountItem(json, client)

        elif url == AmeritradeURLs.PRICE_HISTORY.value:
            return PriceHistoryItem(json, client)


class AmeritradeClient(RestAPI):
    logger = logging.getLogger('ameritrade.Client')

    # do we even need this?
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

        return AmeritradeClient(client_id, account_id, redirect_url, refresh_token)

    def get(self, url, params=None, headers=None, timeout=2):
        self.logger.info('GET %s' % url)

        headers = self.HEADERS if not headers else headers.update(self.HEADERS)

        response = requests.get(url, params, headers=headers, timeout=timeout)

        # a 401 will trigger a request to refresh our token 
        if response.status_code == 401:
            self.logger.info('Refreshing token')
            self.grant_refresh_token()
            self.logger.info('Sending GET request again after refreshing token')
            response = requests.get(url, params, headers=headers, timeout=timeout)

        response = AmeritradeResponse(url, response, self)
        self.logger.debug('GET response: %s' % pp.pformat(response.items))
        return response.items


    def post(self, url, params, headers=None, timeout=2):
        self.logger.info('POST %s' % url)

        headers = self.HEADERS if not headers else headers.update(self.HEADERS)

        # Do we need to check for 401 token expired errors on POST?
        # Maybe only once we get to the access_token itself expiring
        response = requests.post(url,
                                 params,
                                 headers=headers
                                )

        response = AmeritradeResponse(url, response, self)
        self.logger.debug('POST response: %s' % pp.pformat(response.items))
        return response.items


if __name__ == '__main__':
    client = AmeritradeClient.from_config('client.config')
    client.grant_refresh_token()
    print(client.get_quotes('PTN'))

