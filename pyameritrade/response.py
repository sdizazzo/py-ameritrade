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

        elif url == (URLs.GET_ACCOUNT.value, URLs.GET_LINKED_ACCOUNTS.value):
            #This needs to look for multiple items and split them out
            return AccountItem(json, client)

        elif url == URLs.PRICE_HISTORY.value:
            return PriceHistoryItem(json, client)
