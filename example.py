#!/usr/bin/env python

import sys, os
import logging
from datetime import datetime, timedelta

from pyameritrade.client import Client
from pyameritrade.utils import pp, logger

if __name__ == '__main__':
    #logger.setLevel(logging.DEBUG)

    am_client = Client.from_config('client.config')

    #am_client.grant_auth_code()
    movers = am_client.get_movers("$compx", direction='up', change='percent')
    for m in movers:
        print(m)

    quotes = am_client.get_quotes('/GC,PTN')
    for quote in quotes:
        print(quote)

    instrument = am_client.get_instrument('PTN')
    print(instrument)

    instruments = am_client.search_instruments(r'PT.*', 'symbol-regex')
    for instrument in instruments:
        print(instrument)

    account = am_client.get_account(fields='positions')
    pp.pprint(account.json)

    accounts = am_client.get_linked_accounts(fields='positions')
    print(accounts)

    price_history = am_client.get_price_history('ptn', frequency='1', start_date=datetime.now()-timedelta(days=30), end_date=datetime.now()-timedelta(days=20))
    #price_history = am_client.get_price_history('ptn', period_type='day', frequency_type='minute', frequency=1)
    for candle in price_history.candles:
        print(candle)
