#!/usr/bin/env python

from setuptools import setup
import os.path

ns = {}
with open(os.path.join(os.path.dirname(__file__), 'mf2py/version.py'))\
        as version_file:
    exec(version_file.read(), ns)


setup(name='mf2py',
      version=ns['__version__'],
      description='Python Microformats2 parser',
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      author='Tom Morris',
      author_email='tom@tommorris.org',
      url='http://microformats.org/wiki/mf2py',
      install_requires=[
          # Keep in sync with requirements.txt!
          'html5lib>=1.0.1',
          'requests>=2.18.4',
          'BeautifulSoup4>=4.6.0',
      ],
      tests_require=[
          'lxml',
          'mock',
          'nose',
      ],
      packages=['mf2py'],
      package_data={'mf2py': ['backcompat-rules/*.json']},
      test_suite='nose.collector',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Topic :: Text Processing :: Markup :: HTML'
      ])
