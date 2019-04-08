#!/usr/bin/env python

import os
from distutils.core import setup


#this should really be in a if __name__ block
setup(name='pyameritrade',
      version='1.0',
      author='Sean DiZazzo',
      author_email='sean.dizazzo@gmail.com',
      py_modules=['client', 'exception', 'fee',
                  'items', 'response', 'rest_api',
                  'urls'],
      )
