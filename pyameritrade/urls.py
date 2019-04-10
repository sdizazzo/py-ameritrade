#!/usr/bin/env python

import re
from enum import Enum


class NoValue(Enum):
    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)

class URLs(NoValue):
    ROOT = "https://api.tdameritrade.com/v1"
    TOKEN = ROOT + "/oauth2/token"
    AUTH_CODE = "https://auth.tdameritrade.com/auth?response_type=code&redirect_uri=%s&client_id=%s"
    GET_ACCOUNT = ROOT + "/accounts/%s"
    GET_LINKED_ACCOUNTS = ROOT + "/accounts"
    QUOTES = ROOT + "/marketdata/quotes"
    PRICE_HISTORY = ROOT + "/marketdata/%s/pricehistory"
    SEARCH_INSTRUMENTS = ROOT + "/instruments"
    GET_INSTRUMENT = SEARCH_INSTRUMENTS + "/%s"
    GET_MOVERS = ROOT + "/marketdata/%s/movers"

    @classmethod
    def match(klass, URL, url):
                                                        #There's probably a more 
                                                        #general way to do this
        return re.match(URL.value.replace('%s','.+').replace('?', r'\?'), url)
