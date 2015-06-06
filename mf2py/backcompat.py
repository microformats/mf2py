# coding: utf-8
"""Looks for classic microformats class names and augments them with
microformats2 names. Ported and adapted from php-mf2.
"""

from __future__ import unicode_literals, print_function

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
        'classes': {
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
    },
    'hentry': {
        'classes': {
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
        'rels': {
            # Unlike most rel values, bookmark is scoped to its
            # parent, not to the document.
            'bookmark': ['u-url'],
        },
    },
    'hrecipe': {
        'classes': {
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
    },
    'hresume': {
        'classes': {
            'summary': ['p-summary'],
            'contact': ['h-card', 'p-contact'],
            'education': ['h-event', 'p-education'],
            'experience': ['h-event', 'p-experience'],
            'skill': ['p-skill'],
            'affiliation': ['p-affiliation', 'h-card'],
        },
    },
    'vevent': {
        'classes': {
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
    },
    'hreview': {
        'classes': {
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
    },
    'hproduct': {
        'classes': {
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
    },
    'hreview-aggregate': {
        'classes': {
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
    },
    'geo': {
        'classes': {
            'latitude': ['p-latitude'],
            'longitude': ['p-longitude'],
        },
    },
    'adr': {
        'classes': {
            'post-office-box': ['p-post-office-box'],
            'extended-address': ['p-extended-address'],
            'street-address': ['p-street-address'],
            'locality': ['p-locality'],
            'region': ['p-region'],
            'postal-code': ['p-postal-code'],
            'country-name': ['p-country-name'],
        },
    },
}


def apply_rules(doc):
    """add modern classnames for older mf classnames

    modifies BeautifulSoup document in-place
    """

    def update_child_properties(parent, properties):
        for child in parent.find_all(recursive=False):
            child_class = child.get('class', [])
            # augment legacy class names with their associated mf2 classes
            for old_prop, new_props in properties.get('classes', {}).items():
                if old_prop in child_class:
                    child_class += [p for p in new_props
                                    if p not in child_class]
            # check for legacy rel properties (e.g. rel=bookmark that translate
            # to mf2 classes
            child_rel = child.get('rel', [])
            for old_prop, new_props in properties.get('rels', {}).items():
                if child_rel and old_prop in child_rel:
                    child_class += [p for p in new_props
                                    if p not in child_class]
            if child_class:
                child['class'] = child_class
            # recurse if it's not a nested root
            if not any(cls in CLASSIC_ROOT_MAP
                       for cls in child.get('class', [])):
                update_child_properties(child, properties)

    for old_root, new_root in CLASSIC_ROOT_MAP.items():
        for el in doc.find_all(lambda el: old_root in el.get('class', [])
                               and new_root not in el.get('class', [])):
            el['class'].append(new_root)

    for old_root, properties in CLASSIC_PROPERTY_MAP.items():
        for el in doc.find_all(class_=old_root):
            update_child_properties(el, properties)
