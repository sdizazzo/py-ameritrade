#!/usr/bin/env python

import sys, os
import logging

import pprint
pp = pprint.PrettyPrinter(indent=4)

import client



if __name__ == '__main__':
    logger = logging.getLogger('ameritrade')
    formatter = logging.Formatter('%(asctime)s - %(name)40s - %(levelname)10s - %(message)s')
    #logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.INFO)

    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)


    CLIENT_ID = 'FF7C19B25AF18'
    REDIRECT_URL = 'https://10.0.1.103'
    REFRESH_TOKEN = 'F3dw4plOC2ChbUuiQFCIyGpVjggIJNfJx8z0xq7UFv5NH/aC0KUUcq23M9mXf866UqmeCmt8g9vglVre+6zWiDkcbR89pst6JO+wrbv1ZYR8uStGIp02bCDa89/T1KNyRy1bhSw0jAuFEeyU6/wmdK1B8GOrR5rF2PNThUn90/tDuJqPBGQdc9TqKp1Hg5pGNTwKsPkbog0BZsdcZhdX/w6LjooiTjW7ux4sAhr3w7JV4QBBqcLwJ+HUEy6jmlGYRSkfZQ1wrDDmj4aDwyC6DV/Ih2Owt4O3AETyJYTBJJEc+MdLI3WYYS7PwnaMdiHu94+v7a20gN9OMVfIwHGKrvCCA87TPBRO13hPGtLXdcK3Tv4yUiJ6tYzIXjmJ5xH4qF4BqAicMrwYrQ0cP471jlwK8033K7GINsCXVztymqwQcPxjrkLOksFDHm5100MQuG4LYrgoVi/JHHvl9H9TDb2kEqCev9akh6Hph9bCdPY1vLnE2pRxk9g/XNYWsXxXFmGUjFU7GhrAkmRtEFPEwGG8x4fLWgT2zBAHGqZ5tg4s7vzDH8ynvksYY7iU3TL6hHJ9esKUaNIHhsRbsPHTUqf+kpJ8w9vfoby2cANXO/qbrQVLxWlFO1hlazCZdJE82vE3bpj3YqvruGtqpopPfAQB6yK/9zIMXaYODkIaMqf4PkOF+h6+22jCWqseG/nwRCxVBSTgfNFczzzE33eGoku89u+jQ9dYLEMrGvBG0w5cy3z9RwMLfjY95u1OOMj0e7nXbrVTr7N8d7ne4EzXSoLXGu/jattWe76qzHmUZdMbKiwfmpYOiE9u+Pap0YBe7hXdPsf7oEUCvcnyb7OPYaxZBmph2Ft/Bl+KO14KnVv24bO4mccCLsP9HcbtcM77EEFG5gA11lk=212FD3x19z9sWBHDJACbC00B75E'
    client = client.AmeritradeClient(CLIENT_ID, REDIRECT_URL, REFRESH_TOKEN)
    resp = client.grant_refresh_token()
    resp = client.get_quote('PTN')
