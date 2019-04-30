#!/usr/bin/env python

import logging

from plotly import tools
import plotly.plotly as py
import plotly
import plotly.graph_objs as go


# plotly config options
# https://github.com/plotly/plotly.js/blob/master/src/plot_api/plot_config.js

class Chart():
    logger = logging.getLogger('pyameritrade.Chart')

    """
        There are so many possibilities for charting, this should
        be factored into a simple base class, with subclasses for
        differnt options and formatting.  Also creating a helpers.py
        with shortcuts to some common configurations.

        Even the large range yaxis makes traces look flat from such
        different data.  Needs a lot of thought to get right.
    """


    def __init__(self, ph, style='Scatter', filename=None,
                 simple_averages=None, exp_averages=None,
                 offline=True, config={'scrollZoom':True},
                ):
        """
            for 'ph' accept a PriceHistory item or any iterable with
            each item having an attached price_history atribute
        """

        self.figure = tools.make_subplots(rows=2, specs=[[{}], [{}]],
                                          shared_xaxes=True, shared_yaxes=True,
                                          vertical_spacing=0.0001
                                         )
        if hasattr(ph, '__iter__'):
            #not quite there yet...
            for i, p in enumerate(ph, 1):
                self._trace_price(i, p, style)
                # need to pass it in with the number of the
                # enumerated index
                yaxis = dict(overlaying='y', side='right')
                kwargs = {'yaxis'+str(i):yaxis}
                self.figure['layout'].update(**kwargs)
        else:
            self._trace_price(1, ph, style)

            # These only make sense if its one symbol
            self._trace_volume(ph)

            if simple_averages:
                self._trace_averages(ph, 'SMA', simple_averages)

            if exp_averages:
                 self._trace_averages(ph, 'EMA', exp_averages)

        self._plot(offline, config, filename)


    def _trace_price(self, yaxis, ph, style):
        if style == 'Scatter':
            trace = go.Scatter(x=ph.candles['datetime'],
                              # LOLOLOLOLOL
                              # I blame it on the Topamax!
                              y=ph.candles['close'],
                              #fill='tozeroy',
                              name=ph.symbol,
                              yaxis='y'+str(yaxis)
                             )

        elif style == 'Candlestick':
            trace = go.Candlestick(x=ph.candles['datetime'],
                                   open=ph.candles['open'],
                                   close=ph.candles['close'],
                                   high=ph.candles['high'],
                                   low=ph.candles['low'],
                                   name=ph.symbol,
                                   yaxis='y'+str(yaxis)
                                  )
        elif style == 'Ohlc':
            trace = go.Ohlc(x=ph.candles['datetime'],
                            open=ph.candles['open'],
                            close=ph.candles['close'],
                            high=ph.candles['high'],
                            low=ph.candles['low'],
                            name=ph.symbol,
                            yaxis='y'+str(yaxis)
                           )
        else:
            raise TypeError("Unhandled style '%s'" % style)

        self.figure.append_trace(trace, 1, 1)


    def _trace_volume(self, ph):
        trace = go.Bar(x=ph.candles['datetime'],
                       y=ph.candles['volume'],
                       name='Volume',
                       yaxis='y2')
        self.figure.append_trace(trace, 2, 1)


    def _trace_averages(self, ph, type_, averages):
        for average in averages:
            if type_ == 'SMA':
                data = ph.candles['close'].rolling(average).mean()
            elif type_ == 'EMA':
                data = ph.candles['close'].ewm(span=average).mean()
            else:
                raise TypeError("Unhandled average type: %s" % type_)

            trace = go.Scatter(x=ph.candles['datetime'],
                               y=data,
                               name='%s day %s' % (average, type_))
            self.figure.append_trace(trace, 1, 1)


    def _plot(self, offline, config, filename):
        # TODO How do you name a chart when there are multiple symbols?
        #self.figure['layout'].update(title=self.symbol)
        self.figure['layout'].update(yaxis=dict(
                                                type='linear',
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

