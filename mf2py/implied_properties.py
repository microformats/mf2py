from __future__ import unicode_literals, print_function
from . import mf2_classes
from .dom_helpers import get_attr
import sys

if sys.version < '3':
    from urlparse import urljoin
else:
    from urllib.parse import urljoin


def name(el):
    """Find an implied name property

    Args:
      el (bs4.element.Tag): a DOM element

    Returns:
      string: the implied name value
    """
    # if image use alt text if not empty
    prop_value = get_attr(el, "alt", check_name=("img", "area"))
    if prop_value is not None:
        return [prop_value]

    # if abbreviation use the title if not empty
    prop_value = get_attr(el, "title", check_name="abbr")
    if prop_value is not None:
        return [prop_value]

    # if only one child
    children = el.find_all(True, recursive=False)
    if len(children) == 1:
        # use alt if child is img
        prop_value = get_attr(children[0], "alt", check_name="img")
        if prop_value is not None:
            return [prop_value]

        # use title if child is abbr
        prop_value = get_attr(children[0], "title", check_name="abbr")
        if prop_value is not None:
            return [prop_value]

        grandchildren = children[0].find_all(True, recursive=False)
        # if only one grandchild
        if len(grandchildren) == 1:
            # use alt if grandchild is img
            prop_value = get_attr(grandchildren[0], "alt", check_name="img")
            if prop_value is not None:
                return [prop_value]

            # use title if grandchild is title
            prop_value = get_attr(grandchildren[0], "title", check_name="abbr")
            if prop_value is not None:
                return [prop_value]

    # use text if all else fails
    return [el.get_text().strip()]


def photo(el, base_url=''):
    """Find an implied photo property

    Args:
      el (bs4.element.Tag): a DOM element
      base_url (string): the base URL to use, to reconcile relative URLs

    Returns:
      string: the implied photo value
    """
    # if element is an image use source if exists
    prop_value = get_attr(el, "src", check_name="img")
    if prop_value is not None:
        return [urljoin(base_url, prop_value)]

    # if element is an object use data if exists
    prop_value = get_attr(el, "data", check_name="object")
    if prop_value is not None:
        return [prop_value]

    # if element has one image child use source if exists and img is
    # not root class
    poss_imgs = el.find_all("img", recursive=False)
    if len(poss_imgs) == 1:
        poss_img = poss_imgs[0]
        if mf2_classes.root(poss_img.get('class', [])) == []:
            prop_value = get_attr(poss_img, "src", check_name="img")
            if prop_value is not None:
                return [urljoin(base_url, prop_value)]

    # if element has one object child use data if exists and object is
    # not root class
    poss_objs = el.find_all("object", recursive=False)
    if len(poss_objs) == 1:
        poss_obj = poss_objs[0]
        if mf2_classes.root(poss_obj.get('class', [])) == []:
            prop_value = get_attr(poss_obj, "data", check_name="object")
            if prop_value is not None:
                return [prop_value]

    children = el.find_all(True, recursive=False)
    # if only one child then repeat above in child
    if len(children) == 1:
        # if element has one image child use source if exists and img
        # is not root class
        poss_imgs = children[0].find_all("img", recursive=False)
        if len(poss_imgs) == 1:
            poss_img = poss_imgs[0]
            if mf2_classes.root(poss_img.get('class', [])) == []:
                prop_value = get_attr(poss_img, "src", check_name="img")
                if prop_value is not None:
                    return [urljoin(base_url, prop_value)]

        # if element has one object child use data if exists and
        # object is not root class
        poss_objs = children[0].find_all("object", recursive=False)
        if len(poss_objs) == 1:
            poss_obj = poss_objs[0]
            if mf2_classes.root(poss_obj.get('class', [])) == []:
                prop_value = get_attr(poss_obj, "data", check_name="object")
                if prop_value is not None:
                    return [prop_value]


def url(el, base_url=''):
    """Find an implied url property

    Args:
      el (bs4.element.Tag): a DOM element
      base_url (string): the base URL to use, to reconcile relative URLs

    Returns:
      string: the implied url value
    """
    # if element is a link use its href if exists
    prop_value = get_attr(el, "href", check_name=("a", "area"))
    if prop_value is not None:
        return [urljoin(base_url, prop_value)]

    # if one link child use its href
    poss_as = el.find_all("a", recursive=False)
    if len(poss_as) == 1:
        poss_a = poss_as[0]
        if mf2_classes.root(poss_a.get('class', [])) == []:
            prop_value = get_attr(poss_a, "href", check_name="a")
            if prop_value is not None:
                return [urljoin(base_url, prop_value)]
