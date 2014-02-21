# coding: utf-8

import json
import html5lib
import dom_addins
import backcompat
import requests
from urlparse import urlparse
import xml.dom.minidom

class Parser(object):
    useragent = 'mf2py - microformats2 parser for python'

    def __init__(self, *args, **kwargs):
        self.__url__ = None
        self.__doc__ = None
        self.__parsed__ = {"items": [], "rels": {}}

        if 'doc' in kwargs and 'url' in kwargs:
            self.__doc__ = html5lib.parse(kwargs['doc'], treebuilder="dom")
            self.__url__ = kwargs['url']
        elif 'doc' in kwargs:
            self.__doc__ = html5lib.parse(kwargs['doc'], treebuilder="dom")
        elif 'url' in kwargs:
            data = requests.get(kwargs['url'])
            self.__url__ = kwargs['url']
            self.__doc__ = html5lib.parse(data.text, treebuilder="dom")
        else:
            if len(args) > 0:
                if type(args[0]) is file:
                    # load file
                    self.__doc__ = html5lib.parse(args[0], treebuilder="dom")
                    if len(args) > 1 and (type(args[1]) is str or type(args[1]) is unicode):
                        self.__url__ = args[1] #TODO: parse this properly
                elif type(args[0]) is str or type(args[0]) is unicode:
                    data = requests.get(args[0])
                    self.__url__ = args[0]
                    self.__doc__ = html5lib.parse(data.text, treebuilder="dom")
                    # load URL

        # test for base
        if self.__doc__ is not None and self.__url__ is None:
            poss_bases = self.__doc__.getElementsByTagName("base")
            actual_base = None
            if len(poss_bases) is not 0:
                for poss_base in poss_bases:
                    if poss_base.hasAttribute("href"):
                        # check to see if absolute
                        if urlparse(poss_base.getAttribute("href")).netloc is not '':
                            self.__url__ = poss_base.getAttribute("href")

        if self.__doc__ is not None:
            # parse!
            self.__doc__.documentElement.apply_backcompat_rules()
            self.parse()

    def parse(self):
        def detect_and_handle_value_class_pattern(el):
            """Returns value-class-pattern. This may be either a string a dict or None."""
            return [x for x in el.getElementsByClassName("value")]

        parsed = set()
        
        def property_classnames(classes):
            return [c for c in classes if c.startswith("p-") or c.startswith("u-") or c.startswith("e-") or c.startswith("dt-")]
        
        def property_names(classes):
            return [c[2:] for c in property_classnames(classes)]
        
        def url_relative(value):
            return value
        
        def handle_microformat(root_classnames, el, is_nested=True):
            properties, children = parse_props(el, True)
            
            if 'name' not in properties:
                if el.nodeName == 'img' and el.hasAttribute("alt") and not el.getAttribute("alt") == "":
                    properties["name"] = [el.getAttribute("alt")]
                elif el.nodeName == 'abbr' and el.hasAttribute("title") and not el.getAttribute("title") == "":
                    properties["name"] = [el.getAttribute("title")]
                elif len(el.getElementsByTagName("img")) == 1 and el.getElementsByTagName("img")[0].hasAttribute("alt") and \
                        len(str(el.getElementsByTagName("img")[0].getAttribute("alt"))) > 0:
                    properties["name"] = [el.getElementsByTagName("img")[0].getAttribute("alt")]
                elif len(el.getElementsByTagName("abbr")) == 1 and el.getElementsByTagName("abbr")[0].hasAttribute("title") and \
                        len(str(el.getElementsByTagName("title"))) > 0:
                    properties["name"] = [el.getElementsByTagName("abbr")[0].getAttribute("abbr")]
                # TODO: implement the rest of http://microformats.org/wiki/microformats2-parsing#parsing_for_implied_properties
                else:
                    properties["name"] = [el.getText()]
            
            if "photo" not in properties:
                if el.nodeName == 'img' and el.hasAttribute("src"):
                    properties["photo"] = [el.getAttribute("src")]
                elif len(el.getElementsByTagName("img")) == 1:
                    properties["photo"] = [el.getElementsByTagName("img")[0].getAttribute("src")]
                # TODO: implement the other implied photo finders
            
            if "url" not in properties:
                if el.nodeName == 'a' and el.hasAttribute("href"):
                    properties["url"] = [el.getAttribute("href")]
                else:
                    possible_links = el.getElementsByTagName("a")
                    possible_links = [x for x in el.getElementsByTagName("a") if x.hasAttribute("href") and not x.hasClassName(lambda x: x.startswith("h-"))]
                    if len(possible_links) == 1:
                        properties["url"] = [possible_links[0].getAttribute("href")]
            microformat = {"type": root_classnames,
                           "properties": properties}
            if len(children) > 0:
                microformat["children"] = children
            if is_nested:
                microformat["value"] = str(el)
            return microformat
        
        def parse_props(el, is_root_element=False):
            props = {}
            children = []
            # skip to children if this element itself is a nested microformat or it doesn’t have a class
            if el.hasAttribute("class") and not is_root_element:
                # TODO: make this handle multiple spaces, tabs(?) separating classnames
                classes = el.getAttribute("class").split(" ")
                
                # Is this element a microformat root?
                root_classnames = [c for c in classes if c.startswith("h-")]
                if len(root_classnames) > 0:
                    # this element represents a nested microformat
                    if len(property_classnames(classes)) > 0:
                        # nested microformat is property-nested, parse and add to all property lists it's part of
                        nested_microformat = handle_microformat(root_classnames, el)
                        for prop_name in property_names(classes):
                            prop_value = props.get(prop_name, [])
                            prop_value.append(nested_microformat)
                            props[prop_name] = prop_value
                    else:
                        # nested microformat is a child microformat, parse and add to children
                        children.append(handle_microformat(root_classnames, el))
                else:
                    # Parse plaintext p-* properties.
                    for prop in [c for c in classes if c.startswith("p-")]:
                        # TODO: parse for value-class here
                        prop_name = prop[2:]
                        prop_value = props.get(prop_name, [])
                        # TODO: this is a goddamn horror show right here
                        text_value = " ".join(t.nodeValue for t in el.childNodes if t.nodeType == t.TEXT_NODE)
                        text_value = text_value.strip()
                        prop_value.append(text_value)

                        if prop_value is not []:
                            props[prop_name] = prop_value

                    # Parse URL u-* properties.
                    for prop in [c for c in classes if c.startswith("u-")]:
                        prop_name = prop[2:]
                        prop_value = props.get(prop_name, [])

                        # el/at matching
                        url_matched = False
                        if el.nodeName in ("a", "area") and el.hasAttribute("href"):
                            prop_value.append(url_relative(el.getAttribute("href")))
                            url_matched = True
                        elif el.nodeName == "img" and el.hasAttribute("src"):
                            prop_value.append(url_relative(el.getAttribute("src")))
                            url_matched = True
                        elif el.nodeName == "object" and el.hasAttribute("data"):
                            prop_value.append(url_relative(el.getAttribute("data")))
                            url_matched = True

                        if url_matched is False:
                            # TODO: value-class-pattern
                            if el.nodeName == 'abbr' and el.hasAttribute("title"):
                                prop_value.append(el.getAttribute("title"))
                            elif el.nodeName == 'data' and el.hasAttribute("value"):
                                prop_value.append(el.getAttribute("value"))
                            # TODO: else, get inner text
                            pass

                        if prop_value is not []:
                            props[prop_name] = prop_value
                    
                    # Parse datetime dt-* properties.
                    for prop in [c for c in classes if c.startswith("dt-")]:
                        prop_name = prop[3:]
                        prop_value = props.get(prop_name, [])
                        
                        # TODO: parse value-class pattern including datetime parsing rules.
                        # http://microformats.org/wiki/value-class-pattern
                        
                        if el.nodeName in ("time", "ins", "del") and el.hasAttribute("datetime"):
                            prop_value.append(el.getAttribute("datetime"))
                        elif el.nodeName == "abbr" and el.hasAttribute("title"):
                            prop_value.append(el.getAttribute("title"))
                        elif el.nodeName in ("data", "input") and el.hasAttribute("value"):
                            prop_value.append(el.getAttribute("value"))
                        else:
                            prop_value.append(el.firstChild.nodeValue)
                        
                        props[prop_name] = prop_value

                    # Parse embedded markup e-* properties.
                    for prop in [c for c in classes if c.startswith("e-")]:
                        prop_name = prop[2:]
                        prop_value = props.get(prop_name, [])
                        
                        prop_value.append({
                            'html': ''.join([e.toxml() for e in el.childNodes]),
                            'value': el.getText()
                        })
                        
                        props[prop_name] = prop_value
            
            parsed.add(el)
            
            for child in [x for x in el.childNodes if x.nodeType is 1 and x not in parsed]:
                child_properties, child_microformats = parse_props(child)
                for prop_name in child_properties:
                    v = props.get(prop_name, [])
                    v.extend(child_properties[prop_name])
                    props[prop_name] = v
                children.extend(child_microformats)
            
            return props, children

        def parse_el(el, ctx, top_level=False):
            potential_microformats = []

            if el.hasAttribute("class"):
                classes = el.getAttribute("class").split(" ")
                potential_microformats = [x for x in classes if x.startswith("h-")]

            if len(potential_microformats) > 0:
                result = handle_microformat(potential_microformats, el, top_level)
                ctx.append(result)
            else:
                for child in [x for x in el.childNodes if x.nodeType is 1 and x not in parsed]:
                    parse_el(child, ctx)

        ctx = []
        parse_el(self.__doc__.documentElement, ctx, True)
        self.__parsed__["items"] = ctx

    def filter_by_type(self, type_name):
        return [x for x in self.to_dict()['items'] if x['type'] == [type_name]]

    def to_dict(self):
        return self.__parsed__
    
    def to_json(self):
        return json.dumps(self.to_dict())
