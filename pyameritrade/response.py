#!/usr/bin/env python

import logging

from pyameritrade.urls import URLs
from pyameritrade.items import TokenItem, QuoteItem, InstrumentItem, AccountItem, PriceHistoryItem

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
        if url == URLs.TOKEN.value:
            return TokenItem(json, client)

        elif url == URLs.AUTH_CODE.value:
            print(raw_response.text)

        elif url == URLs.QUOTES.value:
            quotes = list()
            for symbol, quote_json in json.items():
                quotes.append(QuoteItem(symbol, quote_json, client))
            return quotes

        elif url in (URLs.GET_INSTRUMENT.value, URLs.SEARCH_INSTRUMENTS.value):
            #This needs to look for multiple items and split them out
            return InstrumentItem(json, client)

        #it's ugly, but for now.  Maybe a regular expression later on
        elif url.startswith(URLs.GET_ACCOUNT.value.strip('%s')):
            account_type = next(iter(json))
            return AccountItem(account_type, json[account_type], client)

        elif url == URLs.GET_LINKED_ACCOUNTS.value:
            accounts = list()
            for all_accounts_json in json:
                for account_type, account_json in all_accounts_json.items():
                    accounts.append(AccountItem(account_type, account_json, client))
            return accounts

        elif url == URLs.PRICE_HISTORY.value:
            return PriceHistoryItem(json, client)
