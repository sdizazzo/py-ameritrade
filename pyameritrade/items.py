#!/usr/bin/env python

import logging
from datetime import datetime

from pyameritrade.utils import pp
from pyameritrade.chart import Chart

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
            setattr(self, k, v)


    def __repr__(self):
        # This isn't very useful as is
        desc = "< "
        for k, v in self.__dict__.items():
            if not v or k in ('json', 'client'): continue
            desc += "%s : %s, " % (k, v)
        desc += " >"
        return pp.pformat(desc)


class ReprMix():
    def __repr__(self):
        return '     [  '+ self.__class__.__name__ +'  ]' + "     " + AmeritradeItem.__repr__(self)


class TokenItem(AmeritradeItem, ReprMix):
    logger = logging.getLogger('pyameritrade.TokenItem')

    def __init__(self, json, client):
        AmeritradeItem.__init__(self, json, client)
        #TODO Is this needed anymore?
        self.client.access_token = self.access_token


class QuoteItem(AmeritradeItem, ReprMix):
    logger = logging.getLogger('pyameritrade.QuoteItem')

    def __init__(self, symbol, json, client):
        AmeritradeItem.__init__(self, json, client)
        #NOTE Am I sure we even need to manually set the symbol like this?
        self.symbol = symbol


class InstrumentItem(AmeritradeItem, ReprMix):
    logger = logging.getLogger('pyameritrade.InstrumentItem')

    def __init__(self, json, client):
        AmeritradeItem.__init__(self, json, client)


class AccountItem(AmeritradeItem, ReprMix):
    logger = logging.getLogger('pyameritrade.AccountItem')

    def __init__(self, account_type, json, client):
        AmeritradeItem.__init__(self, json, client)
        """
            This is going to take much more work to objectify than I'm willing
            to put in at the moment.
        """
        self.account_type = account_type


class MoverItem(AmeritradeItem, ReprMix):
    logger = logging.getLogger('pyameritrade.MoverItem')

    def __init__(self, json, client):
        AmeritradeItem.__init__(self, json, client)


class PriceHistoryItem(AmeritradeItem, Chart):
    logger = logging.getLogger('pyameritrade.PriceHistoryItem')

    def __init__(self, json, client):
        AmeritradeItem.__init__(self, json, client)

        self.candles = pandas.DataFrame(self.json['candles'])
        for i, candle in self.candles.iterrows():
            self.candles.at[i, 'datetime'] = datetime.utcfromtimestamp(candle['datetime']/1000.0)

    def __repr__(self):
        return '     [  '+ self.__class__.__name__ +'  ]' + "     " + " Symbol: %s\nCandles:\n%s" % (self.symbol, self.candles)

