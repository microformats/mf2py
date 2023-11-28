import os
import re
import sys
from unittest import TestCase

import mock
from bs4 import BeautifulSoup

from mf2py.metaformats import parse
from .test_parser import parse_fixture


TEST_DIR = "test/examples/"


def parse_fixture(path):
    with open(os.path.join(TEST_DIR, path)) as f:
        return parse(BeautifulSoup(f.read(), "html5lib"), url="http://tantek.com/")


def test_none():
    result = parse_fixture("base.html")
    assert result is None


def test_ogp():
    result = parse_fixture("metaformats_ogp.html")
    assert result == {
        "type": ["h-entry"],
        "properties": {
            "name": ["Titull foo"],
            "summary": ["Descrypshun bar"],
            "photo": ["http://example.com/baz.jpg"],
            "audio": ["http://example.com/biff.mp3"],
            "video": ["http://example.com/boff.mov"],
            "author": ["http://tantek.com/me"],
            "published": ["2023-01-02T03:04Z"],
            "updated": ["2023-01-02T05:06Z"],
        },
    }
