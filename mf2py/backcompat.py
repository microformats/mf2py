# coding: utf-8
"""Looks for classic microformats class names and augments them with
microformats2 names. Ported and adapted from php-mf2.
"""

from __future__ import unicode_literals, print_function
from .dom_helpers import get_descendents
from . import mf2_classes
import bs4
import copy
import os
import codecs
import json

import sys
if sys.version < '3':
    from urllib import unquote
else:
    from urllib.parse import unquote

# Classic map
_CLASSIC_MAP = {}

# populate backcompat rules from JSON files

_RULES_LOC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backcompat-rules')

for filename in os.listdir(_RULES_LOC):
    file_path = os.path.join(_RULES_LOC, filename)
    root = os.path.splitext(filename)[0]
    with codecs.open(file_path, 'r', 'utf-8') as f:
        rules = json.load(f)

    _CLASSIC_MAP[root] = rules 


def _make_classes_rule(old_class, new_classes):
    """Builds a rule for augmenting an mf1 class with its mf2
    equivalent(s).
    """
    def f(child, **kwargs):
        child_classes = child.get('class', [])
        if old_class in child_classes:
            child_classes.extend(new_classes)
            child['class'] = child_classes
    return f

def _rel_tag_to_category_rule(child, **kwargs):
    """rel=tag converts to p-category using a special transformation (the
    category becomes the tag href's last path segment). This rule adds a new data tag so that
    <a rel="tag" href="http://example.com/tags/cat"></a> gets replaced with
    <data class="p-category" value="cat"></data>
    """

    href = child.get('href', '')
    if 'tag' in child.get('rel', []) and href:
        segments = [seg for seg in href.split('/') if seg]
        if segments:
            data = bs4.BeautifulSoup('').new_tag('data')
            # this does not use what's given in the JSON
            data['class'] = ['p-category']
            data['value'] = unquote(segments[-1])
            child.replace_with(data)


def _make_rels_rule(old_rel, new_classes):
    """Builds a rule for augmenting an mf1 rel with its mf2 class equivalent(s).
    """

    # need to special case rel=tag as it operates differently

    def f(child, **kwargs):
        child_rels = child.get('rel', [])
        child_classes = child.get('class', [])
        if old_rel in child_rels:
            if old_rel == 'tag':
                _rel_tag_to_category_rule(child, **kwargs)
            else:
                child_classes.extend(new_classes)
                child['class'] = child_classes
    return f


def _get_rules(old_root):
    """ for given mf1 root get the rules as a list of functions to act on children """

    class_rules = [_make_classes_rule(old_class, new_classes)
                for old_class, new_classes in _CLASSIC_MAP[old_root].get('properties', {}).items()]
    rel_rules = [_make_rels_rule(old_rel, new_classes)
                for old_rel, new_classes in _CLASSIC_MAP[old_root].get('rels', {}).items()]

    return class_rules + rel_rules

def apply_rules(el):
    """add modern classnames for older mf1 classnames

    returns a copy of el and does not modify the original
    """

    el_copy = copy.copy(el)

    def apply_prop_rules_to_children(parent, rules):

        for child in (c for c in parent.children if isinstance(c, bs4.Tag)):
            classes = child.get('class',[])
            # find existing mf2 properties if any and delete them
            mf2_props = mf2_classes.property_classes(classes)
            child['class'] = [cl for cl in classes if cl not in mf2_props]

            # apply rules to change mf1 to mf2
            for rule in rules:
                rule(child)

            # recurse if it's not a nested mf1 or mf2 root
            if not (mf2_classes.root(classes) or root(classes)):
                apply_prop_rules_to_children(child, rules)


    # add mf2 root equivalent
    classes = el_copy.get('class', [])
    old_roots = root(classes)
    for old_root in old_roots:
        new_roots = _CLASSIC_MAP[old_root]['type']
        classes.extend(new_roots)
    el_copy['class'] = classes


    # add mf2 prop equivalent to descendents and remove existing mf2 props
    rules = []
    for old_root in old_roots:
        rules.extend(_get_rules(old_root))

    apply_prop_rules_to_children(el_copy, rules)

    return el_copy

def root(classes):
    """get all backcompat root classnames
    """
    return [c for c in classes if c in _CLASSIC_MAP]
