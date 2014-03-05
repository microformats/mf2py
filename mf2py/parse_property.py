from bs4 import Tag
from dom_helpers import get_attr
from urlparse import urljoin
## functions to parse the propertis of elements

def text(el):
    # add value-class-pattern
    prop_value = get_attr(el, "title", check_name="abbr")
    if prop_value is not None:
        return prop_value

    prop_value = get_attr(el, "value", check_name=("data","input"))
    if prop_value is not None:
        return prop_value

    prop_value = get_attr(el, "alt", check_name=("img","area"))
    if prop_value is not None:
        return prop_value

    ## see if get_text() replaces img with alts
    # strip here?
    return el.get_text()

def url(el, base_url=''):
    ## do the normalise absolute url thing
    prop_value = get_attr(el, "href", check_name=("a","area"))
    if prop_value is not None:
        return urljoin(base_url, prop_value)

    prop_value = get_attr(el, "src", check_name="img")
    if prop_value is not None:
        return urljoin(base_url, prop_value)

    prop_value = get_attr(el, "data", check_name="object")
    if prop_value is not None:
        return urljoin(base_url, prop_value)

    # add value-class-pattern

    prop_value = get_attr(el, "title", check_name="abbr")
    if prop_value is not None:
        return prop_value

    prop_value = get_attr(el, "data", check_name="object")
    if prop_value is not None:
        return prop_value

    # strip here?
    return el.get_text()

def datetime(el):

    # add value-class-pattern

    prop_value = get_attr(el, "datetime", check_name=("time","ins","del"))
    if prop_value is not None:
        return prop_value

    prop_value = get_attr(el, "title", check_name="abbr")
    if prop_value is not None:
        return prop_value

    prop_value = get_attr(el, "value", check_name=("data","input"))
    if prop_value is not None:
        return prop_value

    # strip here?
    return el.get_text()

def embedded(el):

    return {
                'html': ''.join([unicode(e) for e in el.children]),
                'value': el.get_text()     # strip here?
            }
