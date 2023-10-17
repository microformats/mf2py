import os
import re
import sys
from unittest import TestCase

import mock
from bs4 import BeautifulSoup

from mf2py import Parser

TestCase.maxDiff = None


TEST_DIR = "test/examples/"


def parse_fixture(path, url=None):
    with open(os.path.join(TEST_DIR, path)) as f:
        p = Parser(doc=f, url=url, html_parser="html5lib")
        return p.to_dict()


def test_empty():
    p = Parser()
    assert type(p) is not None
    assert type(p.to_dict()) is dict


def test_open_file():
    with open(os.path.join(TEST_DIR, "empty.html")) as f:
        p = Parser(doc=f)

    assert p.__doc__ is not None
    assert type(p) is not None
    assert type(p.to_dict()) is dict


def test_doc_tag():
    # test that strings, BS doc and BS tags are all parsed
    doc = """<article class="h-entry"></article>"""
    soup = BeautifulSoup(doc, "html5lib")
    parse_string = Parser(doc).to_dict()
    assert "h-entry" in parse_string["items"][0]["type"]
    parse_doc = Parser(soup).to_dict()
    assert "h-entry" in parse_doc["items"][0]["type"]
    parse_tag = Parser(soup.article).to_dict()
    assert "h-entry" in parse_tag["items"][0]["type"]


@mock.patch("requests.get")
def test_user_agent(getter):
    ua_expect = "mf2py - microformats2 parser for python"
    assert Parser.useragent.startswith(ua_expect)

    resp = mock.MagicMock()
    resp.content = b""
    resp.text = ""
    resp.headers = {}
    getter.return_value = resp

    Parser(url="http://example.com")
    getter.assert_called_with(
        "http://example.com", headers={"User-Agent": Parser.useragent}
    )

    Parser.useragent = "something else"
    assert Parser.useragent == "something else"
    # set back to default. damn stateful classes
    Parser.useragent = "mf2py - microformats2 parser for python"


def test_base():
    with open(os.path.join(TEST_DIR, "base.html")) as f:
        p = Parser(doc=f)

    assert p.__url__ == "http://tantek.com/"


def test_simple_parse():
    result = parse_fixture("simple_person_reference.html")
    assert result["items"][0]["properties"] == {"name": ["Frances Berriman"]}


def test_simple_person_reference_same_element():
    result = parse_fixture("simple_person_reference_same_element.html")
    assert result["items"][0]["properties"] == {"name": ["Frances Berriman"]}


def test_person_with_url():
    result = parse_fixture("person_with_url.html")
    assert result["items"][0]["properties"]["name"] == ["Tom Morris"]
    assert result["items"][0]["properties"]["url"] == ["http://tommorris.org/"]


def test_vcp():
    result = parse_fixture("value_class_person.html")
    assert result["items"][0]["properties"]["tel"] == ["+44 1234 567890"]


def test_multiple_root_classnames():
    result = parse_fixture("nested_multiple_classnames.html")
    # order does not matter
    assert len(result["items"]) == 1
    assert set(result["items"][0]["type"]) == set(["h-entry", "h-as-note"])


def test_property_nested_microformat():
    result = parse_fixture("nested_multiple_classnames.html")

    assert len(result["items"]) == 1
    assert "author" in result["items"][0]["properties"]
    assert (
        result["items"][0]["properties"]["author"][0]["properties"]["name"][0]
        == "Tom Morris"
    )
    assert (
        result["items"][0]["properties"]["reviewer"][0]["properties"]["name"][0]
        == "Tom Morris"
    )
    assert (
        result["items"][0]["properties"]["author"][0]["properties"]["adr"][0][
            "properties"
        ]["city"][0]
        == "London"
    )


def test_plain_child_microformat():
    result = parse_fixture("nested_multiple_classnames.html")

    assert len(result["items"]) == 1
    assert "children" in result["items"][0]
    assert len(result["items"][0]["children"]) == 1
    assert result["items"][0]["children"][0]["properties"]["name"][0] == "Some Citation"


def test_datetime_parsing():
    result = parse_fixture("datetimes.html")
    assert result["items"][0]["properties"]["start"][0] == "2014-01-01T12:00:00+0000"
    assert result["items"][0]["properties"]["end"][0] == "3014-01-01T18:00:00+0000"
    assert result["items"][0]["properties"]["duration"][0] == "P1000Y"
    assert result["items"][0]["properties"]["updated"][0] == "2011-08-26T00:01:21+0000"
    assert result["items"][0]["properties"]["updated"][1] == "2011-08-26T00:01:21+0000"


def test_datetime_vcp_parsing():
    result = parse_fixture("datetimes.html")
    assert len(result["items"]) == 16
    assert result["items"][1]["properties"]["published"][0] == "3014-01-01 01:21Z"
    assert result["items"][2]["properties"]["updated"][0] == "2014-03-11 09:55"
    assert result["items"][3]["properties"]["published"][0] == "2014-01-30 15:28"
    assert result["items"][4]["properties"]["published"][0] == "9999-01-14T11:52+0800"
    assert result["items"][5]["properties"]["published"][0] == "2014-06-01 12:30-0600"
    assert result["items"][8]["properties"]["start"][0] == "2014-06-01 12:30-0600"
    assert result["items"][9]["properties"]["start"][0] == "2014-06-01 12:30-0600"
    assert result["items"][10]["properties"]["start"][0] == "2014-06-01 00:30-0600"
    assert result["items"][10]["properties"]["end"][0] == "2014-06-01 12:15"
    assert result["items"][10]["properties"]["start"][1] == "2014-06-01 00:30-0600"
    assert result["items"][10]["properties"]["end"][1] == "2014-06-01 12:15"
    assert result["items"][11]["properties"]["start"][0] == "2016-03-02 00:30-0600"
    assert result["items"][12]["properties"]["start"][0] == "2014-06-01 12:30-600"
    assert result["items"][13]["properties"]["start"][0] == "2014-06-01 12:30+600"
    assert result["items"][14]["properties"]["start"][0] == "2014-06-01 12:30Z"
    assert result["items"][15]["properties"]["start"][0] == "2014-06-01 12:30-600"


def test_dt_end_implied_date():
    """Test that events with dt-start and dt-end use the implied date rule
    http://microformats.org/wiki/value-class-pattern#microformats2_parsers
    for times without dates"""
    result = parse_fixture("datetimes.html")

    event_wo_tz = result["items"][6]
    assert event_wo_tz["properties"]["start"][0] == "2014-05-21 18:30"
    assert event_wo_tz["properties"]["end"][0] == "2014-05-21 19:30"

    event_w_tz = result["items"][7]
    assert event_w_tz["properties"]["start"][0] == "2014-06-01 12:30-0600"
    assert event_w_tz["properties"]["end"][0] == "2014-06-01 19:30-0600"


def test_embedded_parsing():
    result = parse_fixture("embedded.html")
    assert (
        result["items"][0]["properties"]["content"][0]["html"]
        == "<p>Blah blah blah blah blah.</p>\n   <p>Blah.</p>\n   <p>Blah blah blah.</p>"
    )
    assert (
        result["items"][0]["properties"]["content"][0]["value"]
        == "Blah blah blah blah blah.\nBlah.\nBlah blah blah."
    )


def test_hoisting_nested_hcard():
    result = parse_fixture("nested_hcards.html")
    expected = [
        {
            "properties": {
                "author": [
                    {
                        "properties": {"name": ["KP1"]},
                        "type": ["h-card"],
                        "value": "KP1",
                    }
                ],
                "in-reply-to": [
                    {"properties": {"name": ["KP"]}, "type": ["h-cite"], "value": "KP"}
                ],
            },
            "type": ["h-entry"],
        }
    ]
    assert expected == result["items"]


def test_html_tag_class():
    result = parse_fixture("hfeed_on_html_tag.html")
    assert ["h-feed"] == result["items"][0]["type"]

    assert ["entry1"] == result["items"][0]["children"][0]["properties"]["name"]
    assert ["entry2"] == result["items"][0]["children"][1]["properties"]["name"]


def test_string_strip():
    result = parse_fixture("string_stripping.html")
    assert "Tom Morris" == result["items"][0]["properties"]["name"][0]


def test_template_parse():
    result = parse_fixture("template_tag.html")
    assert 0 == len(result["items"])


def test_template_tag_inside_e_value():
    result = parse_fixture("template_tag_inside_e_value.html")
    assert (
        "This is a Test with a <code>template</code> tag after this:"
        == result["items"][0]["properties"]["content"][0]["html"]
    )
    assert (
        "This is a Test with a template tag after this:"
        == result["items"][0]["properties"]["content"][0]["value"]
    )


def test_ordering_dedup():
    """test that classes are dedeuped and alphabetically ordered"""

    result = parse_fixture("ordering_dedup.html")
    item = result["items"][0]
    assert ["h-entry", "h-feed", "h-product", "h-x-test"] == item["type"]
    assert ["example.com", "example.com/2"] == item["properties"]["url"]
    assert ["name", "URL name"] == item["properties"]["name"]
    assert ["author", "bookmark", "me"] == result["rel-urls"]["example.com/rel"]["rels"]
    assert "de" == result["rel-urls"]["example.com/lang"]["hreflang"]


def test_class_names_format():
    """test that only classes with letters and possibly numbers in the vendor prefix part are used"""

    result = parse_fixture("class_names_format.html")
    item = result["items"][0]
    assert ["h-feed", "h-p3k-entry", "h-x-test"] == item["type"]
    assert "url" in item["properties"]
    assert "p3k-url" in item["properties"]
    assert "Url" not in item["properties"]
    assert "-url" not in item["properties"]
    assert "url-" not in item["properties"]

    assert "name" in item["properties"]
    assert "p3k-name" in item["properties"]
    assert "nAme" not in item["properties"]
    assert "-name" not in item["properties"]
    assert "name-" not in item["properties"]


def test_area_uparsing():
    result = parse_fixture("area.html")
    assert {"url": ["http://suda.co.uk"], "name": ["Brian Suda"]} == result["items"][0][
        "properties"
    ]
    assert "shape" in result["items"][0]
    assert "coords" in result["items"][0]


def test_src_equiv():
    result = parse_fixture("test_src_equiv.html")
    for item in result["items"]:
        assert "x-example" in item["properties"]
        assert "http://example.org/" == item["properties"]["x-example"][0]


def test_rels():
    result = parse_fixture("rel.html")
    assert {
        "in-reply-to": ["http://example.com/1", "http://example.com/2"],
        "author": ["http://example.com/a", "http://example.com/b"],
        "alternate": ["http://example.com/fr"],
        "home": ["http://example.com/fr"],
    } == result["rels"]
    assert {
        "http://example.com/1": {"text": "post 1", "rels": ["in-reply-to"]},
        "http://example.com/2": {"text": "post 2", "rels": ["in-reply-to"]},
        "http://example.com/a": {"text": "author a", "rels": ["author"]},
        "http://example.com/b": {"text": "author b", "rels": ["author"]},
        "http://example.com/fr": {
            "text": "French mobile homepage",
            "media": "handheld",
            "rels": ["alternate", "home"],
            "hreflang": "fr",
        },
    } == result["rel-urls"]


def test_alternates():
    result = parse_fixture("rel.html")
    assert [
        {
            "url": "http://example.com/fr",
            "media": "handheld",
            "text": "French mobile homepage",
            "rel": "home",
            "hreflang": "fr",
        }
    ] == result["alternates"]


def test_enclosures():
    result = parse_fixture("rel_enclosure.html")
    assert {"enclosure": ["http://example.com/movie.mp4"]} == result["rels"]
    assert {
        "http://example.com/movie.mp4": {
            "rels": ["enclosure"],
            "text": "my movie",
            "type": "video/mpeg",
        }
    } == result["rel-urls"]


def test_empty_href():
    result = parse_fixture("hcard_with_empty_url.html", "http://foo.com")

    for hcard in result["items"]:
        assert ["http://foo.com"] == hcard["properties"]["url"]


def test_link_with_u_url():
    result = parse_fixture("link_with_u-url.html", "http://foo.com")
    assert {
        "type": ["h-card"],
        "properties": {
            "name": [""],
            "url": ["http://foo.com/"],
        },
    } == result["items"][0]


def test_broken_url():
    result = parse_fixture("broken_url.html", "http://example.com")
    assert (
        result["items"][0]["properties"]["relative"][0] == "http://example.com/foo.html"
    )
    assert result["items"][0]["properties"]["url"][0] == "http://www.[w3.org/"
    assert (
        result["items"][0]["properties"]["photo"][0]
        == "http://www.w3].org/20[08/site/images/logo-w3c-mobile-lg"
    )


def test_complex_e_content():
    """When parsing h-* e-* properties, we should fold {"value":..., "html":...}
    into the parsed microformat object, instead of nesting it under an
    unnecessary second layer of "value":
    """
    result = parse_fixture("complex_e_content.html")

    assert {
        "type": ["h-entry"],
        "properties": {
            "content": [
                {
                    "type": ["h-card"],
                    "properties": {"name": ["Hello"]},
                    "html": "<p>Hello</p>",
                    "value": "Hello",
                }
            ],
        },
    } == result["items"][0]


def test_nested_values():
    """When parsing nested microformats, check that value is the value of
    the simple property element"""
    result = parse_fixture("nested_values.html")
    entry = result["items"][0]

    assert {
        "properties": {
            "name": ["Kyle"],
            "url": ["http://about.me/kyle"],
        },
        "value": "Kyle",
        "type": ["h-card"],
    } == entry["properties"]["author"][0]

    assert {
        "properties": {
            "name": ["foobar"],
            "url": ["http://example.com/foobar"],
        },
        "value": "http://example.com/foobar",
        "type": ["h-cite"],
    } == entry["properties"]["like-of"][0]

    assert {
        "properties": {
            "name": ["George"],
            "url": ["http://people.com/george"],
        },
        "type": ["h-card"],
    } == entry["children"][0]


# implied properties tests


def test_implied_name():
    result = parse_fixture("implied_properties/implied_properties.html")

    for i in range(7):
        assert result["items"][i]["properties"]["name"][0] == "Tom Morris"


def test_implied_url():
    result = parse_fixture(
        "implied_properties/implied_properties.html", url="http://foo.com/"
    )
    assert result["items"][1]["properties"]["url"][0] == "http://tommorris.org/"
    # img should not have a "url" property
    assert "url" not in result["items"][4]["properties"]
    # href="" is relative to the base url
    assert result["items"][5]["properties"]["url"][0] == "http://foo.com/"


def test_implied_photo():
    result = parse_fixture("implied_properties/implied_photo.html")

    for i in range(12):
        photos = result["items"][i]["properties"]["photo"]
        assert len(photos) == 1
        assert photos[0] == "http://example.com/photo.jpg"

    # tests for no photo
    for i in range(12, 23):
        assert "photo" not in result["items"][i]["properties"]

    result = parse_fixture("implied_properties/implied_photo_relative_url.html")

    assert (
        result["items"][0]["properties"]["photo"][0]["value"]
        == "http://example.com/jane-img.jpeg"
    )
    assert (
        result["items"][1]["properties"]["photo"][0]
        == "http://example.com/jane-object.jpeg"
    )


def test_implied_url():
    result = parse_fixture("implied_properties/implied_url.html")

    for i in range(12):
        urls = result["items"][i]["properties"]["url"]
        assert len(urls) == 1
        assert urls[0] == "http://example.com"

    # tests for no url
    for i in range(12, 23):
        assert "url" not in result["items"][i]["properties"]


def test_stop_implied_url():
    """testing that explicit properties case implied url-parsing to be aborted"""

    result = parse_fixture("implied_properties/stop_implied_url.html")

    assert "url" not in result["items"][0]["properties"]
    assert "url" not in result["items"][1]["properties"]
    assert "url" not in result["items"][2]["properties"]
    assert "url" not in result["items"][3]["properties"]
    assert "url" not in result["items"][4]["properties"]
    assert "url" not in result["items"][5]["properties"]

    assert result["items"][6]["properties"]["url"] == ["http://example.com/"]
    assert result["items"][7]["properties"]["url"] == ["http://example.com/"]
    assert result["items"][8]["properties"]["url"] == ["http://example.com/"]
    assert result["items"][9]["properties"]["url"] == ["http://example.com/"]


def test_implied_nested_photo():
    result = parse_fixture(
        "implied_properties/implied_properties.html", url="http://bar.org"
    )
    assert result["items"][2]["properties"]["photo"][0] == {
        "alt": "",
        "value": "http://tommorris.org/photo.png",
    }
    assert (
        result["items"][3]["properties"]["photo"][0] == "http://tommorris.org/photo.png"
    )
    assert result["items"][4]["properties"]["photo"][0] == {
        "alt": "Tom Morris",
        "value": "http://tommorris.org/photo.png",
    }
    # src="" is relative to the base url
    assert result["items"][6]["properties"]["photo"][0] == "http://bar.org"


def test_implied_nested_photo_alt_name():
    result = parse_fixture("implied_properties/implied_properties.html")
    assert result["items"][3]["properties"]["name"][0] == "Tom Morris"


def test_implied_image():
    result = parse_fixture("implied_properties/implied_properties.html")
    assert result["items"][4]["properties"]["photo"][0] == {
        "alt": "Tom Morris",
        "value": "http://tommorris.org/photo.png",
    }
    assert result["items"][4]["properties"]["name"][0] == "Tom Morris"


def test_implied_name_empty_alt():
    """An empty alt text should not prevent us from including other
    children in the implied name.
    """

    result = parse_fixture("implied_properties/implied_name_empty_alt.html")
    hcard = result["items"][0]

    assert {
        "type": ["h-card"],
        "properties": {
            "name": ["@kylewmahan"],
            "url": ["https://twitter.com/kylewmahan"],
            "photo": [{"alt": "", "value": "https://example.org/test.jpg"}],
        },
    } == hcard


def test_relative_datetime():
    result = parse_fixture("implied_properties/implied_relative_datetimes.html")
    assert result["items"][0]["properties"]["updated"][0] == "2015-01-02 05:06"


def test_stop_implied_name_nested_h():
    result = parse_fixture("implied_properties/stop_implied_name_nested_h.html")
    assert "name" not in result["items"][0]["properties"]


def test_stop_implied_name_e_content():
    result = parse_fixture("implied_properties/stop_implied_name_e_content.html")
    assert "name" not in result["items"][0]["properties"]


def test_stop_implied_name_p_content():
    result = parse_fixture("implied_properties/stop_implied_name_p_content.html")
    assert "name" not in result["items"][0]["properties"]


def test_implied_properties_silo_pub():
    result = parse_fixture("implied_properties/implied_properties_silo_pub.html")
    item = result["items"][0]

    # implied_name = item['properties']['name'][0]
    # implied_name = re.sub('\s+', ' ', implied_name).strip()
    # assert '@kylewmahan on Twitter', implied_name)

    # no implied name expected under new rules

    assert "name" not in item["properties"]


def test_simple_person_reference_implied():
    result = parse_fixture("implied_properties/simple_person_reference_implied.html")
    assert result["items"][0]["properties"] == {"name": ["Frances Berriman"]}


def test_implied_name_alt():
    result = parse_fixture("implied_properties/implied_name_alt.html")
    assert result["items"][0]["children"][0] == {
        "type": ["h-card"],
        "properties": {
            "name": ["Avatar of Stephen"],
            "photo": [{"alt": "Avatar of", "value": "avatar.jpg"}],
        },
    }


def test_value_name_whitespace():
    result = parse_fixture("value_name_whitespace.html")

    for i in range(3):
        assert result["items"][i]["properties"]["content"][0]["value"] == "Hello World"
        assert result["items"][i]["properties"]["name"][0] == "Hello World"

    for i in range(3, 8):
        assert result["items"][i]["properties"]["content"][0]["value"] == "Hello\nWorld"
        assert result["items"][i]["properties"]["name"][0] == "Hello\nWorld"

    for i in range(8, 10):
        assert (
            result["items"][i]["properties"]["content"][0]["value"] == "One\nTwo\nThree"
        )
        assert result["items"][i]["properties"]["name"][0] == "One\nTwo\nThree"

    assert (
        result["items"][10]["properties"]["content"][0]["value"]
        == "Hello World      one\n      two\n      three\n    "
    )
    assert (
        result["items"][10]["properties"]["name"][0]
        == "Hello World      one\n      two\n      three\n    "
    )

    assert (
        result["items"][11]["properties"]["content"][0]["value"]
        == "Correct name Correct summary"
    )
    assert result["items"][11]["properties"]["name"][0] == "Correct name"


# backcompat tests


def test_backcompat_hentry():
    result = parse_fixture("backcompat/hentry.html")
    assert "h-entry" in result["items"][0]["type"]
    assert (
        "Tom Morris"
        == result["items"][0]["properties"]["author"][0]["properties"]["name"][0]
    )
    assert "A Title" == result["items"][0]["properties"]["name"][0]
    assert "Some Content" == result["items"][0]["properties"]["content"][0]["value"]


def test_backcompat_hproduct():
    result = parse_fixture("backcompat/hproduct.html")
    assert 1 == len(result["items"])
    assert ["h-product"] == result["items"][0]["type"]
    assert ["bullshit"] == result["items"][0]["properties"]["category"]
    assert ["Quacktastic Products"] == result["items"][0]["properties"]["brand"]
    assert ["#BULLSHIT-001"] == result["items"][0]["properties"]["identifier"]
    assert (
        "Magical tasty sugar pills that don't do anything."
        == result["items"][0]["properties"]["description"][0]
    )
    assert ["Tom's Magical Quack Tincture"] == result["items"][0]["properties"]["name"]


def test_backcompat_hproduct_nested_hreview():
    result = parse_fixture("backcompat/hproduct_hreview_nested.html")
    assert ["h-review"] == result["items"][0]["children"][0]["type"]


def test_backcompat_hreview_nested_card_event_product():
    result = parse_fixture("backcompat/hreview_nested_card_event_product.html")
    assert ["h-review"] == result["items"][0]["type"]
    items = result["items"][0]["properties"]["item"]
    assert 3 == len(items)

    event = items[0]
    assert ["h-event"] == event["type"]
    assert ["http://example.com/event-url"] == event["properties"]["url"]
    assert ["event name"] == event["properties"]["name"]

    card = items[1]
    assert ["h-card"] == card["type"]
    assert ["http://example.com/card-url"] == card["properties"]["url"]
    assert ["card name"] == card["properties"]["name"]

    product = items[2]
    assert ["h-product"] == product["type"]
    assert ["http://example.com/product-url"] == product["properties"]["url"]
    assert ["product name"] == product["properties"]["name"]


def test_backcompat_rel_bookmark():
    """Confirm that rel=bookmark inside of an h-entry is converted
    to u-url.
    """
    result = parse_fixture("backcompat/feed_with_rel_bookmark.html")
    for ii, url in enumerate(
        (
            "/2014/11/24/jump-rope",
            "/2014/11/23/graffiti",
            "/2014/11/21/earth",
            "/2014/11/19/labor",
        )
    ):
        assert ["h-entry"] == result["items"][ii]["type"]
        assert [url] == result["items"][ii]["properties"]["url"]


def test_backcompat_rel_bookmark():
    """Confirm that rel=bookmark inside of an hentry and hreview is converted
    to a u-url and original u-url is ignored
    """

    tests = [
        "backcompat/hentry_with_rel_bookmark.html",
        "backcompat/hreview_with_rel_tag_bookmark.html",
    ]

    results = [parse_fixture(x) for x in tests]

    for result in results:
        assert [
            "https://example.com/bookmark",
            "https://example.com/bookmark-url",
        ] == result["items"][0]["properties"]["url"]


def test_backcompat_rel_tag():
    """Confirm that rel=tag inside of an hentry is converted
    to a p-category and the last path segment of the href is used.
    """

    tests = [
        "backcompat/hentry_with_rel_tag.html",
        "backcompat/hfeed_with_rel_tag.html",
        "backcompat/hrecipe_with_rel_tag.html",
        "backcompat/hreview_with_rel_tag_bookmark.html",
    ]

    results = [parse_fixture(x) for x in tests]
    for result in results:
        assert ["cat", "dog", "mountain lion", "mouse", "meerkat"] == result["items"][
            0
        ]["properties"]["category"]


def test_backcompat_rel_tag_entry_title():
    """Confirm that other backcompat properties on a rel=tag are parsed"""

    result = parse_fixture("backcompat/hentry_with_rel_tag_entry_title.html")
    assert ["cat"] == result["items"][0]["properties"]["category"]
    assert ["rhinoceros"] == result["items"][0]["properties"]["name"]


def test_backcompat_rel_multiple_root():
    """Confirm that rel=tag and rel=bookmark inside of an hentry+hreview is parsed correctly"""

    result = parse_fixture("backcompat/hreview_hentry_with_rel_tag_bookmark.html")

    assert len(result["items"]) == 1
    assert "h-entry" in result["items"][0]["type"]
    assert "h-review" in result["items"][0]["type"]

    assert ["cat", "dog", "mountain lion", "mouse", "meerkat"] == result["items"][0][
        "properties"
    ]["category"]
    assert [
        "https://example.com/bookmark",
        "https://example.com/bookmark-url",
    ] == result["items"][0]["properties"]["url"]


def test_backcompat_ignore_mf1_root_if_mf2_present():
    """Confirm that mf1 root class is ignored if another mf2 root class is present."""
    result = parse_fixture("backcompat/ignore_mf1_root_if_mf2_present.html")
    assert "h-entry" not in result["items"][0]["type"]
    assert "h-event" in result["items"][0]["type"]


def test_backcompat_no_implied_properties_mf1_root():
    """Confirm that mf1 root class does not have implied properties"""
    result = parse_fixture("backcompat/ignore_mf1_root_if_mf2_present.html")
    assert "h-entry" not in result["items"][0]["properties"]
    assert "name" not in result["items"][0]["type"]
    assert "url" not in result["items"][0]["properties"]
    assert "photo" not in result["items"][0]["properties"]


def test_backcompat_ignore_mf2_properties_in_mf1_root():
    """Confirm that mf2 properties are ignored in mf1 root class"""
    result = parse_fixture("backcompat/ignore_mf2_properties_in_mf1_root.html")
    assert "Correct name" == result["items"][0]["properties"]["name"][0]
    assert "Correct summary" == result["items"][0]["properties"]["summary"][0]


def test_backcompat_ignore_mf1_properties_in_mf2_root():
    """Confirm that mf1 properties are ignored in mf2 root class"""
    result = parse_fixture("backcompat/ignore_mf1_properties_in_mf2_root.html")
    assert "Correct name" == result["items"][0]["properties"]["name"][0]
    assert "Correct summary" == result["items"][0]["properties"]["summary"][0]


def test_backcompat_nested_mf2_in_mf1():
    """Confirm that mf2 roots nested inside mf1 root are parsed"""
    result = parse_fixture("backcompat/nested_mf2_in_mf1.html")
    assert "h-feed" == result["items"][0]["type"][0]
    assert "h-entry" == result["items"][0]["children"][0]["type"][0]
    assert "Correct name" == result["items"][0]["children"][0]["properties"]["name"][0]
    assert (
        "Correct summary"
        == result["items"][0]["children"][0]["properties"]["summary"][0]
    )


def test_backcompat_nested_mf1_in_mf2():
    """Confirm that mf1 roots nested inside mf2 root are parsed"""
    result = parse_fixture("backcompat/nested_mf1_in_mf2.html")
    assert "h-feed" == result["items"][0]["type"][0]
    assert "h-entry" == result["items"][0]["children"][0]["type"][0]
    assert "Correct name" == result["items"][0]["children"][0]["properties"]["name"][0]
    assert (
        "Correct summary"
        == result["items"][0]["children"][0]["properties"]["summary"][0]
    )


def test_backcompat_nested_mf1_in_mf2_e_content():
    """Confirm that mf1 roots nested inside mf2 root e-content are parsed as authored"""
    result = parse_fixture("backcompat/nested_mf1_in_mf2_e_content.html")

    mf2_entry = result["items"][0]
    mf1_entry = mf2_entry["children"][0]

    assert (
        '<div class="hentry">\n<span class="entry-title">Correct name</span>\n\n<span class="entry-summary">Correct summary</span>\n</div>'
        == mf2_entry["properties"]["content"][0]["html"]
    )

    assert (
        "Correct name Correct summary" == mf2_entry["properties"]["content"][0]["value"]
    )

    assert "h-entry" == mf1_entry["type"][0]
    assert "Correct name" == mf1_entry["properties"]["name"][0]
    assert "Correct summary" == mf1_entry["properties"]["summary"][0]


def test_backcompat_hentry_content_html():
    """Confirm that mf1 entry-content html is parsed as authored without mf2 replacements"""
    result = parse_fixture("backcompat/hentry_content_html.html")

    entry = result["items"][0]

    assert (
        '<p class="entry-summary">This is a summary</p> \n        <p>This is <a href="/tags/mytag" rel="tag">mytag</a> inside content. </p>'
        == entry["properties"]["content"][0]["html"]
    )


def test_whitespace_with_tags_inside_property():
    """Whitespace should only be trimmed at the ends of textContent, not inside.

    https://github.com/microformats/mf2py/issues/112
    """
    result = parse_fixture("tag_whitespace_inside_p_value.html")
    assert result["items"][0]["properties"] == {"name": ["foo bar"]}


def test_photo_with_alt():
    """Confirm that alt text in img is parsed as a u-* property and implied photo"""

    path = "img_with_alt.html"

    result = parse_fixture(path)

    with open(os.path.join(TEST_DIR, path)) as f:
        exp_result = Parser(doc=f, html_parser="html5lib").to_dict()

    # simple img with u-*
    assert "/photo.jpg" == result["items"][0]["properties"]["photo"][0]
    assert "/photo.jpg" == exp_result["items"][0]["properties"]["photo"][0]

    assert {"alt": "alt text", "value": "/photo.jpg"} == result["items"][1][
        "properties"
    ]["url"][0]
    assert "/photo.jpg" == exp_result["items"][1]["properties"]["url"][0]["value"]
    assert "alt text" == exp_result["items"][1]["properties"]["url"][0]["alt"]

    assert {"alt": "", "value": "/photo.jpg"} == result["items"][2]["properties"][
        "in-reply-to"
    ][0]
    assert (
        "/photo.jpg" == exp_result["items"][2]["properties"]["in-reply-to"][0]["value"]
    )
    assert "" == exp_result["items"][2]["properties"]["in-reply-to"][0]["alt"]

    # img with u-* and h-* example
    assert "h-cite" in result["items"][3]["properties"]["in-reply-to"][0]["type"]
    assert (
        "/photo.jpg"
        == result["items"][3]["properties"]["in-reply-to"][0]["properties"]["photo"][0]
    )
    assert "/photo.jpg" == result["items"][3]["properties"]["in-reply-to"][0]["value"]
    assert "alt" not in result["items"][3]["properties"]["in-reply-to"][0]

    assert "h-cite" in exp_result["items"][3]["properties"]["in-reply-to"][0]["type"]
    assert (
        "/photo.jpg"
        == exp_result["items"][3]["properties"]["in-reply-to"][0]["properties"][
            "photo"
        ][0]
    )
    assert (
        "/photo.jpg" == exp_result["items"][3]["properties"]["in-reply-to"][0]["value"]
    )
    assert "alt" not in exp_result["items"][3]["properties"]["in-reply-to"][0]

    assert "h-cite" in result["items"][4]["properties"]["in-reply-to"][0]["type"]
    assert {"alt": "alt text", "value": "/photo.jpg"} == result["items"][4][
        "properties"
    ]["in-reply-to"][0]["properties"]["photo"][0]
    assert "/photo.jpg" == result["items"][4]["properties"]["in-reply-to"][0]["value"]
    assert "alt" in result["items"][4]["properties"]["in-reply-to"][0]

    assert "h-cite" in exp_result["items"][4]["properties"]["in-reply-to"][0]["type"]
    assert (
        "/photo.jpg"
        == exp_result["items"][4]["properties"]["in-reply-to"][0]["properties"][
            "photo"
        ][0]["value"]
    )
    assert (
        "/photo.jpg" == exp_result["items"][4]["properties"]["in-reply-to"][0]["value"]
    )
    assert (
        "alt text"
        == exp_result["items"][4]["properties"]["in-reply-to"][0]["properties"][
            "photo"
        ][0]["alt"]
    )
    assert "alt text" == exp_result["items"][4]["properties"]["in-reply-to"][0]["alt"]

    assert "h-cite" in result["items"][5]["properties"]["in-reply-to"][0]["type"]
    assert {"alt": "", "value": "/photo.jpg"} == result["items"][5]["properties"][
        "in-reply-to"
    ][0]["properties"]["photo"][0]
    assert "/photo.jpg" == result["items"][5]["properties"]["in-reply-to"][0]["value"]
    assert "alt" in result["items"][5]["properties"]["in-reply-to"][0]

    assert "h-cite" in exp_result["items"][5]["properties"]["in-reply-to"][0]["type"]
    assert (
        "/photo.jpg"
        == exp_result["items"][5]["properties"]["in-reply-to"][0]["properties"][
            "photo"
        ][0]["value"]
    )
    assert (
        "/photo.jpg" == exp_result["items"][5]["properties"]["in-reply-to"][0]["value"]
    )
    assert (
        ""
        == exp_result["items"][5]["properties"]["in-reply-to"][0]["properties"][
            "photo"
        ][0]["alt"]
    )
    assert "" == exp_result["items"][5]["properties"]["in-reply-to"][0]["alt"]


def test_photo_with_srcset():
    result = parse_fixture("img_with_srcset.html")

    assert result["items"][0]["properties"]["photo"][0]["srcset"] == {
        "480w": "elva-fairy-480w.jpg",
        "800w": "elva-fairy-800w.jpg",
    }
    assert result["items"][1]["properties"]["photo"][0]["srcset"] == {
        "1x": "elva-fairy-320w.jpg",
        "1.5x": "elva-fairy-480w.jpg",
        "2x": "elva-fairy-640w.jpg",
    }
    assert (
        result["items"][1]["properties"]["photo"][0]["srcset"]["2x"]
        != "elva-fairy-2w.jpg"
    )
    for i in range(2, 5):
        assert result["items"][i]["properties"]["photo"][0]["srcset"] == {
            "1x": "elva-fairy,320w.jpg",
            "1.5x": "elva-fairy,480w.jpg",
        }
    assert result["items"][5]["properties"]["photo"][0]["srcset"] == {
        "1x": "elva-fairy,320w.jpg",
    }

    result = parse_fixture("img_with_srcset_with_base.html")

    assert result["items"][0]["properties"]["photo"][0]["srcset"] == {
        "480w": "https://example.com/elva-fairy-480w.jpg",
        "800w": "https://example.com/elva-fairy-800w.jpg",
    }


def test_parse_id():
    result = parse_fixture("parse_id.html")
    assert "recentArticles" == result["items"][0]["id"]
    assert "article" == result["items"][0]["children"][0]["id"]
    assert "id" not in result["items"][0]["children"][1]
    assert "theAuthor" == result["items"][0]["properties"]["author"][0]["id"]


# unicode tests


def get_all_files():
    all_files = []

    for dir_, _, files in os.walk(TEST_DIR):
        for filename in files:
            rel_dir = os.path.relpath(dir_, TEST_DIR)
            all_files.append(os.path.join(rel_dir, filename))

    return all_files


def assert_unicode_everywhere(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            assert not isinstance(k, bytes), "key=%r; type=%r" % (k, type(k))
            assert_unicode_everywhere(v)
    elif isinstance(obj, list):
        for v in obj:
            assert_unicode_everywhere(v)

    assert not isinstance(obj, bytes), "value=%r; type=%r" % (obj, type(obj))


def check_unicode(filename, jsonblob):
    assert_unicode_everywhere(jsonblob)


def test_unicode_everywhere():
    """make sure everything is unicode"""

    for h in get_all_files():
        result = parse_fixture(h)
        check_unicode(h, result)


def test_input_tree_integrity():
    """make sure that if we parse a BS4 soup, our modifications do not leak into the document represented by it"""

    for path in get_all_files():
        with open(os.path.join(TEST_DIR, path)) as f:
            soup = BeautifulSoup(f, features="lxml")
            html1 = soup.prettify()
            p = Parser(doc=soup, html_parser="lxml")
            html2 = soup.prettify()
        make_labelled_cmp("tree_integrity_" + path)(html1, html2)


def make_labelled_cmp(label):
    def f(html1, html2):
        assert html1 == html2

    f.description = label
    return f


def test_all_u_cases():
    """test variations of u- parsing and that relative urls are always resolved"""

    URL_COUNT = 28
    result = parse_fixture("u_all_cases.html")

    assert URL_COUNT == len(result["items"][0]["properties"]["url"])
    for i in range(URL_COUNT):
        make_labelled_cmp("all_u_cases_" + str(i))(
            "http://example.com/test", result["items"][0]["properties"]["url"][i]
        )
