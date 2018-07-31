from __future__ import unicode_literals

import sys
import bs4
import copy
import re
import string

from bs4.element import Tag, NavigableString, Comment, NamespacedAttribute

if sys.version < '3':
    from urlparse import urljoin
    text_type = unicode
    binary_type = str
else:
    from urllib.parse import urljoin
    text_type = str
    binary_type = bytes
    basestring = str

def get_attr(el, attr, check_name=None):
    """Get the attribute of an element if it exists.

    Args:
      el (bs4.element.Tag): a DOM element
      attr (string): the attribute to get
      check_name (string or list, optional): a list/tuple of strings or single
        string, that must match the element's tag name

    Returns:
      string: the attribute's value
    """
    if check_name is None:
        return el.get(attr)
    if isinstance(check_name, basestring) and el.name == check_name:
        return el.get(attr)
    if isinstance(check_name, (tuple, list)) and el.name in check_name:
        return el.get(attr)


def get_img_src_alt(img, dict_class, img_with_alt, base_url=''):
    """given a img element, returns both src and alt attributes as a list of tuples if alt exists, else returns the src as a string
    use for alt parsing with img
    """

    alt = get_attr(img, "alt", check_name="img")
    src = get_attr(img, "src", check_name="img")

    if src is not None:
        src = urljoin(base_url, src)

        if alt is None or not img_with_alt:
            return text_type(src)
        else:
            return dict_class([
                                ("value", text_type(src)),
                                ("alt", text_type(alt))
                            ])

def get_children(node):
    """An iterator over the immediate children tags of this tag"""
    for child in node.children:
        if isinstance(child, bs4.Tag):
            yield child


def get_descendents(node):
    """An iterator over the all children tags (descendants) of this tag"""
    for desc in node.descendants:
        if isinstance(desc, bs4.Tag):
            yield desc

def get_textContent(el, replace_img=False, img_to_src=True, base_url=''):
    """ Get the text content of an element, replacing images by alt or src
    """

    DROP_TAGS = ('script', 'style')
    PRE_TAGS = ('pre',)
    P_BREAK_BEFORE = 1
    P_BREAK_AFTER = 0
    PRE_BEFORE = 2
    PRE_AFTER = 3

    def text_collection(el, replace_img=False, img_to_src=True, base_url=''):
        # returns array of strings or integers

        items = []

        # drops the tags defined above and comments
        if el.name in DROP_TAGS or isinstance(el, Comment):
            items = []

        elif isinstance(el, NavigableString):
            value = text_type(el)
            # replace \t \n \r by space
            value = re.sub(r'\t|\n|\r', ' ', value)
            # replace multiple spaces with one space
            value = re.sub(r'[ ]{1,}', ' ', value)
            items = [value]

        # don't do anything special for PRE-formatted tags defined above
        elif el.name in PRE_TAGS:
            items = [PRE_BEFORE, el.get_text(), PRE_AFTER]

        elif el.name == 'img' and replace_img:
            value = el.get('alt')
            if value is None and img_to_src:
                value = el.get('src')
                if value is not None:
                    value = urljoin(base_url, value)

            if value is not None:
                items = [' ', text_type(value), ' ']

        elif el.name == 'br':
            items = ['\n']

        else:
            for child in el.children:

                child_items = text_collection(child, replace_img, img_to_src, base_url)
                items.extend(child_items)

            if el.name == 'p':
                items = [P_BREAK_BEFORE] + items
                items.append(P_BREAK_AFTER)


        return items

    results = [t for t in text_collection(el, replace_img, img_to_src, base_url) if t is not '']

    if results:
        # remove <space> if it is first and last or if it is preceded by a <space> or <p> open/close
        length = len(results)
        for i in range(0, length):
            if (results[i] == ' ' and
                    (i == 0 or
                    i == length - 1 or
                    results[i-1] == ' ' or
                    results[i-1] in (P_BREAK_BEFORE, P_BREAK_AFTER) or
                    results[i+1] == ' ' or
                    results[i+1] in (P_BREAK_BEFORE, P_BREAK_AFTER)
                    )
                ):
                results[i] = ''

    if results:
        # remove leading whitespace and <int> i.e. next lines
        while ((isinstance(results[0], basestring) and re.match(r'^\s*$', results[0])) or
               results[0] in (P_BREAK_BEFORE, P_BREAK_AFTER)):
            results.pop(0)
            if not results:
                break

    if results:
        # remove trailing whitespace and <int> i.e. next lines
        while ((isinstance(results[-1], basestring) and re.match(r'^\s*$', results[-1])) or
               results[-1] in (P_BREAK_BEFORE, P_BREAK_AFTER)):
            results.pop(-1)
            if not results:
                break

    # trim leading and trailing non-<pre> whitespace
    if results:
        if isinstance(results[0], basestring):
            results[0] = results[0].lstrip()
        if isinstance(results[-1], basestring):
            results[-1] = results[-1].rstrip()

    # create final string by concatenating replacing consecutive sequence of <int> by largest value number of \n
    text = ''
    count = 0
    last = None
    for t in results:
        if t in (P_BREAK_BEFORE, P_BREAK_AFTER):
            count = max(t, count)
        elif t == PRE_BEFORE:
            text = text.rstrip(' ')
        elif not isinstance(t, int):
            if count or last == '\n':
                t = t.lstrip(' ')
            text = ''.join([text, '\n'*count , t])
            count = 0
        last = t

    return text

def deepcopy_tag(tag):
    """Create deep copy of a Tag element:

    Args:
      tag (bs4.element.Tag): a Tag to copy

    Returns:
      bs4.element.Tag: a unconnected copy of tag"""

    # This function is based on Tag.__copy__() in BS4,
    # also under MIT license,  Copyright (c) 2004-2016 Leonard Richardson
    # It only exists as a workaround since the source function is missing a deepcopy and not handling all cases
    # and potentially can be removed in the future

    attrs = {}
    for key, value in tag.attrs.items():
        if isinstance(key, NamespacedAttribute):
            attrs[NamespacedAttribute(key.prefix,key.name,key.namespace)] = copy.deepcopy(value)
        else:
            attrs[key] = copy.deepcopy(value)

    clone = type(tag)(None, tag.builder, tag.name, tag.namespace,
                           tag.prefix, attrs, is_xml=tag._is_xml)
    
    for attr in ('can_be_empty_element', 'hidden'):
        setattr(clone, attr, getattr(tag, attr))
        
    for child in tag.contents:
        if isinstance(child, Tag):
            clone.append(deepcopy_tag(child))
        else:
            #NavigableString's have a __copy__() set up
            clone.append(copy.copy(child))
        
    return clone

