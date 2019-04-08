#!/usr/bin/emv python

import logging
import ujson
from json.decoder import JSONDecodeError

import pprint
pp = pprint.PrettyPrinter(indent=4)

class RequestError(Exception):
    logger = logging.getLogger('ameritrade.RequestError')

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

        #TODO clean this up
        try:
            self.message = "Got an error requesting %s\n\n%s\n\nERROR:\n%s\n\nRequest params:\n%s\n\nRequest headers:\n%s" % (url, self.response,  pp.pformat(self.response.json()), request, self.request.headers)
        except JSONDecodeError:
            self.message = "Got an error requesting %s\n\n%s\nERROR:\n%s\n\nRequest params:\n%s" % (url, self.response, pp.pformat(self.response.content), request)

        self.logger.exception(self.message)
        print()
        super().__init__(self, self.response.json())
