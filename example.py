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
    quotes = am_client.get_quotes('/GC,PTN')
    print(quotes[1])
    instrument = am_client.get_instrument('PTN')
    print(instrument)
    instruments = am_client.search_instruments(r'PT.*', 'symbol-regex')
    print(instruments)
    account = am_client.get_account(fields='positions')
    account = am_client.get_linked_accounts(fields='positions')
    print(account)
    price_history = am_client.get_price_history('ptn', frequency='1', start_date=datetime.now()-timedelta(days=30), end_date=datetime.now()-timedelta(days=20))
    #price_history = am_client.get_price_history('ptn', period_type='day', frequency_type='minute', frequency=1)
    print(price_history)
