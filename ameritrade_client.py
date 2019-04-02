#!/usr/bin/env python

import sys
import logging
from datetime import datetime
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
    QUOTES = ROOT + "/marketdata/quotes"
    PRICE_HISTORY = ROOT + "/marketdata/%s/pricehistory"
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
        return self.get(AmeritradeURLs.QUOTES.value, {'symbol':symbol.upper()})

    ###########################################################
    #### Prine History
    ############################################################

    def get_price_history(self, symbol, period_type=None, period=None, frequency_type=None, frequency=None,
                            end_date=None, start_date=None, need_extended_hours_data=True):

        params = dict()

        for k, v in locals().items():
            ## Maybe TODO Make that a generator expresssion

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

        print(params)
        return self.get(AmeritradeURLs.PRICE_HISTORY.value % symbol.upper(), params=params)

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


    ############################################################
    #### Orders
    ############################################################



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

class AmeritradeFee():
    logger = logging.getLogger('ameritrade.Fee')
    #https://www.tdameritrade.com/pricing.page
    #Stock commision $6.95
    #ETF commision $0 or $6.95
    #Options $6.95, plus $0.75 per contract
    #Options exercises and assignments $19.99
    #Futures and options on futures $2.25 per contract Plus exchange and regulatory fees

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
        elif url == AmeritradeURLs.PRICE_HISTORY.value:
            return PriceHistoryItem(json, client)

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

class AccountPriceHistoryItem(AmeritradeItem):
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
    GET_HEADERS = {}

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
            headers = self.GET_HEADERS
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

