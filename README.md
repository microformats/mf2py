mf2py
=====

A new Python parser for [microformats 2](http://microformats.org/wiki/Microformats2).

Current status: early alpha - mostly usable. Implements property parsing (except value-class-pattern rules), implied and rels/alternate parsing.

Tom Morris: Please do help work on it. Currently I'm just writing test cases as we
implement stuff and TDDing to completion. Once the parser is stable, I intend
to import one of the full test suites.

Will eventually need good documentation and tidying up.


License: [MIT](http://opensource.org/licenses/mit-license.php)

Install
-------

`pip install mf2py`

Kartik Prabhu: 'this version not on pip'

Usage
-----

Import the parser object using

    from mf2py.parser import Parser

Parse a file containing the content

	file = open('file/content.html','r')
	p = Parser(doc=file)
	file.close()

Parse string containing content

	content = '<article class="h-entry"><h1 class="p-name">Hellow</h1></article>'
	p = Parser(doc=content)

Parse content from a URL

    p = Parser(url="http://tommorris.org/")

Get parsed microformat as python dictionary

	p.to_dict()

Get parsed microformat as JSON output

	p.to_json()

Filter by microformat type

    p.to_dict(filter_by_type="h-entry")
    p.to_json(filter_by_type="h-entry")
