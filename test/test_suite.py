from __future__ import unicode_literals, print_function
from nose.tools import assert_equal, assert_true, assert_false
import glob
import json
import mf2py
import os.path
import sys
from test_parser import check_unicode


assert_equal.__self__.maxDiff = None


def test_mf2tests():
    allfiles = glob.glob(
        os.path.join('.', 'testsuite', 'tests', '*', '*', '*.json'))
    for jsonfile in allfiles:
        htmlfile = jsonfile[:-4] + 'html'
        with open(htmlfile) as f:
            p = mf2py.parse(doc=f, url='http://example.com')
            yield check_unicode, htmlfile, p
        with open(jsonfile) as jsonf:
            try:
                s = json.load(jsonf)
            except:
                s = "bad file: " + jsonfile + sys.exc_info()[0]
        yield check_mf2, htmlfile, p, s


def check_mf2(htmlfile, p, s):
    # TODO ignore extra keys in p that are not in s
    assert_equal(p, s)
