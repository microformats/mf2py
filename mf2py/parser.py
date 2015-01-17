# coding: utf-8

import json
from bs4 import BeautifulSoup

import requests

from .dom_helpers import get_attr
from . import backcompat, mf2_classes, implied_properties, parse_property, temp_fixes

import sys
if sys.version < '3':
    from urlparse import urlparse, urljoin
else:
    from urllib.parse import urlparse, urljoin


class Parser(object):
    """Object to parse a document for microformats and return them in
    appropriate formats.

    Keyword arguments
    ----
    doc : file handle, text of content to parse, or BeautifulSoup document.
          Optionally fetched from given 'url' kwarg
    url : url of the file to be processed. Optionally fetched from
          base-element of given 'doc' kwarg

    Attributes
    ----------
    useragent : returns the User-Agent string for the Parser

    Public methods
    ---------------
    parse : parses the file/url contents for microformats. done automatically
            on initialisation.
    filter_by_type : returns only the microformat specified by type_name
                     argument
    to_dict : returns python dict containing parsed microformats
    to_json : returns json formatted version of parsed microformats

    """
    useragent = 'mf2py - microformats2 parser for python'

    def __init__(self, *args, **kwargs):
        self.__url__ = None
        self.__doc__ = None
        self.__parsed__ = {"items": [], "rels": {}}

        if 'doc' in kwargs:
            self.__doc__ = kwargs['doc']
            if not isinstance(self.__doc__, BeautifulSoup):
                self.__doc__ = BeautifulSoup(self.__doc__)

        if 'url' in kwargs:
            self.__url__ = kwargs['url']

            if self.__doc__ is None:
                data = requests.get(self.__url__)

                # check for charater encodings and use 'correct' data
                if 'charset' in data.headers.get('content-type', ''):
                    self.__doc__ = BeautifulSoup(data.text)
                else:
                    self.__doc__ = BeautifulSoup(data.content)

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
            temp_fixes.apply_rules(self.__doc__)
            backcompat.apply_rules(self.__doc__)
            self.parse()


    ## function to parse the document
    def parse(self):
        self._default_date = None


        ## function for handling a root microformat i.e. h-*
        def handle_microformat(root_class_names, el, simple_value=None):
            properties = {}
            children = []
            self._default_date = None

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
            if str(el.name) == "area":
                shape = get_attr(el, 'shape')
                if shape is not None:
                    microformat['shape'] = shape

                coords = get_attr(el, 'coords')
                if coords is not None:
                    microformat['coords'] = coords

            # insert children if any
            if children:
                microformat["children"] = children
            # simple value is the parsed property value if it were not
            # an h-* class
            if simple_value is not None:
                microformat["value"] = simple_value
            return microformat

        ## function to parse properties of element
        def parse_props(el):
            props = {}
            children = []

            classes = el.get("class", [])
            # Is this element a microformat root?
            root_class_names = mf2_classes.root(classes)
            # Is this a property element (p-*, u-*, etc.)
            is_property_el = False

            # Parse plaintext p-* properties.
            p_value = None
            for prop_name in mf2_classes.text(classes):
                is_property_el = True
                prop_value = props.setdefault(prop_name, [])

                # if value has not been parsed then parse it
                if p_value is None:
                    p_value = parse_property.text(el).strip()

                if root_class_names:
                    prop_value.append(
                        handle_microformat(root_class_names, el, p_value))
                else:
                    prop_value.append(p_value)

            # Parse URL u-* properties.
            u_value = None
            for prop_name in mf2_classes.url(classes):
                is_property_el = True
                prop_value = props.setdefault(prop_name, [])

                # if value has not been parsed then parse it
                if u_value is None:
                    u_value = parse_property.url(el, base_url=self.__url__)

                if root_class_names:
                    prop_value.append(
                        handle_microformat(root_class_names, el, u_value))
                else:
                    prop_value.append(u_value)

            # Parse datetime dt-* properties.
            dt_value = None
            for prop_name in mf2_classes.datetime(classes):
                is_property_el = True
                prop_value = props.setdefault(prop_name, [])

                # if value has not been parsed then parse it
                if dt_value is None:
                    dt_value, new_date = parse_property.datetime(
                        el, self._default_date)
                    # update the default date
                    if new_date:
                        self._default_date = new_date

                if root_class_names:
                    prop_value.append(
                        handle_microformat(root_class_names, el, dt_value))
                else:
                    prop_value.append(dt_value)

            # Parse embedded markup e-* properties.
            e_value = None
            for prop_name in mf2_classes.embedded(classes):
                is_property_el = True
                prop_value = props.setdefault(prop_name, [])

                # if value has not been parsed then parse it
                if e_value is None:
                    e_value = parse_property.embedded(el)

                if root_class_names:
                    prop_value.append(
                        handle_microformat(root_class_names, el, e_value))
                else:
                    prop_value.append(e_value)

            # if this is not a property element, but it is a h-* microformat,
            # add it to our list of children
            if not is_property_el and root_class_names:
                children.append(handle_microformat(root_class_names, el))

            # parse child tags, provided this isn't a microformat root-class
            if not root_class_names:
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


        ## function to parse the top-level microformats element
        def parse_el(el, ctx, top_level=False):

            classes = el.get("class", [])

            # Workaround for bs4+html5lib bug that
            # prevents it from recognizing multi-valued
            # attrs on the <html> element
            # https://bugs.launchpad.net/beautifulsoup/+bug/1296481
            if el.name == 'html' and not isinstance(classes, list):
                classes = classes.split()

            # find potential microformats in root classnames h-*
            potential_microformats = mf2_classes.root(classes)

            # if potential microformats found parse them
            if potential_microformats:
                result = handle_microformat(potential_microformats, el)
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
        for el in self.__doc__.find_all(["a", "link"],attrs={'rel': True}):
            parse_rels(el)

    ## function to get a python dictionary version of parsed microformat
    def to_dict(self, filter_by_type=None):
        if filter_by_type is None:
            return self.__parsed__
        else:
            return [x for x in self.__parsed__['items'] if x['type'] == [filter_by_type]]

    ## function to get a json version of parsed microformat
    def to_json(self, **kwargs):

        if kwargs.pop('pretty_print', False):
            return json.dumps(self.to_dict(**kwargs), indent=4, separators=(', ', ': '))
        else:
            return json.dumps(self.to_dict(**kwargs))
