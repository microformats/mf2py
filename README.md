![mf2py banner](http://microformats.github.io/mf2py/banner.png)

[![version](https://badge.fury.io/py/mf2py.svg?)](https://badge.fury.io/py/mf2py)
[![downloads](https://img.shields.io/pypi/dm/mf2py)](https://pypistats.org/packages/mf2py)
[![license](https://img.shields.io/pypi/l/mf2py?)](https://github.com/microformats/mf2py/blob/main/LICENSE)
[![python-version](https://img.shields.io/pypi/pyversions/mf2py)](https://badge.fury.io/py/mf2py)

## Welcome 👋

`mf2py` is a full-featured microformats2 (mf2) parser implemented in Python.

mf2py implements the full mf2 specification, including backward compatibility with microformats1.

## Installation 💻

To install `mf2py`, run the following command:

```bash
pip install mf2py
```

## Quickstart 🚀

Import the parser using:

```pycon
>>> import mf2py

```

### Parse a File

Parse a file containing HTML:

```pycon
>>> with open("example.html", "r") as file:
...     mf2json = mf2py.parse(doc=file)
>>> mf2json
{'items': [{'type': ['h-entry'],
            'properties': {'name': ['Hello'],
                           'content': [{'html': 'Just saying hi.',
                                        'value': 'Just saying hi.'}]}}],
 'rels': {},
 'rel-urls': {},
 'debug': {'description': 'mf2py - microformats2 parser for python',
           'source': 'https://github.com/microformats/mf2py',
           'version': '1.1.3',
           'markup parser': 'html5lib'}}

```

### Parse a String

Parse string containing HTML content:

```pycon
>>> content = '<article class="h-entry"><h1 class="p-name">Hello</h1></article>'
>>> mf2py.parse(doc=content)["items"]
[{'type': ['h-entry'], 'properties': {'name': ['Hello']}}]

```

### Parse an HTML Document Retrieved from a URL

Parse content from a URL:

```pycon
>>> mf2json = mf2py.parse(url="https://indieweb.org")

```

### Extensions

Use `expose_dom=True` to expose the DOM of embedded properties.

### Parser Object

`parse` is a convenience method that actually delegates to
`mf2py.Parser` to do the real work. More sophisticated behaviors are
available by invoking the object directly.

```pycon
>>> p = mf2py.Parser()

```

#### JSON Output

Retrieve parsed microformats as a Python dictionary or JSON string:

```pycon
>>> mf2dict = p.to_dict()
>>> mf2json = p.to_json()

```

#### Filter by Microformat Type

Filter by microformat type.

```pycon
>>> dict_entries = p.to_dict(filter_by_type="h-entry")
>>> json_entries = p.to_json(filter_by_type="h-entry")

```

## Breaking Changes in v2

- img alt support is now on by default

## FAQs ❓

* I passed `mf2py.parse()` a BeautifulSoup document, and it got modified!

Yes, mf2py currently does that. We're working on preventing it! Hopefully soon.

## Testing Environments 🌐

A hosted live version of mf2py can be found at [python.microformats.io](https://python.microformats.io).

## Contributing 🛠️

We welcome contributions and bug reports via Github, and on the microformats wiki.

We to follow the [IndieWebCamp code of conduct](http://indiewebcamp.com/code-of-conduct). Please be respectful of other contributors, and forge a spirit of positive co-operation without discrimination or disrespect.

## License 🧑‍⚖️

`mf2py` is licensed under an MIT License.
