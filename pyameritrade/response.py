#!/usr/bin/env python

import re
import logging
import ujson

from pyameritrade.urls import URLs
from pyameritrade.items import TokenItem, QuoteItem, InstrumentItem,\
                               AccountItem, PriceHistoryItem, MoverItem

from pyameritrade.exception import RequestError
from pyameritrade.utils import pp

class Response():
    logger = logging.getLogger('pyameritrade.Response')

    def __init__(self, url, raw_response, client):
        self.url = url
        self.raw_response = raw_response
        self.client = client

        self.items = None
        self.headers = raw_response.headers

        self.error = None
        if not self.raw_response.ok:
            raise RequestError(url=self.url, request=self.raw_response.request, response=self.raw_response)

        # Actually 'text/html;charset=UTF-8'
            # should we take the encoding into account?
        if self.raw_response.headers['Content-Type'].startswith('application/json'):
            data = ujson.loads(self.raw_response.content)
        else:
            raise TypeError("Not Configured to handle %s" % self.raw_response.headers['Content-Type'])

        self.items = self.parse(url, data, client)


    def parse(self, url, data, client):
        # check url to see which type of response we are expecting,
        # hence which type of items to return
        if URLs.match(URLs.TOKEN, url):
            return TokenItem(data, client)

        elif self.client.redirect_url + URLs.AUTH_TOKEN.value == url:
            return TokenItem(data, client)

        elif URLs.match(URLs.QUOTES, url):
            quotes = list()
            for symbol, quote_json in data.items():
                quotes.append(QuoteItem(symbol, quote_json, client))
            return quotes

        elif URLs.match(URLs.GET_INSTRUMENT, url):
            #Assuming it's safe to just grab the first item...
            return InstrumentItem(next(iter(data)), client)

        elif URLs.match(URLs.SEARCH_INSTRUMENTS, url):
            instruments = list()
            for symbol, instrument_json in data.items():
                instruments.append(InstrumentItem(instrument_json, client))
            return instruments

        elif URLs.match(URLs.GET_ACCOUNT, url):
            account_type = next(iter(data))
            return AccountItem(account_type, data[account_type], client)

        elif URLs.match(URLs.GET_LINKED_ACCOUNTS, url):
            accounts = list()
            for all_accounts_json in data:
                for account_type, account_json in all_accounts_json.items():
                    accounts.append(AccountItem(account_type, account_json, client))
            return accounts

        elif URLs.match(URLs.PRICE_HISTORY, url):
            return PriceHistoryItem(data, client)

        elif URLs.match(URLs.GET_MOVERS, url):
            movers = list()
            for mover_json in data:
                movers.append(MoverItem(mover_json, client))
            return movers
