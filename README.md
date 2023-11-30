![mf2py banner](http://microformats.github.io/mf2py/banner.png)

[![version](https://badge.fury.io/py/mf2py.svg?)](https://badge.fury.io/py/mf2py)
[![downloads](https://img.shields.io/pypi/dm/mf2py)](https://pypistats.org/packages/mf2py)
[![license](https://img.shields.io/pypi/l/mf2py?)](https://github.com/microformats/mf2py/blob/main/LICENSE)
[![python-version](https://img.shields.io/pypi/pyversions/mf2py)](https://badge.fury.io/py/mf2py)

## Welcome 👋

`mf2py` is a Python [microformats](https://microformats.org/wiki/microformats) parser with full support for `microformats2` and `microformats1`.

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

### Parse an HTML File

```pycon
>>> with open("example.html", "r") as file:
...     mf2json = mf2py.parse(doc=file)
>>> mf2json
{'items': [{'type': ['h-entry'],
            'properties': {'author': [{'lang': 'en-us',
                                       'properties': {'name': ['James'],
                                                      'url': ['https://example.com/']},
                                       'type': ['h-card'],
                                       'value': 'James'}],
                           'name': ['Excited for the Taylor Swift Eras Tour'],
                           'category': ['music', 'Taylor Swift'],
                           'featured': [{'alt': 'Eras tour poster',
                                         'value': 'https://example.com/eras.jpg'}],
                           'published': ['2023-11-30T19:08:09'],
                           'content': [{'value': 'I can't decide which era is my favorite.',
                                        'lang': 'en-us',
                                        'html': '<p>I can't decide which era is my favorite.</p>'}]},
            'lang': 'en-us'}],
 'rels': {'webmention': ['https://example.com/mentions']},
 'rel-urls': {'https://example.com/mentions': {'rels': ['webmention'],
                                               'text': ''}},
 'debug': {'description': 'mf2py - microformats2 parser for python',
           'source': 'https://github.com/microformats/mf2py',
           'version': '1.1.3',
           'markup parser': 'html5lib'}}

```

### Parse an HTML String

```pycon
>>> content = '<article class="h-entry"><h1 class="p-name">Hello</h1></article>'
>>> mf2py.parse(doc=content)["items"]
[{'type': ['h-entry'], 'properties': {'name': ['Hello']}}]

```

### Parse an HTML Document Retrieved from a URL

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
