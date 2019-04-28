#!/usr/bin/env python

import sys, os
import logging
from datetime import datetime, timedelta

from pyameritrade.client import Client
from pyameritrade.utils import pp, logger


if __name__ == '__main__':
    #logger.setLevel(logging.DEBUG)

    am_client = Client.from_config('client.config')
    am_client.authenticate()

    movers = am_client.get_movers("$dji", direction='up', change='value')
    for m in movers:
        print(m)
        print("Symbol: %s    Off 52 wk high by: %.2f" % (m.symbol, (m.quote._52WkHigh-m.quote.lastPrice)))

    quotes = am_client.get_quotes('/GC,PTN')
    for quote in quotes:
        print(quote)

    instrument = am_client.get_instrument('PTN')
    print(instrument.price_history(period_type='year', period=1, frequency_type='weekly'))

    instruments = am_client.search_instruments(r'PT.*', 'symbol-regex')
    for instrument in instruments:
        print(instrument)

    accounts = am_client.get_linked_accounts(fields='positions')
    print(accounts)

    price_history = am_client.get_price_history('$DJI', period_type='year', period=20, frequency_type='daily')
    print(price_history)
    # plotly config options
    # https://github.com/plotly/plotly.js/blob/master/src/plot_api/plot_config.js
    price_history.generate_chart(style='Scatter',
                                 simple_averages=(50, 200),
                                 exp_averages=(50,),
                                 config={'scrollZoom':True},
                                 offline=True,
                                 filename='dow_20year.html'
                                )

    price_history = am_client.get_price_history('aapl', period_type='day', period=1, frequency_type='minute', frequency=5)
    price_history.generate_chart(style='Candlestick', offline=True)

