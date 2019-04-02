#!/usr/bin/env python

import sys, os
import logging
from datetime import datetime, timedelta
import pprint
pp = pprint.PrettyPrinter(indent=4)

from ameritrade_client import AmeritradeClient

import urllib.parse

if __name__ == '__main__':
    logger = logging.getLogger('ameritrade')
    formatter = logging.Formatter('%(asctime)s - %(name)30s - %(levelname)10s - %(message)s')
    #logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.INFO)

    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)


    client = AmeritradeClient.from_config('client.config')
    resp = client.grant_refresh_token()
    #resp = client.get_quote('/GC,/GCM19')
    #resp = client.get_instrument('OGM19')
    #resp = client.search_instruments(r'/G.*', 'symbol-regex')
    #resp = client.get_account(fields='positions')
    resp = client.get_price_history('ptn', frequency='1', start_date=datetime.now()-timedelta(days=30), end_date=datetime.now()-timedelta(days=20))
    #resp = client.get_price_history('ptn', period_type='day', frequency_type='minute', frequency=30)
