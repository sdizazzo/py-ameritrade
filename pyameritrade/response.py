#!/usr/bin/env python

import re
import logging

from pyameritrade.urls import URLs
from pyameritrade.items import TokenItem, QuoteItem, InstrumentItem,\
                               AccountItem, PriceHistoryItem, MoverItem

from pyameritrade.exception import RequestError


class Response():
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
        if URLs.match(URLs.TOKEN, url):
            return TokenItem(json, client)

        elif URLs.match(URLs.AUTH_CODE, url):
            print(raw_response.text)

        elif URLs.match(URLs.QUOTES, url):
            quotes = list()
            for symbol, quote_json in json.items():
                quotes.append(QuoteItem(symbol, quote_json, client))
            return quotes

        elif URLs.match(URLs.GET_INSTRUMENT, url):
            #Assuming it's safe to just grab the first item...
            return InstrumentItem(next(iter(json)), client)

        elif URLs.match(URLs.SEARCH_INSTRUMENTS, url):
            instruments = list()
            for symbol, instrument_json in json.items():
                instruments.append(InstrumentItem(instrument_json, client))
            return instruments

        elif URLs.match(URLs.GET_ACCOUNT, url):
            account_type = next(iter(json))
            return AccountItem(account_type, json[account_type], client)

        elif URLs.match(URLs.GET_LINKED_ACCOUNTS, url):
            accounts = list()
            for all_accounts_json in json:
                for account_type, account_json in all_accounts_json.items():
                    accounts.append(AccountItem(account_type, account_json, client))
            return accounts

        elif URLs.match(URLs.PRICE_HISTORY, url):
            return PriceHistoryItem(json, client)

        elif URLs.match(URLs.GET_MOVERS, url):
            movers = list()
            for mover_json in json:
                movers.append(MoverItem(mover_json, client))
            return movers
