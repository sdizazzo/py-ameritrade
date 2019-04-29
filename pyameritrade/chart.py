#!/usr/bin/env python

import logging

from plotly import tools
import plotly.plotly as py
import plotly
import plotly.graph_objs as go


class Chart():
    #
    # Does it make sense to make this a mixin
    # when this is specific to PriceHistory?
    # Is there reason to make any other kind of
    # chart or graph? It might look neat, but
    # is pretty useless for analysis.

    # I really just wanted to move the funcionality 
    # out of the items.py
    #  Maybe that is reason enough.
    #
    logger = logging.getLogger('pyameritrade.Chart')

    def _trace_price(self, style, candles=None):
        if not candles:
            candles = self.candles

        if style == 'Scatter':
            trace = go.Scatter(x=candles['datetime'],
                              # LOLOLOLOLOL
                              # I blame it on the Topamax!
                              y=candles['close'],
                              fill='tozeroy',
                              name=self.symbol,
                             )

        elif style == 'Candlestick':
            trace = go.Candlestick(x=candles['datetime'],
                                   open=candles['open'],
                                   close=candles['close'],
                                   high=candles['high'],
                                   low=candles['low'],
                                   name=self.symbol
                                  )
        elif style == 'Ohlc':
            trace = go.Ohlc(x=candles['datetime'],
                            open=candles['open'],
                            close=candles['close'],
                            high=candles['high'],
                            low=candles['low'],
                            name=self.symbol
                           )
        else:
            raise TypeError("Unhandled style '%s'" % style)

        self.figure.append_trace(trace, 1, 1)


    def _trace_volume(self):
        trace = go.Bar(x=self.candles['datetime'],
                       y=self.candles['volume'],
                       name='Volume',
                       yaxis='y2')
        self.figure.append_trace(trace, 2, 1)


    def _trace_averages(self, type_, averages):
        for average in averages:
            if type_ == 'SMA':
                data = self.candles['close'].rolling(average).mean()
            elif type_ == 'EMA':
                data = self.candles['close'].ewm(span=average).mean()
            else:
                raise TypeError("Unhandled average type: %s" % type_)

            trace = go.Scatter(x=self.candles['datetime'],
                               y=data,
                               name='%s day %s' % (average, type_))
            self.figure.append_trace(trace, 1, 1)


    def _plot(self, offline, config, filename):
        self.figure['layout'].update(title=self.symbol)
        self.figure['layout'].update(yaxis=dict(
                                                type='log',
                                                domain=[0.2,1.0],
                                                autorange=True,
                                               )
                                    )

        self.figure['layout'].update(yaxis2=dict(
                                     domain=[0.0,0.2])
                                     )

        #seems stupid.  I'm tired.
        # .plot() cant handle filename=None
        kwargs = dict(config=config)
        if filename: kwargs.update(filename=filename)

        if offline:
            plotly.offline.plot(self.figure,
                                **kwargs)
        else:
            py.plot(self.figure, **kwargs)


    #
    # Working toward adding several symbols to the same chart
    # perhaps for use with Movers or any other
    #
    # will take some decoupling
    #
    def compare(self, candles):
        self._trace_price('Scatter', candles=candles)


    def generate_chart(self, style='Scatter', filename=None,
                             simple_averages=None, exp_averages=None,
                             offline=True, config={'scrollZoom':True},
                      ):

        self.figure = tools.make_subplots(rows=2, specs=[[{}], [{}]],
                                          shared_xaxes=True, shared_yaxes=True,
                                          vertical_spacing=0.0001
                                         )
        self._trace_price(style)

        self._trace_volume()

        if simple_averages:
            self._trace_averages('SMA', simple_averages)

        if exp_averages:
             self._trace_averages('EMA', exp_averages)

        self._plot(offline, config, filename)

