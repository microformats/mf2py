# coding: utf-8

import json
from bs4 import BeautifulSoup
import backcompat
import requests
from urlparse import urlparse

class Parser(object):
    useragent = 'mf2py - microformats2 parser for python'

    def __init__(self, *args, **kwargs):
        self.__url__ = None
        self.__doc__ = None
        self.__parsed__ = {"items": [], "rels": {}}

        if 'url' in kwargs:
            data = requests.get(kwargs['url'])
            self.__url__ = kwargs['url']
            self.__doc__ = BeautifulSoup(data.text)
        else:
            if len(args) > 0:
                if type(args[0]) is file:
                    # load file
                    self.__doc__ = BeautifulSoup(args[0])
                    if len(args) > 1 and (type(args[1]) is str or type(args[1]) is unicode):
                        self.__url__ = args[1] #TODO: parse this properly
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
            #self.__doc__.apply_backcompat_rules()
            self.parse()

    ## function to parse the document
    def parse(self):
        # finds returns elements in el having class="value" (why?)
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

            ## helper functions to parse microformat
        ## function to find an implied name property (added by Kartik)
            def implied_name(el):
                # if image use alt text if not empty
                if el.name == 'img' and "alt" in el.attrs and not el["alt"] == "":
                    return [el["alt"]]
                # if abbreviation use the title if not empty
                elif el.name == 'abbr' and "title" in el.attrs and not el["title"] == "":
                    return [el["title"]]
                # if only one image child then use alt text if not empty
                elif len(el.find_all("img")) == 1 and "alt" in el.find_all("img")[0].attrs and \
                        len(str(el.find_all("img")[0]["alt"])) > 0:
                    return [el.find_all("img")[0]["alt"]]
                # if only one abbreviation child use abbreviation if not empty
                elif len(el.find_all("abbr")) == 1 and "title" in el.find_all("abbr")[0].attrs and \
                        len(str(el.find_all("abbr")[0]["title"])) > 0:
                    return [el.find_all("abbr")[0]["title"]]
                # TODO: implement the rest of http://microformats.org/wiki/microformats2-parsing#parsing_for_implied_properties
                # use text if all else fails
                else:
                    return [el.get_text()]

            ## function to find implied photo property (added by Kartik)
            def implied_photo(el):
                # if element is an image use source if exists
                if el.name == 'img' and "src" in el.attrs:
                    return [el["src"]]
                # if element has one image child use source if exists (check existence of src?)
                elif len(el.find_all("img")) == 1 and "src" in el.find_all("img")[0].attrs :
                    return [el.find_all("img")[0]["src"]]
                # TODO: implement the other implied photo finders from http://microformats.org/wiki/microformats2-parsing#parsing_for_implied_properties
                else:
                    return None

            ## function to find implied url (added by Kartik)
            def implied_url(el):
                # if element is a link use its href if exists
                if el.name == 'a' and "href" in el.attrs:
                    return el["href"]
                # if one link child use its href 
                elif len(el.find_all("a")) == 1 and "href" in el.find_all("a")[0].attrs and root_classnames(el.find_all("a")[0].get('class',[])) == []:
                        return el.find_all("a")[0]["href"]
                else:
                    return None    

            # actual parsing of microformat
            # parse for properties and children
            properties, children = parse_props(el, True)
           
            # if some properties not already found find in implied ways 
            if 'name' not in properties:
                properties["name"] = impled_name()
                
            if "photo" not in properties:
                x = implied_photo()
                if x is not None:
                    properties["photo"] = x

            if "url" not in properties:
                x = implied_url()
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
                        # TODO: parse for value-class here
                        prop_name = prop[2:]
                        prop_value = props.get(prop_name, [])
                        prop_value.append(el.get_text())

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
                            # TODO: value-class-pattern
                            if el.name == 'abbr' and "title" in el.attrs:
                                prop_value.append(el["title"])

                            elif el.name == 'data' and "value" in el.attrs:
                                prop_value.append(el["value"])
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
            
            for child in [x for x in el.children if x not in parsed]:
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
                # parse children (add description for conditionals)
                for child in [x for x in el.children if x not in parsed]:
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
