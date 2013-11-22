import nose
import os.path
from pprint import pprint
from mf2py.parser import Parser

def parse_fixture(path):
    p = Parser(open(os.path.join("test/examples/", path)))
    return p.to_dict()

def test_empty():
   p = Parser() 
   assert type(p) is not None
   assert type(p.to_dict()) is dict

def test_open_file():
   p = Parser(open("test/examples/empty.html"))
   assert p.__doc__ is not None
   assert type(p) is not None
   assert type(p.to_dict()) is dict

def test_user_agent():
    assert Parser.useragent == 'mf2py - microformats2 parser for python'
    Parser.useragent = 'something else'
    assert Parser.useragent == 'something else'
    # set back to default. damn stateful classes
    Parser.useragent = 'mf2py - microformats2 parser for python'
 
def test_base():
    p = Parser(open("test/examples/base.html"))
    assert p.__url__ == u"http://tantek.com/"

def test_simple_parse():
    result = parse_fixture("simple_person_reference.html")
    assert result["items"][0]["properties"] == {u'name': [u'Frances Berriman']}

def test_simple_person_reference_implied():
    p = Parser(open("test/examples/simple_person_reference_implied.html"))
    result = p.to_dict()
    assert result["items"][0]["properties"] == {u'name': [u'Frances Berriman']}

def test_simple_person_reference_same_element():
    result = parse_fixture("simple_person_reference_same_element.html")
    assert result["items"][0]["properties"] == {u'name': [u'Frances Berriman']}

def test_person_with_url():
    p = Parser(open("test/examples/person_with_url.html"))
    result = p.to_dict()
    assert result["items"][0]["properties"]["name"] == [u'Tom Morris']
    assert result["items"][0]["properties"]["url"] == [u'http://tommorris.org/']

def test_multiple_root_classnames():
    result = parse_fixture("nested_multiple_classnames.html")
    # order does not matter
    assert len(result["items"]) == 1
    assert set(result["items"][0]["type"]) == set(["h-entry", "h-as-note"])

def test_property_nested_microformat():
    result = parse_fixture("nested_multiple_classnames.html")
    
    assert len(result["items"]) == 1
    assert "author" in result["items"][0]["properties"]
    assert result["items"][0]["properties"]["author"][0]["properties"]["name"][0] == "Tom Morris"

def test_implied_name():
    result = parse_fixture("implied_properties.html")
    assert result["items"][0]["properties"]["name"][0] == "Tom Morris"

def test_implied_url():
    result = parse_fixture("implied_properties.html")
    assert result["items"][1]["properties"]["url"][0] == "http://tommorris.org/"

def test_implied_nested_photo():
    result = parse_fixture("implied_properties.html")
    assert result["items"][2]["properties"]["photo"][0] == "http://tommorris.org/photo.png"

def test_implied_nested_photo_alt_name():
    result = parse_fixture("implied_properties.html")
    assert result["items"][3]["properties"]["name"][0] == "Tom Morris"

def test_implied_image():
    result = parse_fixture("implied_properties.html")
    assert result["items"][4]["properties"]["photo"][0] == "http://tommorris.org/photo.png"
    assert result["items"][4]["properties"]["name"][0] == "Tom Morris"

if __name__ == '__main__':
    result = parse_fixture("nested_multiple_classnames.html")
    pprint(result)
