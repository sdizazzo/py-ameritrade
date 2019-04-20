#!/usr/bin/env python

import logging
from datetime import datetime

from pyameritrade.utils import pp

import ujson
import pandas

from plotly import tools
import plotly.plotly
import plotly.graph_objs

class AmeritradeItem():
    logger = logging.getLogger('ameritrade.Item')

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
    logger = logging.getLogger('ameritrade.TokenItem')

    def __init__(self, json, client):
        AmeritradeItem.__init__(self, json, client)

        self.client.access_token = self.access_token


class QuoteItem(AmeritradeItem, ReprMix):
    logger = logging.getLogger('ameritrade.QuoteItem')

    def __init__(self, symbol, json, client):
        AmeritradeItem.__init__(self, json, client)
        #NOTE Am I sure we even need to manually set the symbol like this?
        self.symbol = symbol


class InstrumentItem(AmeritradeItem, ReprMix):
    logger = logging.getLogger('ameritrade.InstrumentItem')

    def __init__(self, json, client):
        AmeritradeItem.__init__(self, json, client)


class AccountItem(AmeritradeItem, ReprMix):
    logger = logging.getLogger('ameritrade.AccountItem')

    def __init__(self, account_type, json, client):
        AmeritradeItem.__init__(self, json, client)
        """
            This is going to take much more work to objectify than I'm willing
            to put in at the moment.
        """
        self.account_type = account_type

class MoverItem(AmeritradeItem, ReprMix):
    logger = logging.getLogger('ameritrade.MoverItem')

    def __init__(self, json, client):
        AmeritradeItem.__init__(self, json, client)


class PriceHistoryItem(AmeritradeItem):
    logger = logging.getLogger('ameritrade.PriceHistoryItem')

    def __init__(self, json, client):
        AmeritradeItem.__init__(self, json, client)

        self.candles = pandas.DataFrame(self.json['candles'])
        for i, candle in self.candles.iterrows():
            self.candles.at[i, 'datetime'] = datetime.utcfromtimestamp(candle['datetime']/1000.0)

    def __repr__(self):
        return '     [  '+ self.__class__.__name__ +'  ]' + "     " + " Symbol: %s\nCandles:\n%s" % (self.symbol, self.candles)



    def generate_graph(self, trace='line', volume=True, filename=None,
                             simple_averages=None, exp_averages=None):

        # I'm not sure this sould be a method on this class, but on a 
        # second layer.  I'm not sure I will ever get to that much detail with this
        # library, though.  It probably should just be an example and left to the
        # user in that case.  Well it is here for now.
        #
        # I'm getting a little lazier now knowing I can't trade gold with this the
        # way I wanted to.

        opens = self.candles['open']
        closes = self.candles['close']
        highs = self.candles['high']
        lows = self.candles['low']
        datetimes = self.candles['datetime']

        if trace.lower() == 'line':
            main_trace = plotly.graph_objs.Scatter(x=datetimes,
                                                   y=closes,
                                                   fill='tozeroy',
                                                   name=self.symbol
                                                  )
        elif trace.lower() == 'candlestick':
            main_trace = plotly.graph_objs.Candlestick(x=datetimes,
                                                       open=opens,
                                                       close=closes,
                                                       high=highs,
                                                       low=lows,
                                                       name=self.symbol
                                                      )
        elif trace.lower() == 'ohlc':
            main_trace = plotly.graph_objs.Ohlc(x=datetimes,
                                                open=opens,
                                                close=closes,
                                                high=highs,
                                                low=lows,
                                                name=self.symbol
                                               )
        else:
            raise TypeError("Unknown trace type '%s'" % trace)

        fig = tools.make_subplots(rows=2, specs=[[{}], [{}]],
                          shared_xaxes=True, shared_yaxes=True,
                          vertical_spacing=0.0001)

        fig.append_trace(main_trace, 1, 1)

        if volume:
            volume_trace = plotly.graph_objs.Bar(x=datetimes,
                                                 y=self.candles['volume'],
                                                 name='Volume',
                                                 yaxis='y2')
            fig.append_trace(volume_trace, 2, 1)

        #Clearly this is getting repetitive
        if simple_averages:
            for average in simple_averages:
                # TODO
                # Since we are calculating these, we should probably add them
                # to the candles dataframe so they could be used again if needed
                #
                sma = closes.rolling(average).mean()
                sma_trace = plotly.graph_objs.Scatter(x=datetimes,
                                                      y=sma,
                                                      name='%s day SMA' % average)
                fig.append_trace(sma_trace, 1, 1)

        if exp_averages:
            for average in exp_averages:
                ema = closes.ewm(span=average).mean()
                ema_trace = plotly.graph_objs.Scatter(x=datetimes,
                                                      y=ema,
                                                      name='%s day EMA' % average)
                fig.append_trace(ema_trace, 1, 1)


        fig['layout'].update(title=self.symbol)
        fig['layout'].update(yaxis=dict(
                                        type='log',
                                        domain=[0.2,1.0],
                                        autorange=True,
                                       )
                            )

        fig['layout'].update(yaxis2=dict(
                             domain=[0.0,0.2])
                            )

        plotly.plotly.plot(fig, filename=filename)


