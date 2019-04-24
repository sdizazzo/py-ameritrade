#!/usr/bin/env python

import logging

from plotly import tools
import plotly.plotly as py
import plotly
import plotly.graph_objs as go


class Chart():
    logger = logging.getLogger('pyameritrade.Chart')

    def _trace_price(self, style):
        if style == 'Scatter':
            s_trace= go.Scatter(x=self.candles['datetime'],
                                y=['close'],
                                fill='tozeroy',
                                name=self.symbol
                               )
            self.figure.append_trace(s_trace, 1, 1)

        elif style == 'Candlestick':
            c_trace = go.Candlestick(x=self.candles['datetime'],
                                     open=self.candles['open'],
                                     close=self.candles['close'],
                                     high=self.candles['high'],
                                     low=self.candles['low'],
                                     name=self.symbol
                                    )
            self.figure.append_trace(c_trace, 1, 1)

        elif style == 'Ohlc':
            o_trace = go.Ohlc(x=self.candles['datetime'],
                              open=self.candles['open'],
                              close=self.candles['close'],
                              high=self.candles['high'],
                              low=self.candles['low'],
                              name=self.symbol
                             )
            self.figure.append_trace(o_trace, 1, 1)

        else:
            raise TypeError("Unhandled style '%s'" % style)


    def _trace_volume(self):
        v_trace = go.Bar(x=self.candles['datetime'],
                         y=self.candles['volume'],
                         name='Volume',
                         yaxis='y2')
        self.figure.append_trace(v_trace, 2, 1)


    def _trace_averages(self, type_, averages):
        for average in averages:
            if type_ == 'SMA':
                data = self.candles['close'].rolling(average).mean()
            elif type_ == 'EMA':
                data = self.candles['close'].ewm(span=average).mean()
            else:
                raise TypeError("Unhandled average type: %s" % type_)

            avg_trace = go.Scatter(x=self.candles['datetime'],
                                   y=data,
                                   name='%s day %s' % (average, type_))
            self.figure.append_trace(avg_trace, 1, 1)


    def _plot(self, offline, config):
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
        if offline:
            plotly.offline.plot(self.figure, config=config)
        else:
            py.plot(self.figure)


    def generate_chart(self, style='Scatter', filename=None,
                             simple_averages=None, exp_averages=None,
                             offline=True, config={'scrollZoom':True}):

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

        self._plot(offline, config)

