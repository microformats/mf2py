#!/usr/bin/env python

from setuptools import setup

setup(name='mf2py',
      version='0.1.2',
      description='Python Microformats2 parser',
      author='Tom Morris',
      author_email='tom@tommorris.org',
      url='http://microformats.org/wiki/mf2py',
      install_requires=['html5lib', 'requests'],
      packages=['mf2py'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Programming Language :: Python :: 2.7',
          'Topic :: Text Processing :: Markup :: HTML'
      ]
     )
