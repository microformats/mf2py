import sys
import bs4
import copy
import re

if sys.version < '3':
    from urlparse import urljoin
    text_type = unicode
    binary_type = str
else:
    from urllib.parse import urljoin
    text_type = str
    binary_type = bytes
    basestring = str

def get_textContent(el, replace_img=False, fix_whitespace=False, base_url=''):
    """ Get the text content of an element, replacing images by alt or src
    """

    def whitespacer(el):
        """ helper function to deal with whitespace
        """

        # replace \t \n \r by <space> in all strings
        for s in el.find_all(text=True):
            new_s = re.sub(r'\t|\n|\r', ' ', unicode(s))
            s.replace_with(new_s)

        # replace <br> by \n
        for br in el.find_all('br'):
            br.replace_with('\n')

        # add \n before a <p>
        for p in el.find_all('p'):
            p.insert_before('\n')

        text = el.get_text()
        # remove spaces before and after \n
        text = re.sub(r'[ ]{0,}\n[ ]{0,}', '\n', text)
        text = re.sub(r'[ ]{1,}', ' ', text)

        return text.strip()

    # copy el to avoid making direct changes
    el_copy = copy.copy(el)

    # drop all <style> and <script> elements
    drops = el_copy.find_all(['style', 'script'])
    for drop in drops:
        drop.decompose()

    # replace <img> with alt or src
    if replace_img:
        imgs = el_copy.find_all('img')

        for img in imgs:
            replacement = img.get('alt')
            if replacement is None:
                replacement = img.get('src')
                if replacement is not None:
                    replacement = ' ' + urljoin(base_url, replacement) + ' '

            if replacement is None:
                replacement = ''

            img.replace_with(replacement)

    if fix_whitespace:
        return whitespacer(el_copy)
    else:
        return el_copy.get_text().strip()

def get_attr(el, attr, check_name=None):
    """Get the attribute of an element if it exists and is not empty.

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


def get_children(node):
    """An iterator over the immediate children tags of this tag"""
    for child in node.contents:
        if isinstance(child, bs4.Tag):
            yield child


def get_descendents(node):
    for child in get_children(node):
        yield child
        for desc in get_descendents(child):
            yield desc
