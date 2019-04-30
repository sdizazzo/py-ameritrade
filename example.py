#!/usr/bin/env python

import sys, os
import logging
from datetime import datetime, timedelta

from pyameritrade.client import Client
from pyameritrade.utils import logger, pp
from pyameritrade.charts.chart import Chart


if __name__ == '__main__':
    #logger.setLevel(logging.DEBUG)

    am_client = Client.from_config('client.config')
    am_client.authenticate()

    movers = am_client.get_movers("$SPX.X", direction='up', change='value')
    for m in movers:
        #m.price_history(period_type='day', period=1, frequency_type='minute', frequency=5)
        off_high = (1 - (m.quote.lastPrice/m.quote._52WkHigh))*100
        above_low = ((m.quote.lastPrice/m.quote._52WkLow)-1)*100
        print("*** Symbol: %s  ***" % m.symbol)
        print("Current price:  %s   52wk HIGH: %s   52wk LOW: %s" % (m.quote.lastPrice, m.quote._52WkHigh, m.quote._52WkLow ))
        print("Off High %.2f%%" % off_high)
        print("Above Low: %.2f%%" % above_low)

    quotes = am_client.get_quotes('/GC,PTN')
    for quote in quotes:
        print(quote)

    instrument = am_client.get_instrument('PTN')

    instruments = am_client.search_instruments(r'XT.*', 'symbol-regex')
    for instrument in instruments:
        instrument.price_history(period_type='day', period=1, frequency_type='minute', frequency=5)

    accounts = am_client.get_linked_accounts(fields='positions')
    print(accounts)

    ph = am_client.get_price_history('$DJI', period_type='year', period=20, frequency_type='daily')
    print(ph)

    # plotly config options
    # https://github.com/plotly/plotly.js/blob/master/src/plot_api/plot_config.js
    Chart(ph,
          style='Scatter',
          simple_averages=(50, 200),
          exp_averages=(50,)
    ).plot(config={'scrollZoom':True},
           offline=True,
           filename='dow_20year.html',
           title='$DJI'
    )

    ph = am_client.get_price_history('aapl', period_type='day', period=1, frequency_type='minute', frequency=5)
    Chart(ph, style='Candlestick').plot(title='AAPL 5 min Candles')

    phs = list()
    for quote in am_client.get_quotes('AAPL,GOOG,MSFT,NFLX,DIS'):
        ph = quote.price_history(period_type='day', period=1, frequency_type='minute', frequency=1)
        phs.append(ph)

    Chart(phs, style='Scatter').plot(title='Compare')
