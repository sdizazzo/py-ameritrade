#!/usr/bin/env python

import logging
from datetime import datetime

from urls import URLs

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

        return self.post(URLs.TOKEN.value, params, headers)

    def grant_offline_token(self):
        params = { 'grant_type': 'authorization_code',
                   'access_type': 'offline',
                   'code': self.access_token,
                   'client_id': self.client_id+"@AMER.OAUTHAP",
                   'redirect_uri': self.redirect_url}

        headers = { 'Content-Type': 'application/x-www-form-urlencoded' }

        return self.post(URLs.TOKEN.value, params, headers)


    def grant_auth_code(self):
        self.get(URLs.AUTH_CODE.value % (self.redirect_url, self.client_id+'@AMER.OAUTHAP'),
                 cert=('etc/certificate.pem', 'etc/key.pem')
                )

    ############################################################
    #### Quotes
    ############################################################

    def get_quotes(self, symbol):
        """
            https://developer.tdameritrade.com/quotes/apis/get/marketdata/quotes
        """

        return self.get(URLs.QUOTES.value, {'symbol':symbol.upper()})

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

        return self.get(URLs.PRICE_HISTORY.value % symbol.upper(), params=params)

    ############################################################
    #### Instruments
    ############################################################

    def get_instrument(self, cusip):
        """
            https://developer.tdameritrade.com/instruments/apis/get/instruments/%7Bcusip%7D
        """
        return self.get(URLs.GET_INSTRUMENT.value % cusip)

    def search_instruments(self, symbol, projection):
        """
            https://developer.tdameritrade.com/instruments/apis/get/instruments
        """
        return self.get(URLs.SEARCH_INSTRUMENTS.value, {'symbol':symbol, 'projection':projection})


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
        return self.get(URLs.GET_ACCOUNT.value % account_id, fields)


    def get_linked_accounts(self, fields=None):
        """
            https://developer.tdameritrade.com/account-access/apis/get/accounts-0
        """
        # NOTE: QUESTION:  How is it linked?  By the App?
        if fields:
            fields = {'fields': fields}
        return self.get(URLs.GET_LINKED_ACCOUNTS.value, fields)


    ############################################################
    #### Orders
    ############################################################

    #TODO



