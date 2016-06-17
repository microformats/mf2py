from .dom_helpers import get_descendents


def apply_rules(doc):
    for el in get_descendents(doc):
        if el.name == 'template':
            el.extract()
