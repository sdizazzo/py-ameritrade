#!/usr/bin/emv python

import logging
import ujson
from json.decoder import JSONDecodeError

from pyameritrade.utils import pp

class RequestError(Exception):
    logger = logging.getLogger('pyameritrade.RequestError')

    def __init__(self, url, request, response):
        self.url = url
        self.request = request
        self.response = response

        if self.request.body:
            if self.request.headers['Content-Type'] == 'application/json':
                request = pp.pformat(ujson.loads(self.request.body))
            else:
                request = self.request.body
        else:
            request = None

        #TODO clean this up...seriously
        try:
            self.message = "Got an error requesting %s\n\n%s\n\nERROR:\n%s\n\nRequest params:\n%s\n\nRequest headers:\n%s" % (url, self.response,  pp.pformat(self.response.json()), request, self.request.headers)
            output = self.response.json()
        except JSONDecodeError:
            self.message = "Got an error requesting %s\n\n%s\nERROR:\n%s\n\nRequest params:\n%s" % (url, self.response, self.response.content, request)
            output = self.response.content

        self.logger.exception(self.message)
        print()
        super().__init__(self, pp.pprint(output))
