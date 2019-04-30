#!/usr/bin/env python

import logging
from datetime import datetime

from pyameritrade.utils import pp
from pyameritrade.properties import QuoteProperty, PHMethod

import ujson
import pandas

from plotly import tools
import plotly.plotly as py
import plotly
import plotly.graph_objs as go



class AmeritradeItem():
    logger = logging.getLogger('pyameritrade.Item')

    def __init__(self, json, client):
        self.json = json
        self.client = client

        for k, v in self.json.items():
            #cant begin a variable/attr with a number.
            # ie 52WkHigh
            if isinstance(k, str) and k[0].isdigit():
                k = '_'+k
            setattr(self, k, v)


    def __repr__(self):
        attrs = dict()
        for k, v in self.__dict__.items():
            #Do we want to show None/empty values?
            #if not v or k in ('json', 'client'): continue
            if k in ('json', 'client'): continue
            attrs[k] = v
        return pp.pformat(attrs)



class Describe():
    def __repr__(self):
        return '     [  '+ self.__class__.__name__ +'  ]\n' + AmeritradeItem.__repr__(self)



class Token(AmeritradeItem, Describe):
    logger = logging.getLogger('pyameritrade.Token')

    def __init__(self, json, client):
        AmeritradeItem.__init__(self, json, client)


class Quote(AmeritradeItem, PHMethod, Describe):
    logger = logging.getLogger('pyameritrade.Quote')

    def __init__(self, symbol, json, client):
        AmeritradeItem.__init__(self, json, client)


class Instrument(AmeritradeItem, QuoteProperty, PHMethod, Describe):
    logger = logging.getLogger('pyameritrade.Instrument')

    def __init__(self, json, client):
        AmeritradeItem.__init__(self, json, client)


class Account(AmeritradeItem, Describe):
    logger = logging.getLogger('pyameritrade.Account')

    def __init__(self, account_type, json, client):
        AmeritradeItem.__init__(self, json, client)
        """
            This is going to take much more work to objectify than I'm willing
            to put in at the moment.
        """
        self.account_type = account_type


class Mover(AmeritradeItem, QuoteProperty, PHMethod, Describe):
    logger = logging.getLogger('pyameritrade.Mover')

    def __init__(self, json, client):
        AmeritradeItem.__init__(self, json, client)


class PriceHistory(AmeritradeItem):
    logger = logging.getLogger('pyameritrade.PriceHistory')

    def __init__(self, json, client):
        AmeritradeItem.__init__(self, json, client)

        self.candles = pandas.DataFrame(self.json['candles'])
        for i, candle in self.candles.iterrows():
            self.candles.at[i, 'datetime'] = datetime.utcfromtimestamp(candle['datetime']/1000.0)

    def __repr__(self):
        return '     [  '+ self.__class__.__name__ +'  ]' + "     " + " Symbol: %s\nCandles:\n%s" % (self.symbol, self.candles)

