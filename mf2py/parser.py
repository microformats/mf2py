# coding: utf-8

import json
from bs4 import BeautifulSoup
import backcompat, implied_properties
import requests
from urlparse import urlparse
from dom_helpers import is_tag

class Parser(object):
    """Object to parse a document for microformats and return them in appropriate formats.

    Args
    ----
    file : file handle to file containing contents (first arg or kwarg 'doc')
    url : url of the file to be processed
            (kwarg or second arg. Can be first arg if no file given)

    Attributes
    ----------
    useragent : returns the UA string for the Parser

    Public methods
    ---------------
    parse : parses the file/url contents for microformats
    filter_by_type : returns only the microformat specified by type_name argument
    to_dict : returns python dict containing parsed microformats
    to_json : returns json formatted version of parsed microformats

    """
    useragent = 'mf2py - microformats2 parser for python'

    def __init__(self, *args, **kwargs):
        self.__url__ = None
        self.__doc__ = None
        self.__parsed__ = {"items": [], "rels": {}}

        if 'doc' in kwargs and 'url' in kwargs:
            self.__doc__ = BeautifulSoup(kwargs['doc'])
            self.__url__ = kwargs['url']
        elif 'doc' in kwargs:
            self.__doc__ = BeautifulSoup(kwargs['doc'])
        elif 'url' in kwargs:
            data = requests.get(kwargs['url'])
            self.__url__ = kwargs['url']
            self.__doc__ = BeautifulSoup(data.text)
        else:
            if len(args) > 0:
                if type(args[0]) is file:
                    # load file
                    self.__doc__ = BeautifulSoup(args[0])
                    if len(args) > 1 and (type(args[1]) is str or type(args[1]) is unicode):
                        self.__url__ = args[1] #TODO(tommorris): parse this properly
                elif type(args[0]) is str or type(args[0]) is unicode:
                    # load URL
                    data = requests.get(args[0])
                    self.__url__ = args[0]
                    self.__doc__ = BeautifulSoup(data.text)


        # test for base
        if self.__doc__ is not None and self.__url__ is None:
            poss_bases = self.__doc__.find_all("base")
            actual_base = None
            if len(poss_bases) is not 0:
                for poss_base in poss_bases:
                    # try to get href
                    if 'href' in poss_base.attrs and urlparse(poss_base['href']).netloc is not '':
                        self.__url__ = poss_base['href']

        if self.__doc__ is not None:
            # parse!
            backcompat.apply_rules(self.__doc__)
            self.parse()


    ## function to parse the document
    def parse(self):
        # finds returns elements in el having class="value" for value-class-pattern http://microformats.org/wiki/value-class-pattern
        def detect_and_handle_value_class_pattern(el):
            """Returns value-class-pattern. This may be either a string a dict or None."""
            return el.find_all(class_="value")

        # set of all parsed things
        parsed = set()

        ## function to get all root classnames
        def root_classnames(classes):
            return [c for c in classes if c.startswith("h-")]

        ##  function to get all property classnames        
        def property_classnames(classes):
            return [c for c in classes if c.startswith("p-") or c.startswith("u-") or c.startswith("e-") or c.startswith("dt-")]
   
        ## function to get names of properties from classnames i.e. without microformat prefix     
        def property_names(classes):
            return [c[2:] for c in property_classnames(classes)]

        ## (what is this?)        
        def url_relative(value):
            return value

        ## function for handling a root microformat i.e. h-*        
        def handle_microformat(root_class_names, el, is_nested=True):

            # parse for properties and children
            properties, children = parse_props(el, True)
           
            # if some properties not already found find in implied ways 
            if 'name' not in properties:
                properties["name"] = implied_properties.name(el)
                
            if "photo" not in properties:
                x = implied_properties.photo(el)
                if x is not None:
                    properties["photo"] = x

            if "url" not in properties:
                x = implied_properties.url(el)
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
                microformat["value"] = str(el)
            return microformat
        
        ## function to parse properties of element
        def parse_props(el, is_root_element=False):

            #helper functions (?)

            props = {}
            children = []
            # skip to children if this element itself is a nested microformat or it doesn’t have a class
            if "class" in el.attrs and not is_root_element:
                classes = el["class"]
                # Is this element a microformat root?
                root_class_names = root_classnames(classes)
                if len(root_class_names) > 0:
                    # this element represents a nested microformat
                    if len(property_classnames(classes)) > 0:
                        # nested microformat is property-nested, parse and add to all property lists it's part of
                        nested_microformat = handle_microformat(root_class_names, el)
                        for prop_name in property_names(classes):
                            prop_value = props.get(prop_name, [])
                            prop_value.append(nested_microformat)
                            props[prop_name] = prop_value
                    else:
                        # nested microformat is a child microformat, parse and add to children
                        children.append(handle_microformat(root_class_names, el))
                else:
                    # Parse plaintext p-* properties.
                    for prop in [c for c in classes if c.startswith("p-")]:
                        # TODO(tommorris): parse for value-class here
                        prop_name = prop[2:]
                        prop_value = props.get(prop_name, [])
                        # added string stripping
                        prop_value.append(el.get_text().strip())

                        if prop_value is not []:
                            props[prop_name] = prop_value

                    # Parse URL u-* properties.
                    for prop in [c for c in classes if c.startswith("u-")]:
                        prop_name = prop[2:]
                        prop_value = props.get(prop_name, [])

                        # el/at matching
                        url_matched = False
                        if el.name in ("a", "area") and "href" in el.attrs:
                            prop_value.append(url_relative(el["href"]))
                            url_matched = True
                        elif el.name == "img" and "src" in el.attrs:
                            prop_value.append(url_relative(el["src"]))
                            url_matched = True
                        elif el.name == "object" and "data" in el.attrs:
                            prop_value.append(url_relative(el["data"]))
                            url_matched = True

                        if url_matched is False:
                            # TODO(tommorris): value-class-pattern
                            if el.name == 'abbr' and "title" in el.attrs:
                                prop_value.append(el["title"])

                            elif el.name == 'data' and "value" in el.attrs:
                                prop_value.append(el["value"])
                            # TODO(tommorris): else, get inner text
                            pass

                        if prop_value is not []:
                            props[prop_name] = prop_value
                    
                    # Parse datetime dt-* properties.
                    for prop in [c for c in classes if c.startswith("dt-")]:
                        prop_name = prop[3:]
                        prop_value = props.get(prop_name, [])
                        
                        # TODO(barnabywalters): parse value-class pattern including datetime parsing rules.
                        # http://microformats.org/wiki/value-class-pattern
                        if el.name in ("time", "ins", "del") and "datetime" in el.attrs:
                            prop_value.append(el["datetime"])
                        elif el.name == "abbr" and "title" in el.attrs:
                            prop_value.append(el["title"])
                        elif el.name in ("data", "input") and "value" in el.attrs:
                            prop_value.append(el["value"])
                        else:
                            prop_value.append(el.get_text())
                        
                        props[prop_name] = prop_value

                    # Parse embedded markup e-* properties.
                    for prop in [c for c in classes if c.startswith("e-")]:
                        prop_name = prop[2:]
                        prop_value = props.get(prop_name, [])
                        
                        prop_value.append({
                            'html': ''.join([unicode(e) for e in el.children]),
                            'value': el.get_text()
                        })
                        
                        props[prop_name] = prop_value
            
            parsed.add(el)

            # parse children if they are tags and not already parsed
            for child in [x for x in el.children if is_tag(x) and x not in parsed]:
                child_properties, child_microformats = parse_props(child)
                for prop_name in child_properties:
                    v = props.get(prop_name, [])
                    v.extend(child_properties[prop_name])
                    props[prop_name] = v
                children.extend(child_microformats)
            
            return props, children

        ## function to parse an element for microformats
        def parse_el(el, ctx, top_level=False):
            potential_microformats = []

            classes = el.get("class",[])
            # find potential microformats in root classnames h-*
            potential_microformats = root_classnames(classes)

            # if potential microformats found parse them
            if len(potential_microformats) > 0:
                result = handle_microformat(potential_microformats, el, top_level)
                ctx.append(result)
            else:
                # parse children if they are tags and not already parsed
                for child in [x for x in el.children if is_tag(x) and x not in parsed]:
                    parse_el(child, ctx)

        ctx = []
        # start parsing at root element of the document
        parse_el(self.__doc__, ctx, True)
        self.__parsed__["items"] = ctx

    ## function to get only certain type of microformat
    def filter_by_type(self, type_name):
        return [x for x in self.to_dict()['items'] if x['type'] == [type_name]]

    ## function to get a python dictionary version of parsed microformat
    def to_dict(self):
        return self.__parsed__
    ## function to get a json version of parsed microformat    
    def to_json(self):
        return json.dumps(self.to_dict())
