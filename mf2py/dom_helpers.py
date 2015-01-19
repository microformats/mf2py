import sys
if sys.version < '3':
    text_type = unicode
    binary_type = str
else:
    text_type = str
    binary_type = bytes
    basestring = str


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
        attr_value = el.get(attr, None)
    elif isinstance(check_name, basestring) and el.name == check_name:
        attr_value = el.get(attr, None)
    elif ((isinstance(check_name, tuple) or isinstance(check_name, list))
          and el.name in check_name):
        attr_value = el.get(attr, None)
    else:
        attr_value = None

    if (isinstance(attr_value, text_type)
            or isinstance(attr_value, binary_type)):
        if attr_value.strip() == "":
            attr_value = None

    return attr_value
