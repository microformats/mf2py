# coding: utf-8

import json
from bs4 import BeautifulSoup

import requests

from .dom_helpers import get_attr
from . import backcompat, mf2_classes, implied_properties, parse_property

import sys
if sys.version < '3':
    from urlparse import urlparse, urljoin
else:
    from urllib.parse import urlparse, urljoin


class Parser(object):
    """Object to parse a document for microformats and return them in appropriate formats.

    Keyword arguments
    ----
    doc : file handle or text of content to parse. Optionally fetched from given 'url' kwarg
    url : url of the file to be processed. Optionally fetched from base-element of given 'doc' kwarg

    Attributes
    ----------
    useragent : returns the UA string for the Parser

    Public methods
    ---------------
    parse : parses the file/url contents for microformats. done automatically on initialisation.
    filter_by_type : returns only the microformat specified by type_name argument
    to_dict : returns python dict containing parsed microformats
    to_json : returns json formatted version of parsed microformats

    """
    useragent = 'mf2py - microformats2 parser for python'

    def __init__(self, *args, **kwargs):
        self.__url__ = None
        self.__doc__ = None
        self.__parsed__ = {"items": [], "rels": {}}

        if 'doc' in kwargs:
            self.__doc__ = BeautifulSoup(kwargs['doc'])

        if 'url' in kwargs:
            self.__url__ = kwargs['url']

            if self.__doc__ is None:
                data = requests.get(self.__url__)
                self.__doc__ = BeautifulSoup(data.text)

        # check for <base> tag
        if self.__doc__:
            poss_base = self.__doc__.find("base")
            if poss_base:
                poss_base_url = poss_base.get('href')  # try to get href
                if poss_base_url:
                    if urlparse(poss_base_url).netloc:
                        # base specifies an absolute path
                        self.__url__ = poss_base_url
                    elif self.__url__:
                        # base specifies a relative path
                        self.__url__ = urljoin(self.__url__, poss_base_url)

        if self.__doc__ is not None:
            # parse!
            backcompat.apply_rules(self.__doc__)
            self.parse()


    ## function to parse the document
    def parse(self):
        # set of all parsed things
        #parsed = set()

        ## function for handling a root microformat i.e. h-*
        def handle_microformat(root_class_names, el, is_nested=True):
            properties = {}
            children = []

            # parse for properties and children
            for child in el.find_all(True, recursive=False):
                child_props, child_children = parse_props(child)
                for key, new_value in child_props.items():
                    prop_value = properties.get(key, [])
                    prop_value.extend(new_value)
                    properties[key] = prop_value
                children.extend(child_children)

            # if some properties not already found find in implied ways
            if 'name' not in properties:
                properties["name"] = implied_properties.name(el)

            if "photo" not in properties:
                x = implied_properties.photo(el, base_url=self.__url__)
                if x is not None:
                    properties["photo"] = x

            if "url" not in properties:
                x = implied_properties.url(el, base_url=self.__url__)
                if x is not None:
                    properties["url"] = x

            # build microformat with type and properties
            microformat = {"type": root_class_names,
                           "properties": properties}
            # insert children if any
            if len(children) > 0:
                microformat["children"] = children
            # insert value if it is a nested microformat (check this interpretation)
            if is_nested:
                microformat["value"] = el.get_text()
            return microformat

        ## function to parse properties of element
        def parse_props(el):
            props = {}
            children = []

            classes = el.get("class", [])
            # Is this element a microformat root?
            root_class_names = mf2_classes.root(classes)
            if len(root_class_names) > 0:
                # this element represents a nested microformat
                if len(mf2_classes.properties(classes)) > 0:
                    # nested microformat is property-nested, parse and add to all property lists it's part of
                    nested_microformat = handle_microformat(root_class_names, el)
                    for prop_name in mf2_classes.properties(classes):
                        prop_value = props.get(prop_name, [])
                        prop_value.append(nested_microformat)
                        props[prop_name] = prop_value
                else:
                    # nested microformat is a child microformat, parse and add to children
                    children.append(handle_microformat(root_class_names, el))
            else:
                # Parse plaintext p-* properties.
                value = None
                for prop_name in mf2_classes.text(classes):
                    prop_value = props.get(prop_name, [])

                    # if value has not been parsed then parse it
                    if value is None:
                        value = parse_property.text(el)

                    prop_value.append(value)

                    if prop_value is not []:
                        props[prop_name] = prop_value

                # Parse URL u-* properties.
                value = None
                for prop_name in mf2_classes.url(classes):
                    prop_value = props.get(prop_name, [])

                    # if value has not been parsed then parse it
                    if value is None:
                        value = parse_property.url(el, base_url=self.__url__)

                    prop_value.append(value)

                    if prop_value is not []:
                        props[prop_name] = prop_value

                # Parse datetime dt-* properties.
                value = None
                for prop_name in mf2_classes.datetime(classes):
                    prop_value = props.get(prop_name, [])

                    # if value has not been parsed then parse it
                    if value is None:
                        value = parse_property.datetime(el)

                    prop_value.append(value)

                    if prop_value is not []:
                        props[prop_name] = prop_value

                # Parse embedded markup e-* properties.
                value = None
                for prop_name in mf2_classes.embedded(classes):
                    prop_value = props.get(prop_name, [])

                    # if value has not been parsed then parse it
                    if value is None:
                        value = parse_property.embedded(el)

                    prop_value.append(value)

                    if prop_value is not []:
                        props[prop_name] = prop_value

                # parse child tags, provided this isn't a microformat
                for child in el.find_all(True, recursive=False):
                    child_properties, child_microformats = parse_props(child)
                    for prop_name in child_properties:
                        v = props.get(prop_name, [])
                        v.extend(child_properties[prop_name])
                        props[prop_name] = v
                    children.extend(child_microformats)

            return props, children

        ## function to parse an element for rel microformats
        def parse_rels(el):
            rel_attrs = get_attr(el, 'rel')
            # if rel attributes exist
            if rel_attrs is not None:
                # find the url and normalise it
                url = urljoin(self.__url__, el.get('href', ''))

                # there does not exist alternate in rel attributes then parse rels as local
                if "alternate" not in rel_attrs:
                    for rel_value in rel_attrs:
                        value_list = self.__parsed__["rels"].get(rel_value,[])
                        value_list.append(url)
                        self.__parsed__["rels"][rel_value] = value_list
                else:
                    alternate_list = self.__parsed__.get("alternates",[])
                    alternate_dict = {}
                    alternate_dict["url"] = url
                    x = " ".join([r for r in rel_attrs if not r == "alternate"])
                    if x is not "":
                        alternate_dict["rel"] = x

                    x = get_attr(el, "media")
                    if x is not None:
                        alternate_dict["media"] = x

                    x = get_attr(el, "hreflang")
                    if x is not None:
                        alternate_dict["hreflang"] = x

                    x = get_attr(el, "type")
                    if x is not None:
                        alternate_dict["type"] = x

                    alternate_list.append(alternate_dict)
                    self.__parsed__["alternates"] = alternate_list


        ## function to parse an element for microformats
        def parse_el(el, ctx, top_level=False):

            classes = el.get("class",[])
            # find potential microformats in root classnames h-*
            potential_microformats = mf2_classes.root(classes)

            # if potential microformats found parse them
            if len(potential_microformats) > 0:
                result = handle_microformat(potential_microformats, el, top_level)
                ctx.append(result)
            else:
                # parse child tags
                for child in el.find_all(True, recursive=False):
                    parse_el(child, ctx)

        ctx = []
        # start parsing at root element of the document
        parse_el(self.__doc__, ctx, True)
        self.__parsed__["items"] = ctx

        # parse for rel values
        [parse_rels(el) for el in self.__doc__.find_all(["a","link"],attrs={'rel':True})]

    ## function to get a python dictionary version of parsed microformat
    def to_dict(self, filter_by_type=None):
        if filter_by_type is None:
            return self.__parsed__
        else:
            return [x for x in self.__parsed__['items'] if x['type'] == [filter_by_type]]

    ## function to get a json version of parsed microformat
    def to_json(self, **kwargs):
        return json.dumps(self.to_dict(**kwargs))
