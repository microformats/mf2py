import nose
from mf2py.parser import Parser

def test_getElementsByClassName():
    p = Parser(open("test/examples/person_with_url.html"))
    dom = p.__doc__
    assert len(dom.documentElement.getElementsByClassName("u-url")) == 1
    expected_el = dom.documentElement.getElementsByClassName("u-url")[0]
    assert expected_el.getAttribute("class") == "u-url"
