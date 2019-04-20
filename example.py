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
    #print(accounts)

    #NOTE In order to generate a graph, you must create an account with plot.ly and register an api key
    # see plotly_test.ipynb
    price_history = am_client.get_price_history('$DJI', period_type='year', period=20, frequency_type='daily')
    print(price_history)
    price_history.generate_graph(trace='line', simple_averages=(50, 200), exp_averages=(50,))

    price_history = am_client.get_price_history('aapl', period_type='day', period=1, frequency_type='minute', frequency=5)
    price_history.generate_graph(trace='candlestick', filename='AAPL_daily')

