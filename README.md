mf2py
=====

[![Build Status](https://travis-ci.org/microformats/mf2py.svg?branch=master)](https://travis-ci.org/microformats/mf2py)

Python parser for [microformats 2](http://microformats.org/wiki/Microformats2).

Current status: Full-featured and mostly stable. Implements the full
mf2 spec, including backward compatibility with microformats1.

Documentation, code tidying and so on is rather lacking.    

License: [MIT](http://opensource.org/licenses/mit-license.php)

Install
-------

`pip install mf2py`

Usage
-----

Import the parser using

    import mf2py

Parse a file containing the content

    with open('file/content.html','r') as file:
        obj = mf2py.parse(doc=file)

Parse string containing content

    content = '<article class="h-entry"><h1 class="p-name">Hello</h1></article>'
    obj = mf2py.parse(doc=content)

Parse content from a URL

    obj = mf2py.parse(url="http://tommorris.org/")

`parse` is a convenience method that actually delegates to
`mf2py.Parser` to do the real work. More sophisticated behaviors are
available by invoking the object directly.

Get parsed microformat in a variety of formats

    p = mf2py.Parser(...)
    p.to_dict()  # returns a python dictionary
    p.to_json()  # returns a JSON string

Filter by microformat type

    p.to_dict(filter_by_type="h-entry")
    p.to_json(filter_by_type="h-entry")

Experimental features
---------------------
- pass the optional argument `img_with_alt=True` to either the `Parser` object or to the `parse` method to enable parsing of the `alt` attribute of `<img>` tags according to [issue: image alt text is lost during parsing](https://github.com/microformats/microformats2-parsing/issues/2). By default this is `False` to be backwards compatible.

FAQ
---

* I passed `mf2py.parse()` a BeautifulSoup document, and it got modified!

Yes, mf2py currently does that. We're working on preventing it! Hopefully soon.

Frontends
-------------

A basic web interface for mf2py and [mf2util](https://github.com/kylewm/mf2util) is available at [mf2py-web](https://github.com/kylewm/mf2py-web).

A hosted live version can be found at [python.microformats.io](https://python.microformats.io).

Contributions
-------------

We welcome contributions and bug reports via Github, and on the microformats wiki.

We try to follow the [IndieWebCamp code of conduct](http://indiewebcamp.com/code-of-conduct). Please be respectful of other contributors, and forge a spirit of positive co-operation without discrimination or disrespect.

