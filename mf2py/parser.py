import json
import html5lib
from urlparse import urlparse
import xml.dom.minidom

class Parser(object):
    useragent = 'mf2py - microformats2 parser for python'

    def __init__(self, *args, **kwargs):
        self.__url__ = None
        self.__doc__ = None
        self.__parsed__ = {"items": [], "rels": {}}

        if len(args) > 0:
            if type(args[0]) is file:
                # load file
                self.__doc__ = html5lib.parse(args[0], treebuilder="dom")
                if len(args) > 1 and (type(args[1]) is str or type(args[1]) is unicode):
                    self.__url__ = args[1] #TODO: parse this properly
            elif type(args[0]) is str or type(args[0]) is unicode:
                pass
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
            self.parse()

    def parse(self):
        def handle_microformat(microformat_name, el):
            properties = parse_props(el, {})
            if microformat_name == "h-card" and 'name' not in properties:
                properties["name"] = [el.firstChild.nodeValue]
                # TODO: replace with proper name-implied
            microformat = {"type": [microformat_name],
                           "properties": properties}
            return microformat

        def url_relative(value):
            return value

        def parse_props(el, props = {}):
            if el.hasAttribute("class"):
                classes = el.getAttribute("class").split(" ")

                # simple property parsing
                potential_simple_property_signifiers = [x for x in classes if x.startswith("p-")]
                if len(potential_simple_property_signifiers) > 0:
                    for prop in potential_simple_property_signifiers:
                        prop_name = prop.replace("p-", "")
                        prop_value = props.get(prop_name, [])
                        prop_value.append(el.firstChild.nodeValue)

                        if prop_value is not []:
                            props[prop_name] = prop_value

                # url property parsing
                potential_url_property_signifiers = [x for x in classes if x.startswith("u-")]
                if len(potential_url_property_signifiers) > 0:
                    for prop in potential_url_property_signifiers:
                        prop_name = prop.replace("u-", "")
                        prop_value = props.get(prop_name, [])

                        # el/at matching
                        url_matched = False
                        if el.nodeName == 'a' and el.hasAttribute("href"):
                            prop_value.append(url_relative(el.getAttribute("href")))
                            url_matched = True
                        elif el.nodeName == 'area' and el.hasAttribute("href"):
                            prop_value.append(url_relative(el.getAttribute("href")))
                            url_matched = True
                        elif el.nodeName == 'img' and el.hasAttribute("src"):
                            prop_value.append(url_relative(el.getAttribute("src")))
                            url_matched = True
                        elif el.nodeName == 'object' and el.hasAttribute("data"):
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

            for child in [x for x in el.childNodes if x.nodeType is 1]:
                res = parse_props(child)
                props.update(res)
            return props

        def parse_el(el, ctx):
            potential_microformats = []

            if el.hasAttribute("class"):
                classes = el.getAttribute("class").split(" ")
                potential_microformats = [x for x in classes if x.startswith("h-")]

            if len(potential_microformats) > 0:
                for microformat_name in potential_microformats:
                    result = handle_microformat(microformat_name, el)
                    ctx.append(result)

            for child in [x for x in el.childNodes if x.nodeType is 1]:
                parse_el(child, ctx)

        ctx = []
        parse_el(self.__doc__.documentElement, ctx)
        self.__parsed__["items"] = ctx

    def to_dict(self):
        return self.__parsed__
    
    def to_json(self):
        return json.dumps(self.to_dict())
