from bs4 import Tag as bs4Tag


## function to check if an element is a Tag or not.
def is_tag(el):
    return isinstance(el,bs4Tag)

def get_attr(el, attr, check_name=None ):
    """returns the attribute of an element if it exists and is not empty else returns None. Optional kwarg 'check_name' (as a list of strings or single string) to check element type by name
    """
    if check_name is None:
        attr_value = el.get(attr, None)
    elif el.name in check_name:
        attr_value = el.get(attr, None)
    else:
        attr_value = None

    if isinstance(attr_value, str) or isinstance(attr_value, unicode):
        if attr_value.strip() == "":
            attr_value = None

    return attr_value
