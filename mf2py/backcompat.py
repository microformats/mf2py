# coding: utf-8
"""Looks for classic microformats class names and augments them with
microformats2 names. Ported and adapted from php-mf2.
"""

from __future__ import unicode_literals, print_function
from .dom_helpers import get_descendents
import bs4

import sys
if sys.version < '3':
    from urllib import unquote
else:
    from urllib.parse import unquote


# Classic Root Classname map
CLASSIC_ROOT_MAP = {
    'vcard': 'h-card',
    'hfeed': 'h-feed',
    'hentry': 'h-entry',
    'hrecipe': 'h-recipe',
    'hresume': 'h-resume',
    'vevent': 'h-event',
    'hreview': 'h-review',
    'hproduct': 'h-product',
    'hreview-aggregate': 'h-review-aggregate',
    'geo': 'h-geo',
    'adr': 'h-adr',
}

CLASSIC_PROPERTY_MAP = {
    'vcard': {
        'fn': ['p-name'],
        'url': ['u-url'],
        'honorific-prefix': ['p-honorific-prefix'],
        'given-name': ['p-given-name'],
        'additional-name': ['p-additional-name'],
        'family-name': ['p-family-name'],
        'honorific-suffix': ['p-honorific-suffix'],
        'nickname': ['p-nickname'],
        'email': ['u-email'],
        'logo': ['u-logo'],
        'photo': ['u-photo'],
        'url': ['u-url'],
        'uid': ['u-uid'],
        'category': ['p-category'],
        'adr': ['p-adr', 'h-adr'],
        'extended-address': ['p-extended-address'],
        'street-address': ['p-street-address'],
        'locality': ['p-locality'],
        'region': ['p-region'],
        'postal-code': ['p-postal-code'],
        'country-name': ['p-country-name'],
        'label': ['p-label'],
        'geo': ['p-geo', 'h-geo'],
        'latitude': ['p-latitude'],
        'longitude': ['p-longitude'],
        'tel': ['p-tel'],
        'note': ['p-note'],
        'bday': ['dt-bday'],
        'key': ['u-key'],
        'org': ['p-org'],
        'organization-name': ['p-organization-name'],
        'organization-unit': ['p-organization-unit'],
    },
    'hentry': {
        'entry-title': ['p-name'],
        'entry-summary': ['p-summary'],
        'entry-content': ['e-content'],
        'published': ['dt-published'],
        'updated': ['dt-updated'],
        'author': ['p-author', 'h-card'],
        'category': ['p-category'],
        'geo': ['p-geo', 'h-geo'],
        'latitude': ['p-latitude'],
        'longitude': ['p-longitude'],
    },
    'hrecipe': {
        'fn': ['p-name'],
        'ingredient': ['p-ingredient'],
        'yield': ['p-yield'],
        'instructions': ['e-instructions'],
        'duration': ['dt-duration'],
        'nutrition': ['p-nutrition'],
        'photo': ['u-photo'],
        'summary': ['p-summary'],
        'author': ['p-author', 'h-card'],
    },
    'hresume': {
        'summary': ['p-summary'],
        'contact': ['h-card', 'p-contact'],
        'education': ['h-event', 'p-education'],
        'experience': ['h-event', 'p-experience'],
        'skill': ['p-skill'],
        'affiliation': ['p-affiliation', 'h-card'],
    },
    'vevent': {
        'dtstart': ['dt-start'],
        'dtend': ['dt-end'],
        'duration': ['dt-duration'],
        'description': ['p-description'],
        'summary': ['p-name'],
        'url': ['u-url'],
        'category': ['p-category'],
        'location': ['p-location'],
        'geo': ['p-location h-geo'],
        'attendee': ['p-attendee'],
        'contact': ['p-contact'],
        'organizer': ['p-organizer'],
    },
    'hreview': {
        'summary': ['p-name'],
        # doesn't work properly, see spec
        'fn': ['p-item', 'h-item', 'p-name'],
        # of the item being reviewed (p-item h-item u-photo)
        'photo': ['u-photo'],
        # of the item being reviewed (p-item h-item u-url)
        'url': ['u-url'],
        'reviewer': ['p-reviewer', 'p-author', 'h-card'],
        'dtreviewed': ['dt-reviewed'],
        'rating': ['p-rating'],
        'best': ['p-best'],
        'worst': ['p-worst'],
        'description': ['p-description'],
    },
    'hproduct': {
        'fn': ['p-name'],
        'photo': ['u-photo'],
        'brand': ['p-brand'],
        'category': ['p-category'],
        'description': ['p-description'],
        'identifier': ['u-identifier'],
        'url': ['u-url'],
        'review': ['p-review', 'h-review', 'e-description'],
        'price': ['p-price'],
    },
    'hreview-aggregate': {
        'summary': ['p-name'],
        # doesn't work properly, see spec
        'fn': ['p-item', 'h-item', 'p-name'],
        # of the item being reviewed (p-item h-item u-photo)
        'photo': ['u-photo'],
        # of the item being reviewed (p-item h-item u-url)
        'url': ['u-url'],
        'reviewer': ['p-reviewer', 'p-author', 'h-card'],
        'dtreviewed': ['dt-reviewed'],
        'rating': ['p-rating'],
        'best': ['p-best'],
        'worst': ['p-worst'],
        'description': ['p-description'],
        'count': ['p-count'],
        'votes': ['p-votes']
    },
    'geo': {
        'latitude': ['p-latitude'],
        'longitude': ['p-longitude'],
    },
    'adr': {
        'post-office-box': ['p-post-office-box'],
        'extended-address': ['p-extended-address'],
        'street-address': ['p-street-address'],
        'locality': ['p-locality'],
        'region': ['p-region'],
        'postal-code': ['p-postal-code'],
        'country-name': ['p-country-name'],
    },
}

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


def rel_tag_to_category_rule(child, doc, **kwargs):
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
            data = doc.new_tag('data')
            data['class'] = ['p-category']
            data['value'] = unquote(segments[-1])
            child.parent.append(data)


# Augment with special rules
RULES['hentry'] += [
    rel_bookmark_to_url_rule,
    rel_tag_to_category_rule,
]


def apply_rules(doc):
    """add modern classnames for older mf classnames

    modifies BeautifulSoup document in-place
    """
    def apply_rules_to_children(parent, rules):
        for child in (c for c in parent.children if isinstance(c, bs4.Tag)):
            for rule in rules:
                rule(child, doc=doc)
            # recurse if it's not a nested root
            if not any(cls in CLASSIC_ROOT_MAP
                       for cls in child.get('class', [])):
                apply_rules_to_children(child, rules)

    for el in get_descendents(doc):
        if any(cls in CLASSIC_ROOT_MAP for cls in el.get('class', [])):
            for old_root in el.get('class', []):
                if old_root in CLASSIC_ROOT_MAP:
                    new_root = CLASSIC_ROOT_MAP[old_root]
                    if new_root not in el.get('class', []):
                        el['class'].append(new_root)
                        apply_rules_to_children(el, RULES.get(old_root, []))
