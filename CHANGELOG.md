# Change Log
All notable changes to this project will be documented in this file.

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
