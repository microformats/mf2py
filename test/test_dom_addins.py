from mf2py.parser import Parser


def test_getElementsByClassName():
    p = Parser(doc=open("test/examples/person_with_url.html"))
    dom = p.__doc__
    assert len(dom.find_all(class_="u-url")) == 1
    expected_el = dom.find_all(class_="u-url")[0]
    assert expected_el["class"] == ["u-url"]
