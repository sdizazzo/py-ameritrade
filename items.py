#!/usr/bin/env python

import logging

import pprint
pp = pprint.PrettyPrinter(indent=4)

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


class TokenItem(AmeritradeItem):
    logger = logging.getLogger('ameritrade.TokenItem')

    """
    {
        "access_token": "string",
        "refresh_token": "string",
        "token_type": "string",
        "expires_in": 0,
        "scope": "string",
        "refresh_token_expires_in": 0
    }
    """

    def __init__(self, json, client):
        AmeritradeItem.__init__(self, json, client)

        self.client.access_token = self.access_token

    def __repr__(self):
        return '     [  '+ self.__class__.__name__ +'  ]' + "     " + AmeritradeItem.__repr__(self)


class QuoteItem(AmeritradeItem):
    logger = logging.getLogger('ameritrade.QuoteItem')

    def __init__(self, symbol, json, client):
        AmeritradeItem.__init__(self, json, client)

        self.symbol = symbol


    #TODO Shouldn't have to repeat this on each subclass
    def __repr__(self):
        return '     [  '+ self.__class__.__name__ +'  ]' + "     " + AmeritradeItem.__repr__(self)


class InstrumentItem(AmeritradeItem):
    logger = logging.getLogger('ameritrade.InstrumentItem')

    def __init__(self, json, client):
        AmeritradeItem.__init__(self, json, client)

    #TODO Shouldn't have to repeat this on each subclass
    def __repr__(self):
        return '     [  '+ self.__class__.__name__ +'  ]' + "     " + AmeritradeItem.__repr__(self)


class AccountItem(AmeritradeItem):
    logger = logging.getLogger('ameritrade.AccountItem')

    def __init__(self, json, client):
        AmeritradeItem.__init__(self, json, client)

    #TODO Shouldn't have to repeat this on each subclass
    def __repr__(self):
        return '     [  '+ self.__class__.__name__ +'  ]' + "     " + AmeritradeItem.__repr__(self)


class PriceHistoryItem(AmeritradeItem):
    logger = logging.getLogger('ameritrade.PriceHistoryItem')

    def __init__(self, json, client):
        AmeritradeItem.__init__(self, json, client)

    #TODO Shouldn't have to repeat this on each subclass
    def __repr__(self):
        return '     [  '+ self.__class__.__name__ +'  ]' + "     " + AmeritradeItem.__repr__(self)



