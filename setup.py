#!/usr/bin/env python

import os
from distutils.core import setup


setup(name='pyameritrade',
      version=None,
      author='Sean DiZazzo',
      author_email='sean.dizazzo@gmail.com',
      packages=['pyameritrade'],
      license='MIT',
      python_requires='>=3.6.0',
      install_requires=[
            'requests',
            'ujson',
            'pandas',
            'plotly'
            ]
      )
