#!/usr/bin/env python

import logging

from pyameritrade.utils import pp

class TokenAuthenticator():
    logger = logging.getLogger('ameritrade.TokenAuthenticator')

    def __init__(self, html, client):
        self.html = html
        self.client = client
        #print("SELF.HTML: %s" % pp.pformat(self.html))

    def __repr__(self):
        return pp.pformat(self.html)
