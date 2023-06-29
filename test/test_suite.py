import glob
import json
import os.path
import sys

from test_parser import check_unicode

import mf2py


def test_mf2tests():
    allfiles = glob.glob(os.path.join(".", "testsuite", "tests", "*", "*", "*.json"))
    for jsonfile in allfiles:
        htmlfile = jsonfile[:-4] + "html"
        with open(htmlfile) as f:
            p = mf2py.parse(doc=f, url="http://example.com")
            check_unicode(htmlfile, p)
        with open(jsonfile) as jsonf:
            try:
                s = json.load(jsonf)
            except:
                s = "bad file: " + jsonfile + sys.exc_info()[0]
        check_mf2(htmlfile, p, s)


def check_mf2(htmlfile, p, s):
    # TODO ignore extra keys in p that are not in s
    assert p == s
