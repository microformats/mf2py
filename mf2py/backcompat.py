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

# Classic Root Classname map
CLASSIC_ROOT_MAP = {}

# Classic Root properties map
CLASSIC_PROPERTY_MAP = {}

# populate backcompat rules from JSON files

_RULES_LOC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backcompat-rules')

for filename in os.listdir(_RULES_LOC):
    file_path = os.path.join(_RULES_LOC, filename)
    root = os.path.splitext(filename)[0]
    with codecs.open(file_path, 'r', 'utf-8') as f:
        rules = json.load(f)

    CLASSIC_ROOT_MAP[root] = rules['type'][0]
    CLASSIC_PROPERTY_MAP[root] = rules['properties']



def root(classes):
    """get all backcompat root classnames
    """
    return [c for c in classes if c in CLASSIC_ROOT_MAP]


def make_classes_rule(old_class, new_classes):
    """Builds a rule for augmenting an mf1 class with its mf2
    equivalent(s).
    """
    def f(child, **kwargs):
        child_classes = child.get('class', [])
        if old_class in child_classes:
            child_classes += [c for c in new_classes
                              if c not in child_classes]
            child['class'] = child_classes
    return f


# The RULES map has a list of rules for each root class type.
# We'll build the vast majority of it from the CLASSIC_PROPERTY_MAP
RULES = dict(
    (old_root, [make_classes_rule(old_class, new_classes)
                for old_class, new_classes in properties.items()])
    for old_root, properties in CLASSIC_PROPERTY_MAP.items())


def rel_bookmark_to_url_rule(child, **kwargs):
    """rel=bookmark gets augmented with class="u-url
    """
    child_classes = child.get('class', [])
    if ('bookmark' in child.get('rel', [])
            and 'u-url' not in child_classes):
        child_classes.append('u-url')
        child['class'] = child_classes


def rel_tag_to_category_rule(child, **kwargs):
    """rel=tag converts to p-category using a special transformation (the
    category becomes the tag href's last path segment). This rule adds a new
    data tag so that
    <a rel="tag" href="http://example.com/tags/cat"></a> gets augmented with
    <data class="p-category" value="cat"></data>
    """
    rels = child.get('rel', [])
    classes = child.get('class', [])
    if ('tag' in rels and child.get('href')
            and 'p-category' not in classes
            and 'u-category' not in classes):
        segments = [seg for seg in child.get('href').split('/') if seg]
        if segments:
            data = bs4.BeautifulSoup('<data></data>').data
            # use mf1 class here so it doesn't get removed later
            data['class'] = ['category']
            data['value'] = unquote(segments[-1])
            child.parent.append(data)


# Augment with special rules
RULES['hentry'] += [
    rel_bookmark_to_url_rule,
    rel_tag_to_category_rule,
]

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
        new_root = CLASSIC_ROOT_MAP[old_root]
        if new_root not in classes:
            el_copy['class'].append(new_root)


    # add mf2 prop equivalent to descendents and remove existing mf2 props
    rules = []
    for old_root in old_roots:
        rules.extend(RULES.get(old_root,[]))

    apply_prop_rules_to_children(el_copy, rules)

    return el_copy
