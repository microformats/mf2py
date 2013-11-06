import json
import html5lib
from urlparse import urlparse
import xml.dom.minidom

class Parser(object):
    useragent = 'mf2py - microformats2 parser for python'

    def __init__(self, *args, **kwargs):
        self.__url__ = None
        self.__doc__ = None

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

    def to_dict(self):
        return { "items": [], "rels": {} }
    
    def to_json(self):
        return json.dumps(self.to_dict())
