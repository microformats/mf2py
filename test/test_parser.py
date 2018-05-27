from __future__ import unicode_literals, print_function

import os
import re
import sys

import mock
from nose.tools import assert_equal, assert_true, assert_false
from mf2py import Parser
from bs4 import BeautifulSoup
from unittest import TestCase

TestCase.maxDiff = None


if sys.version < '3':
    text_type = unicode
    binary_type = str
else:
    text_type = str
    binary_type = bytes

TEST_DIR = 'test/examples/'

def parse_fixture(path, url=None):
    with open(os.path.join(TEST_DIR, path)) as f:
        p = Parser(doc=f, url=url, html_parser='html5lib')
        return p.to_dict()


def test_empty():
    p = Parser()
    assert_true(type(p) is not None)
    assert_true(type(p.to_dict()) is dict)


def test_open_file():
    with open(os.path.join(TEST_DIR, 'empty.html')) as f:
        p = Parser(doc=f)

    assert_true(p.__doc__ is not None)
    assert_true(type(p) is not None)
    assert_true(type(p.to_dict()) is dict)

def test_doc_tag():
    # test that strings, BS doc and BS tags are all parsed and in the latter cases copies are made but are the same stuff
    doc = '''<article class="h-entry"></article>'''
    soup = BeautifulSoup(doc)

    parse_string = Parser(doc).to_dict()
    assert_true('h-entry' in parse_string['items'][0]['type'])

    p = Parser(soup)
    assert_true('h-entry' in p.to_dict()['items'][0]['type'])
    assert_false(soup is p.__doc__)
    assert_true(soup == p.__doc__)

    p = Parser(soup.article)
    assert_true('h-entry' in p.to_dict()['items'][0]['type'])
    assert_false(soup.article is p.__doc__)
    assert_true(soup.article == p.__doc__)

@mock.patch('requests.get')
def test_user_agent(getter):
    ua_expect = 'mf2py - microformats2 parser for python'
    assert_true(Parser.useragent.startswith(ua_expect))

    resp = mock.MagicMock()
    resp.content = b''
    resp.text = ''
    resp.headers = {}
    getter.return_value = resp

    Parser(url='http://example.com')
    getter.assert_called_with('http://example.com', headers={
        'User-Agent': Parser.useragent
    })

    Parser.useragent = 'something else'
    assert_equal(Parser.useragent, 'something else')
    # set back to default. damn stateful classes
    Parser.useragent = 'mf2py - microformats2 parser for python'


def test_base():
    with open(os.path.join(TEST_DIR, 'base.html')) as f:
        p = Parser(doc=f)

    assert_equal(p.__url__, "http://tantek.com/")


def test_simple_parse():
    result = parse_fixture("simple_person_reference.html")
    assert_equal(result["items"][0]["properties"],
                 {'name': ['Frances Berriman']})


def test_simple_person_reference_same_element():
    result = parse_fixture("simple_person_reference_same_element.html")
    assert_equal(result["items"][0]["properties"],
                 {'name': ['Frances Berriman']})


def test_person_with_url():
    result = parse_fixture("person_with_url.html")
    assert_equal(result["items"][0]["properties"]["name"],
                 ['Tom Morris'])
    assert_equal(result["items"][0]["properties"]["url"],
                 ['http://tommorris.org/'])


def test_vcp():
    result = parse_fixture("value_class_person.html")
    assert_equal(result["items"][0]["properties"]["tel"], ['+44 1234 567890'])


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
                 "3014-01-01 01:21Z")
    assert_equal(result["items"][2]["properties"]["updated"][0],
                 "2014-03-11 09:55")
    assert_equal(result["items"][3]["properties"]["published"][0],
                 "2014-01-30 15:28")
    assert_equal(result["items"][4]["properties"]["published"][0],
                 "9999-01-14T11:52+08:00")
    assert_equal(result["items"][5]["properties"]["published"][0],
                 "2014-06-01 12:30-06:00")
    assert_equal(result["items"][8]["properties"]["start"][0],
                 "2014-06-01 12:30-06:00")
    assert_equal(result["items"][9]["properties"]["start"][0],
                 "2014-06-01 12:30-06:00")
    assert_equal(result["items"][10]["properties"]["start"][0],
                 "2014-06-01 00:30-06:00")
    assert_equal(result["items"][10]["properties"]["end"][0],
                 "2014-06-01 12:15")
    assert_equal(result["items"][10]["properties"]["start"][1],
                 "2014-06-01 00:30-06:00")
    assert_equal(result["items"][10]["properties"]["end"][1],
                 "2014-06-01 12:15")
    assert_equal(result["items"][11]["properties"]["start"][0],
                 "2016-03-02 00:30-06:00")

def test_dt_end_implied_date():
    """Test that events with dt-start and dt-end use the implied date rule
    http://microformats.org/wiki/value-class-pattern#microformats2_parsers
    for times without dates"""
    result = parse_fixture("datetimes.html")

    event_wo_tz = result["items"][6]
    assert_equal(event_wo_tz["properties"]["start"][0],
                 "2014-05-21 18:30")
    assert_equal(event_wo_tz["properties"]["end"][0],
                 "2014-05-21 19:30")

    event_w_tz = result["items"][7]
    assert_equal(event_w_tz["properties"]["start"][0],
                 "2014-06-01 12:30-06:00")
    assert_equal(event_w_tz["properties"]["end"][0],
                 "2014-06-01 19:30-06:00")



def test_embedded_parsing():
    result = parse_fixture("embedded.html")
    assert_equal(
        result["items"][0]["properties"]["content"][0]["html"],
        '<p>Blah blah blah blah blah.</p>\n' +
        '   <p>Blah.</p>\n   <p>Blah blah blah.</p>')
    assert_equal(
        result["items"][0]["properties"]["content"][0]["value"],
        'Blah blah blah blah blah.\nBlah.\nBlah blah blah.')


def test_hoisting_nested_hcard():
    result = parse_fixture("nested_hcards.html")
    expected = [
            {
                'properties': {
                    'author': [
                        {
                            'properties': {'name': ['KP1']},
                            'type': ['h-card'],
                            'value': 'KP1'
                        }
                    ],
                    'in-reply-to': [
                        {
                            'properties': {'name': ['KP']},
                            'type': ['h-cite'],
                            'value': 'KP'
                        }
                    ],
                },
                'type': ['h-entry']
            }
        ]
    assert_equal(expected, result['items'])


def test_html_tag_class():
    result = parse_fixture("hfeed_on_html_tag.html")
    assert_equal(['h-feed'], result['items'][0]['type'])

    assert_equal(['entry1'], result['items'][0]['children'][0]
                 ['properties']['name'])
    assert_equal(['entry2'], result['items'][0]['children'][1]
                 ['properties']['name'])


def test_string_strip():
    result = parse_fixture("string_stripping.html")
    assert_equal('Tom Morris', result["items"][0]["properties"]["name"][0])


def test_template_parse():
    result = parse_fixture("template_tag.html")
    assert_equal(0, len(result["items"]))

def test_ordering_dedup():
    ''' test that classes are dedeuped and alphabetically ordered '''

    result = parse_fixture("ordering_dedup.html")
    item = result['items'][0]
    assert_equal(['h-entry', 'h-feed', 'h-product', 'h-x-test'], item['type'])
    assert_equal(['example.com', 'example.com/2'], item['properties']['url'])
    assert_equal(['name', 'URL name'], item['properties']['name'])
    assert_equal(['author', 'bookmark', 'me'], result['rel-urls']['example.com/rel']['rels'])
    assert_equal('de', result['rel-urls']['example.com/lang']['hreflang'])

def test_class_names_format():
    ''' test that only classes with letters and possibly numbers in the vendor prefix part are used '''

    result = parse_fixture("class_names_format.html")
    item = result['items'][0]
    assert_equal(['h-feed', 'h-p3k-entry', 'h-x-test'], item['type'])
    assert 'url' in item['properties']
    assert 'p3k-url' in item['properties']
    assert 'Url' not in item['properties']
    assert '-url' not in item['properties']
    assert 'url-' not in item['properties']

    assert 'name' in item['properties']
    assert 'p3k-name' in item['properties']
    assert 'nAme' not in item['properties']
    assert '-name' not in item['properties']
    assert 'name-' not in item['properties']

def test_area_uparsing():
    result = parse_fixture("area.html")
    assert_equal({
        'url': ['http://suda.co.uk'], 'name': ['Brian Suda']}, result["items"][0]["properties"])
    assert 'shape' in result["items"][0]
    assert 'coords' in result["items"][0]


def test_src_equiv():
    result = parse_fixture("test_src_equiv.html")
    for item in result["items"]:
        assert 'x-example' in item['properties']
        assert_equal('http://example.org/', item['properties']['x-example'][0])


def test_rels():
    result = parse_fixture("rel.html")
    assert_equal({
        u'in-reply-to': [u'http://example.com/1', u'http://example.com/2'],
        u'author': [u'http://example.com/a', u'http://example.com/b'],
        u'alternate': [u'http://example.com/fr'],
        u'home': [u'http://example.com/fr'],
    }, result['rels'])
    assert_equal({
        u'http://example.com/1': {'text': u"post 1", "rels": [u'in-reply-to']},
        u'http://example.com/2': {'text': u"post 2", "rels": [u'in-reply-to']},
        u'http://example.com/a': {'text': u"author a", "rels": [u'author']},
        u'http://example.com/b': {'text': u"author b", "rels": [u'author']},
        u'http://example.com/fr': {'text': u'French mobile homepage',
                                   u'media': u'handheld',
                                   u'rels': [u'alternate', u'home'],
                                   u'hreflang': u'fr'}
    }, result['rel-urls'])


def test_alternates():
    result = parse_fixture("rel.html")
    assert_equal([{
        'url': 'http://example.com/fr', 'media': 'handheld',
        'text': 'French mobile homepage',
        'rel': 'home', 'hreflang': 'fr'
    }], result['alternates'])


def test_enclosures():
    result = parse_fixture("rel_enclosure.html")
    assert_equal({'enclosure': ['http://example.com/movie.mp4']}, result['rels'])
    assert_equal({'http://example.com/movie.mp4': {
        'rels': ['enclosure'],
        'text': 'my movie',
        'type': 'video/mpeg'}
    }, result['rel-urls'])


def test_empty_href():
    result = parse_fixture("hcard_with_empty_url.html", "http://foo.com")

    for hcard in result['items']:
        assert_equal(['http://foo.com'], hcard['properties']['url'])


def test_link_with_u_url():
    result = parse_fixture("link_with_u-url.html", "http://foo.com")
    assert_equal({
        "type": ["h-card"],
        "properties": {
            "name": [""],
            "url": ["http://foo.com/"],
        },
    }, result["items"][0])


def test_complex_e_content():
    """When parsing h-* e-* properties, we should fold {"value":..., "html":...}
    into the parsed microformat object, instead of nesting it under an
    unnecessary second layer of "value":
    """
    result = parse_fixture("complex_e_content.html")

    assert_equal({
        "type": ["h-entry"],
        "properties": {
            "content": [{
                "type": [
                    "h-card"
                ],
                "properties": {
                    "name": ["Hello"]
                },
                "html": "<p>Hello</p>",
                "value": "Hello"
            }],
        }
    }, result["items"][0])


def test_nested_values():
    """When parsing nested microformats, check that value is the value of
    the simple property element"""
    result = parse_fixture("nested_values.html")
    entry = result["items"][0]

    assert_equal({
        'properties': {
            'name': ['Kyle'],
            'url': ['http://about.me/kyle'],
        },
        'value': 'Kyle',
        'type': ['h-card'],
    }, entry["properties"]["author"][0])

    assert_equal({
        'properties': {
            'name': ['foobar'],
            'url': ['http://example.com/foobar'],
        },
        'value': 'http://example.com/foobar',
        'type': ['h-cite'],
    }, entry["properties"]["like-of"][0])

    assert_equal({
        'properties': {
            'name': ['George'],
            'url': ['http://people.com/george'],
        },
        'type': ['h-card'],
    }, entry["children"][0])


# implied properties tests

def test_implied_name():
    result = parse_fixture("implied_properties/implied_properties.html")

    for i in range(6):
        assert_equal(result["items"][i]["properties"]["name"][0], "Tom Morris")


def test_implied_url():
    result = parse_fixture("implied_properties/implied_properties.html", url="http://foo.com/")
    assert_equal(
        result["items"][1]["properties"]["url"][0], "http://tommorris.org/")
    # img should not have a "url" property
    assert_true("url" not in result["items"][4]["properties"])
    # href="" is relative to the base url
    assert_equal(result["items"][5]["properties"]["url"][0], "http://foo.com/")


def test_implied_nested_photo():
    result = parse_fixture("implied_properties/implied_properties.html", url="http://bar.org")
    assert_equal(result["items"][2]["properties"]["photo"][0],
                 "http://tommorris.org/photo.png")
    # src="" is relative to the base url
    assert_equal(result["items"][5]["properties"]["photo"][0],
                 "http://bar.org")


def test_implied_nested_photo_alt_name():
    result = parse_fixture("implied_properties/implied_properties.html")
    assert_equal(result["items"][3]["properties"]["name"][0], "Tom Morris")


def test_implied_image():
    result = parse_fixture("implied_properties/implied_properties.html")
    assert_equal(result["items"][4]["properties"]["photo"][0],
                 "http://tommorris.org/photo.png")
    assert_equal(result["items"][4]["properties"]["name"][0], "Tom Morris")

def test_implied_name_empty_alt():
    """An empty alt text should not prevent us from including other
    children in the implied name.
    """

    result = parse_fixture("implied_properties/implied_name_empty_alt.html")
    hcard = result['items'][0]

    assert_equal({
        'type': ['h-card'],
        'properties': {
            'name': ['@kylewmahan'],
            'url': ['https://twitter.com/kylewmahan'],
            'photo': ['https://example.org/test.jpg'],
        },
    }, hcard)

def test_relative_datetime():
    result = parse_fixture("implied_properties/implied_relative_datetimes.html")
    assert_equal(result[u'items'][0][u'properties'][u'updated'][0],
                 '2015-01-02 05:06')

def test_stop_implied_name_nested_h():
    result = parse_fixture("implied_properties/stop_implied_name_nested_h.html")
    assert_true('name' not in
                 result[u'items'][0][u'properties'])

def test_stop_implied_name_e_content():
    result = parse_fixture("implied_properties/stop_implied_name_e_content.html")
    assert_true('name' not in
                 result[u'items'][0][u'properties'])

def test_stop_implied_name_p_content():
    result = parse_fixture("implied_properties/stop_implied_name_p_content.html")
    assert_true('name' not in
                 result[u'items'][0][u'properties'])

def test_implied_properties_silo_pub():
    result = parse_fixture('implied_properties/implied_properties_silo_pub.html')
    item = result['items'][0]

    #implied_name = item['properties']['name'][0]
    #implied_name = re.sub('\s+', ' ', implied_name).strip()
    #assert_equal('@kylewmahan on Twitter', implied_name)

    # no implied name expected under new rules

    assert_true('name' not in
                 item[u'properties'])

def test_simple_person_reference_implied():
    result = parse_fixture("implied_properties/simple_person_reference_implied.html")
    assert_equal(result["items"][0]["properties"],
                 {'name': ['Frances Berriman']})


def test_value_name_whitespace():
    result = parse_fixture("value_name_whitespace.html")

    for i in range(3):
        assert_equal(result["items"][i]["properties"]["content"][0]["value"], "Hello World")
        assert_equal(result["items"][i]["properties"]["name"][0], "Hello World")

    for i in range(3, 8):
        assert_equal(result["items"][i]["properties"]["content"][0]["value"], "Hello\nWorld")
        assert_equal(result["items"][i]["properties"]["name"][0], "Hello\nWorld")

    for i in range(8, 10):
        assert_equal(result["items"][i]["properties"]["content"][0]["value"], "One\nTwo\nThree")
        assert_equal(result["items"][i]["properties"]["name"][0], "One\nTwo\nThree")

    assert_equal(result["items"][10]["properties"]["content"][0]["value"], "Hello World      one\n      two\n      three\n    ")
    assert_equal(result["items"][10]["properties"]["name"][0], "Hello World      one\n      two\n      three\n    ")

    assert_equal(result["items"][11]["properties"]["content"][0]["value"], "Correct name Correct summary")
    assert_equal(result["items"][11]["properties"]["name"][0], "Correct name")

# backcompat tests

def test_doc_tag_backcompat():
    # test that strings, BS doc and BS tags are all parsed and in the latter cases copies are made and are modified by backcompat
    doc = '''<article class="hentry"></article>'''
    soup = BeautifulSoup(doc)

    parse_string = Parser(doc).to_dict()
    assert_true('h-entry' in parse_string['items'][0]['type'])

    p = Parser(soup)
    assert_true('h-entry' in p.to_dict()['items'][0]['type'])
    assert_false(soup is p.__doc__)
    assert_false(soup == p.__doc__)

    p = Parser(soup.article)
    assert_true('h-entry' in p.to_dict()['items'][0]['type'])
    assert_false(soup.article is p.__doc__)
    assert_false(soup.article == p.__doc__)

def test_backcompat_hentry():
    result = parse_fixture("backcompat/hentry.html")
    assert_true('h-entry' in result['items'][0]['type'])
    assert_equal('Tom Morris',
                 result['items'][0]['properties']
                 ['author'][0]['properties']['name'][0])
    assert_equal('A Title',
                 result['items'][0]['properties']['name'][0])
    assert_equal('Some Content',
                 result['items'][0]['properties']['content'][0]['value'])

def test_backcompat_hproduct():
    result = parse_fixture("backcompat/hproduct.html")
    assert_equal(1, len(result["items"]))
    assert_equal(["h-product"], result["items"][0]["type"])
    assert_equal(['bullshit'], result["items"][0]["properties"]["category"])
    assert_equal(['Quacktastic Products'], result["items"][0]["properties"]["brand"])
    assert_equal(['#BULLSHIT-001'], result["items"][0]["properties"]["identifier"])
    assert_equal("Magical tasty sugar pills that don't do anything.", result["items"][0]["properties"]['description'][0]) 
    assert_equal(["Tom's Magical Quack Tincture"], result["items"][0]["properties"]["name"])


def test_backcompat_hproduct_nested_hreview():
    result = parse_fixture("backcompat/hproduct_hreview_nested.html")
    assert_equal(['h-review'], result["items"][0]["children"][0]['type'])

def test_backcompat_hreview_nested_card_event_product():
    result = parse_fixture("backcompat/hreview_nested_card_event_product.html")
    assert_equal(['h-review'], result["items"][0]['type'])
    items = result["items"][0]["properties"]['item']
    assert_equal(3, len(items))

    event = items[0]
    assert_equal(['h-event'], event['type'])
    assert_equal(['http://example.com/event-url'], event['properties']['url'])
    assert_equal(['event name'], event['properties']['name'])

    card = items[1]
    assert_equal(['h-card'], card['type'])
    assert_equal(['http://example.com/card-url'], card['properties']['url'])
    assert_equal(['card name'], card['properties']['name'])

    product = items[2]
    assert_equal(['h-product'], product['type'])
    assert_equal(['http://example.com/product-url'], product['properties']['url'])
    assert_equal(['product name'], product['properties']['name'])


def test_backcompat_rel_bookmark():
    """Confirm that rel=bookmark inside of an h-entry is converted
    to u-url.
    """
    result = parse_fixture('backcompat/feed_with_rel_bookmark.html')
    for ii, url in enumerate((
            '/2014/11/24/jump-rope',
            '/2014/11/23/graffiti',
            '/2014/11/21/earth',
            '/2014/11/19/labor',
    )):
        assert_equal(['h-entry'], result['items'][ii]['type'])
        assert_equal([url], result['items'][ii]['properties']['url'])

def test_backcompat_rel_bookmark():
    """Confirm that rel=bookmark inside of an hentry and hreview is converted
    to a u-url and original u-url is ignored
    """

    tests = ['backcompat/hentry_with_rel_bookmark.html', 'backcompat/hreview_with_rel_tag_bookmark.html']

    results = [parse_fixture(x) for x in tests]

    for result in results:
        assert_equal(['https://example.com/bookmark', 'https://example.com/bookmark-url'], result['items'][0]['properties']['url'])

def test_backcompat_rel_tag():
    """Confirm that rel=tag inside of an hentry is converted
    to a p-category and the last path segment of the href is used.
    """

    tests = ['backcompat/hentry_with_rel_tag.html', 'backcompat/hfeed_with_rel_tag.html', 'backcompat/hrecipe_with_rel_tag.html', 'backcompat/hreview_with_rel_tag_bookmark.html']

    results = [parse_fixture(x) for x in tests]
    for result in results:
        assert_equal(['cat', 'dog', 'mountain lion', 'mouse', 'meerkat'], result['items'][0]['properties']['category'])

def test_backcompat_rel_tag_entry_title():
    """Confirm that other backcompat properties on a rel=tag are parsed
    """

    result = parse_fixture('backcompat/hentry_with_rel_tag_entry_title.html')
    assert_equal(['cat'], result['items'][0]['properties']['category'])
    assert_equal(['rhinoceros'], result['items'][0]['properties']['name'])

def test_backcompat_rel_multiple_root():
    """Confirm that rel=tag and rel=bookmark inside of an hentry+hreview is parsed correctly"""

    result = parse_fixture('backcompat/hreview_hentry_with_rel_tag_bookmark.html')

    assert_equal(len(result['items']), 1)
    assert_true('h-entry' in result['items'][0]['type'])
    assert_true('h-review' in result['items'][0]['type'])

    assert_equal(['cat', 'dog', 'mountain lion', 'mouse', 'meerkat'], result['items'][0]['properties']['category'])
    assert_equal(['https://example.com/bookmark', 'https://example.com/bookmark-url'], result['items'][0]['properties']['url'])

def test_backcompat_ignore_mf1_root_if_mf2_present():
    """Confirm that mf1 root class is ignored if another mf2 root class is present.
    """
    result = parse_fixture('backcompat/ignore_mf1_root_if_mf2_present.html')
    assert_true('h-entry' not in result['items'][0]['type'])
    assert_true('h-event' in result['items'][0]['type'])

def test_backcompat_no_implied_properties_mf1_root():
    """Confirm that mf1 root class does not have implied properties
    """
    result = parse_fixture('backcompat/ignore_mf1_root_if_mf2_present.html')
    assert_true('h-entry' not in result['items'][0]['properties'])
    assert_true('name' not in result['items'][0]['type'])
    assert_true('url' not in result['items'][0]['properties'])
    assert_true('photo' not in result['items'][0]['properties'])

def test_backcompat_ignore_mf2_properties_in_mf1_root():
    """Confirm that mf2 properties are ignored in mf1 root class
    """
    result = parse_fixture('backcompat/ignore_mf2_properties_in_mf1_root.html')
    assert_equal('Correct name', result['items'][0]['properties']['name'][0])
    assert_equal('Correct summary', result['items'][0]['properties']['summary'][0])

def test_backcompat_ignore_mf1_properties_in_mf2_root():
    """Confirm that mf1 properties are ignored in mf2 root class
    """
    result = parse_fixture('backcompat/ignore_mf1_properties_in_mf2_root.html')
    assert_equal('Correct name', result['items'][0]['properties']['name'][0])
    assert_equal('Correct summary', result['items'][0]['properties']['summary'][0])

def test_backcompat_nested_mf2_in_mf1():
    """Confirm that mf2 roots nested inside mf1 root are parsed
    """
    result = parse_fixture('backcompat/nested_mf2_in_mf1.html')
    assert_equal('h-feed', result['items'][0]['type'][0])
    assert_equal('h-entry', result['items'][0]['children'][0]['type'][0])
    assert_equal('Correct name', result['items'][0]['children'][0]['properties']['name'][0])
    assert_equal('Correct summary', result['items'][0]['children'][0]['properties']['summary'][0])

def test_backcompat_nested_mf1_in_mf2():
    """Confirm that mf1 roots nested inside mf2 root are parsed
    """
    result = parse_fixture('backcompat/nested_mf1_in_mf2.html')
    assert_equal('h-feed', result['items'][0]['type'][0])
    assert_equal('h-entry', result['items'][0]['children'][0]['type'][0])
    assert_equal('Correct name', result['items'][0]['children'][0]['properties']['name'][0])
    assert_equal('Correct summary', result['items'][0]['children'][0]['properties']['summary'][0])

def test_backcompat_nested_mf1_in_mf2_e_content():
    """Confirm that mf1 roots nested inside mf2 root e-content are parsed as authored
    """
    result = parse_fixture('backcompat/nested_mf1_in_mf2_e_content.html')

    mf2_entry = result['items'][0]
    mf1_entry = mf2_entry['children'][0]

    assert_equal('<div class="hentry">\n<span class="entry-title">Correct name</span>\n\n<span class="entry-summary">Correct summary</span>\n</div>', mf2_entry['properties']['content'][0]['html'])

    assert_equal('Correct name Correct summary', mf2_entry['properties']['content'][0]['value'])

    assert_equal('h-entry', mf1_entry['type'][0])
    assert_equal('Correct name', mf1_entry['properties']['name'][0])
    assert_equal('Correct summary', mf1_entry['properties']['summary'][0])

def test_backcompat_hentry_content_html():
    """Confirm that mf1 entry-content html is parsed as authored without mf2 replacements
    """
    result = parse_fixture('backcompat/hentry_content_html.html')

    entry = result['items'][0]

    assert_equal('<p class="entry-summary">This is a summary</p> \n        <p>This is <a href="/tags/mytag" rel="tag">mytag</a> inside content. </p>', entry['properties']['content'][0]['html'])


# experimental features tests

def test_photo_with_alt():
    """Confirm that alt text in photo is parsed with feature flag alt_in_photo
    """

    path = 'photo_with_alt.html'

    # without flag
    result = parse_fixture(path)

    for i in range(3):
        assert_equal('/photo.jpg', result['items'][i]['properties']['photo'][0])

    # experimental alt_in_photo=True
    with open(os.path.join(TEST_DIR, path)) as f:
        exp_result = Parser(doc=f, html_parser='html5lib', alt_in_photo=True).to_dict()

    assert_equal('/photo.jpg', exp_result['items'][0]['properties']['photo'][0])

    assert_equal('/photo.jpg', exp_result['items'][1]['properties']['photo'][0]['value'])
    assert_equal('alt text', exp_result['items'][1]['properties']['photo'][0]['alt'])

    assert_equal('/photo.jpg', exp_result['items'][2]['properties']['photo'][0]['value'])
    assert_equal('', exp_result['items'][2]['properties']['photo'][0]['alt'])

# unicode tests

def get_all_files():

    all_files = []

    for dir_, _, files in os.walk(TEST_DIR):
        for filename in files:
            rel_dir = os.path.relpath(dir_, TEST_DIR)
            all_files.append( os.path.join(rel_dir, filename))

    return all_files

def assert_unicode_everywhere(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            assert_false(isinstance(k, binary_type),
                         'key=%r; type=%r' % (k, type(k)))
            assert_unicode_everywhere(v)
    elif isinstance(obj, list):
        for v in obj:
            assert_unicode_everywhere(v)

    assert_false(isinstance(obj, binary_type),
                 'value=%r; type=%r' % (obj, type(obj)))


def check_unicode(filename, jsonblob):
    assert_unicode_everywhere(jsonblob)


def test_unicode_everywhere():
    """ make sure everything is unicode """

    for h in get_all_files()  :
        result = parse_fixture(h)
        yield check_unicode, h, result
