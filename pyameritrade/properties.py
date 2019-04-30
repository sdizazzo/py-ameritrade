#!/usr/bin/env python


class QuoteProperty():
    # TODO add an issue for caching
    # SUPER simple caching mechanism
    # if this was long livced at all it would
    # get out of sync with the current price
    #
    _quote = None
    def getvalue(self):
        if self._quote:return self._quote
        quote = self.client.get_quotes(self.symbol)[0]
        self._quote = quote
        return quote
    quote = property(getvalue)


class PHMethod():
    # SUPER simple caching mechanism
    # if this was long livced at all it would
    # get out of sync with the current price
    #

    # method acting like a property
    #TODO This is confusing!!!
    candles = None
    def price_history(self, **kwargs):
        if self.candles:return self.candles
        ph = self.client.get_price_history(self.symbol, **kwargs)
        self.candles = ph.candles
        return ph
