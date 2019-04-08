#!/usr/bin/env python

import pprint
pp = pprint.PrettyPrinter(indent=4)


import logging
#perhaps add more complexity as time goes on
logger = logging.getLogger()
formatter = logging.Formatter('%(asctime)s - %(name)30s - %(levelname)10s - %(message)s')
logger.setLevel(logging.INFO)

sh = logging.StreamHandler()
sh.setFormatter(formatter)
logger.addHandler(sh)
