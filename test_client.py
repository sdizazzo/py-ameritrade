#!/usr/bin/env python

import sys, os
import logging

import pprint
pp = pprint.PrettyPrinter(indent=4)

from ameritrade_client import AmeritradeClient



if __name__ == '__main__':
    logger = logging.getLogger('ameritrade')
    formatter = logging.Formatter('%(asctime)s - %(name)40s - %(levelname)10s - %(message)s')
    #logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.INFO)

    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)


    client = AmeritradeClient.from_config('client.config')
    resp = client.grant_refresh_token()
    #resp = client.get_quote('GCM19')
    #resp = client.get_instrument('GC')
    #resp = client.search_instruments('.*GC', 'symbol-regex')
    resp = client.get_account(fields='positions,orders')
