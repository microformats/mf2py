# coding: utf-8

from nose.tools import assert_equal, assert_true
import os.path
from pprint import pprint
from mf2py.parser import Parser


def parse_fixture(path):
    p = Parser(doc=open(os.path.join("test/examples/", path)))
    return p.to_dict()


def test_empty():
    p = Parser()
    assert_true(type(p) is not None)
    assert_true(type(p.to_dict()) is dict)


def test_open_file():
    p = Parser(doc=open("test/examples/empty.html"))
    assert_true(p.__doc__ is not None)
    assert_true(type(p) is not None)
    assert_true(type(p.to_dict()) is dict)


def test_user_agent():
    assert_equal(Parser.useragent, 'mf2py - microformats2 parser for python')
    Parser.useragent = 'something else'
    assert_equal(Parser.useragent, 'something else')
    # set back to default. damn stateful classes
    Parser.useragent = 'mf2py - microformats2 parser for python'


def test_base():
    p = Parser(doc=open("test/examples/base.html"))
    assert_equal(p.__url__, u"http://tantek.com/")


def test_simple_parse():
    result = parse_fixture("simple_person_reference.html")
    assert_equal(result["items"][0]["properties"],
                 {u'name': [u'Frances Berriman']})


def test_simple_person_reference_implied():
    p = Parser(doc=open("test/examples/simple_person_reference_implied.html"))
    result = p.to_dict()
    assert_equal(result["items"][0]["properties"],
                 {u'name': [u'Frances Berriman']})


def test_simple_person_reference_same_element():
    result = parse_fixture("simple_person_reference_same_element.html")
    assert_equal(result["items"][0]["properties"],
                 {u'name': [u'Frances Berriman']})


def test_person_with_url():
    p = Parser(doc=open("test/examples/person_with_url.html"))
    result = p.to_dict()
    assert_equal(result["items"][0]["properties"]["name"],
                 [u'Tom Morris'])
    assert_equal(result["items"][0]["properties"]["url"],
                 [u'http://tommorris.org/'])


def test_vcp():
    result = parse_fixture("value_class_person.html")
    assert_equal(result["items"][0]["properties"]["tel"], [u'+44 1234 567890'])


def test_multiple_root_classnames():
    result = parse_fixture("nested_multiple_classnames.html")
    # order does not matter
    assert_equal(len(result["items"]), 1)
    assert_equal(set(result["items"][0]["type"]),
                 set(["h-entry", "h-as-note"]))


def test_property_nested_microformat():
    result = parse_fixture("nested_multiple_classnames.html")

    assert_equal(len(result["items"]), 1)
    assert "author" in result["items"][0]["properties"]
    assert_equal(
        result["items"][0]["properties"]["author"][0]["properties"]["name"][0],
        "Tom Morris")
    assert_equal(
        result["items"][0]["properties"]["reviewer"][0]
        ["properties"]["name"][0],
        "Tom Morris")
    assert_equal(
        result["items"][0]["properties"]["author"][0]
        ["properties"]["adr"][0]["properties"]["city"][0],
        "London")


def test_plain_child_microformat():
    result = parse_fixture("nested_multiple_classnames.html")

    assert_equal(len(result["items"]), 1)
    assert_true("children" in result["items"][0])
    assert_equal(len(result["items"][0]["children"]), 1)
    assert_equal(
        result["items"][0]["children"][0]["properties"]["name"][0],
        "Some Citation")


def test_implied_name():
    result = parse_fixture("implied_properties.html")
    assert_equal(result["items"][0]["properties"]["name"][0], "Tom Morris")


def test_implied_url():
    result = parse_fixture("implied_properties.html")
    assert_equal(result["items"][1]["properties"]["url"][0],
                 "http://tommorris.org/")


def test_implied_nested_photo():
    result = parse_fixture("implied_properties.html")
    assert_equal(result["items"][2]["properties"]["photo"][0],
                 "http://tommorris.org/photo.png")


def test_implied_nested_photo_alt_name():
    result = parse_fixture("implied_properties.html")
    assert_equal(result["items"][3]["properties"]["name"][0], "Tom Morris")


def test_implied_image():
    result = parse_fixture("implied_properties.html")
    assert_equal(result["items"][4]["properties"]["photo"][0],
                 "http://tommorris.org/photo.png")
    assert_equal(result["items"][4]["properties"]["name"][0], "Tom Morris")


def test_datetime_parsing():
    result = parse_fixture("datetimes.html")
    assert_equal(result["items"][0]["properties"]["start"][0],
                 "2014-01-01T12:00:00+00:00")
    assert_equal(result["items"][0]["properties"]["end"][0],
                 "3014-01-01T18:00:00+00:00")
    assert_equal(result["items"][0]["properties"]["duration"][0],
                 "P1000Y")
    assert_equal(result["items"][0]["properties"]["updated"][0],
                 "2011-08-26T00:01:21+00:00")
    assert_equal(result["items"][0]["properties"]["updated"][1],
                 "2011-08-26T00:01:21+00:00")


def test_datetime_vcp_parsing():
    result = parse_fixture("datetimes.html")
    assert_equal(result["items"][1]["properties"]["published"][0],
                 "3014-01-01T01:21+00:00")
    assert_equal(result["items"][2]["properties"]["updated"][0],
                 "2014-03-11T09:55")
    assert_equal(result["items"][3]["properties"]["published"][0],
                 "2014-01-30T15:28")
    assert_equal(result["items"][4]["properties"]["published"][0],
                 "9999-01-14T11:52+08:00")


def test_embedded_parsing():
    result = parse_fixture("embedded.html")
    assert_equal(
        result["items"][0]["properties"]["content"][0]["html"],
        '\n   <p>Blah blah blah blah blah.</p>\n   <p>Blah.</p>\n   <p>Blah blah blah.</p>\n  ')
    assert_equal(
        result["items"][0]["properties"]["content"][0]["value"],
        '\n   Blah blah blah blah blah.\n   Blah.\n   Blah blah blah.\n  ')


def test_backcompat():
    result = parse_fixture("backcompat.html")
    assert_equal(set(result["items"][0]["type"]), set(["h-card"]))


def test_hoisting_nested_hcard():
    result = parse_fixture("nested_hcards.html")
    expected = {
        'items': [
            {
                'properties': {
                    'author': [
                        {
                            'properties': {u'name': [u'KP1']},
                            'type': [u'h-card'],
                            'value': u'KP1'
                        }
                    ],
                    'in-reply-to': [
                        {
                            'properties': {u'name': [u'KP']},
                            'type': [u'h-cite'],
                            'value': u'KP'
                        }
                    ],
                    'name': [u'KP\n    KP1']
                },
                'type': ['h-entry']
            }
        ],
        'rels': {}
    }
    assert_equal([u'KP\n    KP1'], result['items'][0]['properties']['name'])
    assert_equal(expected, result)


def test_html_tag_class():
    result = parse_fixture("hfeed_on_html_tag.html")
    assert_equal([u'h-feed'], result['items'][0]['type'])

    assert_equal([u'entry1'], result['items'][0]['children'][0]['properties']['name'])
    assert_equal([u'entry2'], result['items'][0]['children'][1]['properties']['name'])



def test_string_strip():
    result = parse_fixture("string_stripping.html")
    print result 
    assert result["items"][0]["properties"]["name"][0] == "Tom Morris"

def test_template_parse():
    result = parse_fixture("template_tag.html")
    assert len(result["items"]) == 0

if __name__ == '__main__':
    result = parse_fixture("nested_multiple_classnames.html")
    pprint(result)
