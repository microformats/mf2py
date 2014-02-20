from bs4 import Tag as bs4Tag


## function to check if an element is a Tag or not.
def is_tag(el):
    return isinstance(el,bs4Tag)
