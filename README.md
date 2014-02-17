mf2py
=====

A new Python parser for [microformats 2](http://microformats.org/wiki/Microformats2).

Current status: very early alpha - a long way from usable. Implements only p-
and u- property parsing and no implied or rel/alternates parsing, nor does it
yet support child microformats or legacy backcompat.

Please do help work on it. Currently I'm just writing test cases as we
implement stuff and TDDing to completion. Once the parser is stable, I intend
to import one of the full test suites.

Will eventually need good documentation and tidying up.


License: [MIT](http://opensource.org/licenses/mit-license.php)

Install
-------

`pip install mf2py`

Usage
-----

    from mf2py.parser import Parser
    tom = Parser(url="http://tommorris.org/")
    tom.filter_by_type("h-card")

