# coding: utf-8

from mf2py.parser import Parser
from nose.tools import assert_equal, assert_true
from pprint import pprint
import os.path
import sys

if sys.version < '3':
    text_type = unicode
    binary_type = str
else:
    text_type = str
    binary_type = bytes


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
                 "2014-01-01T12:00:00+0000")
    assert_equal(result["items"][0]["properties"]["end"][0],
                 "3014-01-01T18:00:00+0000")
    assert_equal(result["items"][0]["properties"]["duration"][0],
                 "P1000Y")
    assert_equal(result["items"][0]["properties"]["updated"][0],
                 "2011-08-26T00:01:21+0000")
    assert_equal(result["items"][0]["properties"]["updated"][1],
                 "2011-08-26T00:01:21+0000")


def test_datetime_vcp_parsing():
    result = parse_fixture("datetimes.html")
    assert_equal(result["items"][1]["properties"]["published"][0],
                 "3014-01-01T01:21:00+0000")
    assert_equal(result["items"][2]["properties"]["updated"][0],
                 "2014-03-11T09:55:00")
    assert_equal(result["items"][3]["properties"]["published"][0],
                 "2014-01-30T15:28:00")
    assert_equal(result["items"][4]["properties"]["published"][0],
                 "9999-01-14T11:52:00+0800")
    assert_equal(result["items"][5]["properties"]["published"][0],
                 "2014-06-01T12:30:00-0600")


def test_dt_end_implied_date():
    """Test that events with dt-start and dt-end use the implied date
    rules http://microformats.org/wiki/value-class-pattern#microformats2_parsers
    for times without dates"""
    result = parse_fixture("datetimes.html")

    event_wo_tz = result["items"][6]
    assert_equal(event_wo_tz["properties"]["start"][0],
                 "2014-05-21T18:30:00")
    assert_equal(event_wo_tz["properties"]["end"][0],
                 "2014-05-21T19:30:00")

    event_w_tz = result["items"][7]
    assert_equal(event_w_tz["properties"]["start"][0],
                 "2014-06-01T12:30:00-0600")
    assert_equal(event_w_tz["properties"]["end"][0],
                 "2014-06-01T19:30:00-0600")


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
    assert_true('h-entry' in result['items'][0]['type'])
    assert_equal('Tom Morris',
                 result['items'][0]['properties']['author'][0]['properties']['name'][0])
    assert_equal('A Title',
                 result['items'][0]['properties']['name'][0])
    assert_equal('Some Content',
                 result['items'][0]['properties']['content'][0]['value'])


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
    assert result["items"][0]["properties"]["name"][0] == "Tom Morris"


def test_template_parse():
    result = parse_fixture("template_tag.html")
    assert len(result["items"]) == 0


def test_backcompat_hproduct():
    result = parse_fixture("backcompat_hproduct.html")
    assert len(result["items"]) == 1
    assert result["items"][0]["type"] == ["h-product"]
    assert result["items"][0]["properties"]["category"] == [u'bullshit']
    assert result["items"][0]["properties"]["brand"] == [u'Quacktastic Products']
    assert result["items"][0]["properties"]["identifier"] == [u'#BULLSHIT-001']
    assert result["items"][0]["properties"]['description'][0] ==  u"Magical tasty sugar pills that don't do anything."
    assert result["items"][0]["properties"]["name"] == [u"Tom's Magical Quack Tincture"]


def test_backcompat_hproduct_nested_hreview():
    result = parse_fixture("backcompat_hproduct_hreview_nested.html")
    assert result["items"][0]["children"][0]['type'] == ['h-review']
    assert type(result["items"][0]["children"][0]['properties']['name'][0]) == text_type


def test_area_uparsing():
    result = parse_fixture("area.html")
    assert result["items"][0]["properties"] == {u'url': [u'http://suda.co.uk'], u'name': [u'Brian Suda']}
    assert 'shape' in result["items"][0].keys()
    assert 'coords' in result["items"][0].keys()


def test_src_equiv():
    result = parse_fixture("test_src_equiv.html")
    for item in result["items"]:
        assert 'x-example' in item['properties'].keys()
        assert u'http://example.org/' == item['properties']['x-example'][0]

def test_rels():
    result = parse_fixture("rel.html")
    assert result['rels'] == {u'in-reply-to': [u'http://example.com/1', u'http://example.com/2'], u'author': [u'http://example.com/a', u'http://example.com/b']}

if __name__ == '__main__':
    result = parse_fixture("nested_multiple_classnames.html")
    pprint(result)
