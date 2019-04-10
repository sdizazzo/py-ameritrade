#!/usr/bin/env python

import logging

class AmeritradeFee():
    logger = logging.getLogger('ameritrade.Fee')
    #https://www.tdameritrade.com/pricing.page
    #Stock commision $6.95
    #ETF commision $0 or $6.95
    #Options $6.95, plus $0.75 per contract
    #Options exercises and assignments $19.99
    #Futures and options on futures $2.25 per contract Plus exchange and regulatory fees

    # NOTE Some fees are variable, so we might want to make them
    # configurable via the config file
    # or perhaps they can be grabbed from the Account object


    ## Futures Options / contract
    ## comission = 2.25
    ## exchange_fee = 1.45
    ## NFA_fee = .02

    # Not sure if this matters or not
    ## TAX_RATE = ??
