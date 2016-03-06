# Change Log
All notable changes to this project will be documented in this file.

## 1.0.3 - 2016-02-05
### Changed
- Performance improvement by limiting number of calls to soup.find_all
  in backcompat module. Should not be any functional changes.

## 1.0.2 - 2016-01-26
### Added
- Backward compatibility parsing for rel=tag properties. These are now converted
  to p-category based on the last path segment of the tag URI as spec'd in
  http://microformats.org/wiki/h-entry#Parser_Compatibility
- Optional property html_parser to specify the html parser that BeautifulSoup
  should use (e.g., "lxml" or "html5lib")

## 1.0.1 - 2015-12-11
### Changed
- `u-*` properties are now parsed from `<link>` elements per the updated spec
  http://microformats.org/wiki/microformats2-parsing-issues#link_elements_and_u-_parsing

## 1.0.0 - 2015-10-05
### Changed
- Version number bumped to 1.0.0 following community discussion.

## 0.2.8 - 2015-09-21
### Changed
- Stricter checks that Parser.__init__ params are actually None before
  ignoring them.

## 0.2.7 - 2015-08-03
### Changed
- Now produces unicode strings for every key and value, no more byte
  strings anywhere.
- Do not add 'T' between date and time when normalizing dates
### Added
- Unit tests for running the microformats test suite

## 0.2.6 - 2015-05-06
### Added
- New top-level "rel-urls" entry, contains rich data parsed from rel
  links, organized by URL.

## 0.2.5 - 2015-03-01
### Added
- convenience method `mf2py.parse` that takes the same arguments as Parser
  and returns a dict.
### Changed
- nested h-* classes now parse their "value" based on the property
  they represent (p-*, u-*, dt-*), so for example "p-in-reply-to
  h-cite" would have a name as its value and "u-in-reply-to h-cite"
  will have a URL.

## 0.2.4 - 2015-02-13
### Added
- Add rel=bookmark to backward compat parsing rules based (translated
  to u-url in mf2)
### Changed
- Parser constructor now takes explicit named arguments instead of
  **kwargs, for saner behavior when called with unnamed arguments.
- Bugfix: Empty href="" attributes are now properly interpreted as
  the current document's URL.

## 0.2.3 - 2015-02-07
### Changed
- Minor Py3 compatibility fix
- Correct typo `test_requires` -> `tests_require` in setup.py

## 0.2.2 - 2015-02-05
### Changed
- Started keeping a changelog!
- Use a better method for extracting HTML for an e-* property
- Correct BeautifulSoup4 dependency in setup.py to fix error with
  installation from PyPI.
- Buffed up docstrings for public methods.
