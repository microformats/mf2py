# Home

![mf2py banner](banner.png)

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

```python
import mf2py
```

### Parse a File

Parse a file containing HTML:

```python
with open('file/content.html','r') as file:
    obj = mf2py.parse(doc=file)
```

### Parse a String

Parse string containing HTML content:

```python
content = '<article class="h-entry"><h1 class="p-name">Hello</h1></article>'
obj = mf2py.parse(doc=content)
```

### Parse a HTML Document Retrieved from a URL

Parse content from a URL:

```python
obj = mf2py.parse(url="http://tommorris.org/")
```

`parse` is a convenience method that actually delegates to
`mf2py.Parser` to do the real work. More sophisticated behaviors are
available by invoking the object directly.

### Format Options

Retrieve parsed microformats as a Python dictionary or JSON string:

```python
p = mf2py.Parser(...)
p.to_dict()  # returns a python dictionary
p.to_json()  # returns a JSON string
```

### Filter by Microformat Type

Filter by microformat type:

```python
p.to_dict(filter_by_type="h-entry")
p.to_json(filter_by_type="h-entry")
```

## Experimental Features 🧪

- Pass the optional argument `img_with_alt=True` to either the `Parser` object or to the `parse` method to enable parsing of the `alt` attribute of `<img>` tags according to [issue: image alt text is lost during parsing](https://github.com/microformats/microformats2-parsing/issues/2). By default this is `False` to be backwards compatible.

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