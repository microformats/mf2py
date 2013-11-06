import json
import html5lib

class Parser(object):
    useragent = 'mf2py - microformats2 parser for python'

    def __init__(self, *args, **kwargs):
        self.__url__ = None
        self.__doc__ = None

        if len(args) > 0:
            if type(args[0]) is file:
                # load file
                self.__doc__ = html5lib.parse(args[0])
                if len(args) > 1 and (type(args[1]) is str or type(args[1]) is unicode):
                    self.__url__ = args[1] #TODO: parse this properly
            elif type(args[0]) is str or type(args[0]) is unicode:
                pass
                # load URL

    def to_dict(self):
        return { "items": [], "rels": {} }
    
    def to_json(self):
        return json.dumps(self.to_dict())
