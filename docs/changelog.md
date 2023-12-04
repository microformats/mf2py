# Change Log
All notable changes to this project will be documented in this file.

## v2.0.0 - 2023-12-04

The mf2py library is excited to transition into 2.0. This version increase incorporates months of work from contributors, informed by active discussions among implementers and users.

This release officially deprecates support for versions of Python lower than 3.8.

Below are the changes we have made in this release.

## New Features

* Enable img_with_alt by default by @capjamesg in https://github.com/microformats/mf2py/pull/184
* Add timezone offset normalisation by @angelogladding in https://github.com/microformats/mf2py/pull/206
* Add extension to expose DOM for embedded properties by @angelogladding in https://github.com/microformats/mf2py/pull/208
* Add srcset support by @angelogladding in https://github.com/microformats/mf2py/pull/209
* Add language support by @angelogladding in https://github.com/microformats/mf2py/pull/210
* Add extension to support metaformats by @snarfed in https://github.com/microformats/mf2py/pull/213

## Changes

* Remove `img_with_alt` option entirely by @angelogladding in https://github.com/microformats/mf2py/pull/200
* Resolve implied photo relative paths by @angelogladding in https://github.com/microformats/mf2py/pull/205
* Make relative URLs in `e-` properties absolute by @angelogladding in https://github.com/microformats/mf2py/pull/201
* Fix whitespace in plaintext conversion by @angelogladding in https://github.com/microformats/mf2py/pull/207
* Replace `dict_class` with standard `dict` by @angelogladding in https://github.com/microformats/mf2py/pull/196

## Tests, Library and Documentation Maintenance

* Update tests to include alt texts by default by @angelogladding in https://github.com/microformats/mf2py/pull/190
* Add Windows and macOS tests by @capjamesg in https://github.com/microformats/mf2py/pull/198
* Use poetry for dependency management by @angelogladding in https://github.com/microformats/mf2py/pull/189
* Deprecate Python 2 support by @angelogladding in https://github.com/microformats/mf2py/pull/179
* Code linted with `black` and `isort` by @capjamesg 
* Bump requests from 2.21.0 to 2.31.0 by @dependabot in https://github.com/microformats/mf2py/pull/185
* Add linting CI actions by @capjamesg in https://github.com/microformats/mf2py/pull/193
* Move from nose2 to pytest by @capjamesg in https://github.com/microformats/mf2py/pull/186
* Switch from nosetests to pytest by @angelogladding in https://github.com/microformats/mf2py/pull/178
* Add 3.11, 3.12 and drop pypy from test matrix; upgrade poetry action by @angelogladding in https://github.com/microformats/mf2py/pull/204
* Prepare tests to test extensions by @angelogladding in https://github.com/microformats/mf2py/pull/214
* Bring README doctests up-to-date by @angelogladding in https://github.com/microformats/mf2py/pull/215
* Update README by @angelogladding in https://github.com/microformats/mf2py/pull/216
* Fix tests/doctests by @angelogladding in https://github.com/microformats/mf2py/pull/217

**Full Changelog**: https://github.com/microformats/mf2py/compare/v1.1.3...v2.0.0

## 1.1.3 - 2022-06-28
- reduce instances where photo is implied (#135)
- always do relative URL resolution (#138)
- VCP now handles tz offsets without leading zeros (#142)
- implement id parsing (#143)
- fix outdated syntax causing SyntaxWarning (#157)

## 1.1.2 - 2018-08-08
- add parsing for iframe.u-*[src] (#116)
- bug fix: reduced implied urls (#117)
- bug fix: don't collapse whitespace between tags
- specify explicit versions for dependencies
- revert BeautifulSoup copying added in 1.1.1 due to bugs (eg #108)
- misc performance improvements

## 1.1.1 - 2018-06-15

- streamline backcompat to use JSON only.
- fix multiple mf1 root rel-tag parsing 
- correct url and photo for hreview.
- add rules for nested hreview. update backcompat to use multiple matches in old properties.
- fix `rel-tag` to `p-category` conversion so that other classes are not lost.
- use original authored html for `e-*` parsing in backcompat
- make classes and rels into unordered (alphabetically ordered) deduped arrays.
- only use class names for mf2 which follow the naming rules
- fix `parse` method to use default html parser.
- always use the first value for attributes for rels.
- correct AM/PM conversion in datetime value class pattern.
 - add ordinal date parsing to datetimes value class pattern. ordinal date is normalised to YYYY-MM-DD
- remove hack for html tag classes since that is fixed in new BS
- better whitespace algorithm for `name` and `html.value` parsing
- experimental flag for including `alt` in `u-photo` parsing
- make a copy of the BeautifulSoup given by user to work on for parsing to prevent changes to original doc
- bump version to 1.1.1 

## 1.1.0 - 2018-03-16

- bump version to 1.1.0 since it is a "major" change 
- added tests for new implied name rules
- modified earlier tests to accommodate new rules
- use space separator instead of "T"
- Don't add "00" seconds unless authored
- use TZ authored in separate `value` element
- only use first found `value` of a particular type `date`, `time`, or `timezone`.
- move backcompat rules into JSON files
- reorganise value class pattern parsing into new files
- add datetime_helpers to organise datetime parsing rules
- reorganise tests
- remove Heroku frontend, point to mf2py-web and python.microformats.io instead in README.
- remove Flask and gunicorn requirements
- add debug info with description, version, url and the html parser used 

## 1.0.6 - 2018-03-04

- strip leading/trailing white space for `e-*[html]`. update the corresponding tests
- blank values explicitly authored are allowed as property values 
- include `alt` or `src` from `<img>` in parsing for `p-*` and `e-*[value]`
- parse `title` from `<link>` for `p-*` resolves #84 
- and `poster` from `<video>` for `u-*` resolves #76 
- use `html5lib` as default parser
- use the final redirect URL resolves #62 
- update requirements to use BS4 v4.6.0 and html5lib v1.0.1
- drop support for Python 2.6 as html5lib dropped support

## 1.0.5 - 2016-05-09

- Implied property checks now ignore alt="", treating it the same as
  if no alt value is defined.
- Support for using a custom dict implementation by setting
  mf2py.Parser.dict_class. collections.OrderedDict yields much nicer
  output for hosted parsers.

## 1.0.4 - 2016-03-21
### Changed
- Performance improvement changing simple calls to soup.find_all to
  a manual iteration over .contents.

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
