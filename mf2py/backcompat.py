# coding: utf-8

"""Looks for classic microformats class names and augments them with
microformats2 names. Ported and adapted from php-mf2.
"""

# Classic Root Classname map
CLASSIC_ROOT_MAP = {
    u'vcard': u'h-card',
    u'hfeed': u'h-feed',
    u'hentry': u'h-entry',
    u'hrecipe': u'h-recipe',
    u'hresume': u'h-resume',
    u'vevent': u'h-event',
    u'hreview': u'h-review',
    u'hproduct': u'h-product'
}

CLASSIC_PROPERTY_MAP = {
    u'vcard': {
        u'classes': {
            u'fn': [u'p-name'],
            u'url': [u'u-url'],
            u'honorific-prefix': [u'p-honorific-prefix'],
            u'given-name': [u'p-given-name'],
            u'additional-name': [u'p-additional-name'],
            u'family-name': [u'p-family-name'],
            u'honorific-suffix': [u'p-honorific-suffix'],
            u'nickname': [u'p-nickname'],
            u'email': [u'u-email'],
            u'logo': [u'u-logo'],
            u'photo': [u'u-photo'],
            u'url': [u'u-url'],
            u'uid': [u'u-uid'],
            u'category': [u'p-category'],
            u'adr': [u'p-adr', u'h-adr'],
            u'extended-address': [u'p-extended-address'],
            u'street-address': [u'p-street-address'],
            u'locality': [u'p-locality'],
            u'region': [u'p-region'],
            u'postal-code': [u'p-postal-code'],
            u'country-name': [u'p-country-name'],
            u'label': [u'p-label'],
            u'geo': [u'p-geo', u'h-geo'],
            u'latitude': [u'p-latitude'],
            u'longitude': [u'p-longitude'],
            u'tel': [u'p-tel'],
            u'note': [u'p-note'],
            u'bday': [u'dt-bday'],
            u'key': [u'u-key'],
            u'org': [u'p-org'],
            u'organization-name': [u'p-organization-name'],
            u'organization-unit': [u'p-organization-unit'],
        },
    },
    u'hentry': {
        u'classes': {
            u'entry-title': [u'p-name'],
            u'entry-summary': [u'p-summary'],
            u'entry-content': [u'e-content'],
            u'published': [u'dt-published'],
            u'updated': [u'dt-updated'],
            u'author': [u'p-author', u'h-card'],
            u'category': [u'p-category'],
            u'geo': [u'p-geo', u'h-geo'],
            u'latitude': [u'p-latitude'],
            u'longitude': [u'p-longitude'],
        },
        u'rels': {
            # Unlike most rel values, bookmark is scoped to its
            # parent, not to the document.
            u'bookmark': [u'u-url'],
        },
    },
    u'hrecipe': {
        u'classes': {
            u'fn': [u'p-name'],
            u'ingredient': [u'p-ingredient'],
            u'yield': [u'p-yield'],
            u'instructions': [u'e-instructions'],
            u'duration': [u'dt-duration'],
            u'nutrition': [u'p-nutrition'],
            u'photo': [u'u-photo'],
            u'summary': [u'p-summary'],
            u'author': [u'p-author', u'h-card'],
        },
    },
    u'hresume': {
        u'classes': {
            u'summary': [u'p-summary'],
            u'contact': [u'h-card', u'p-contact'],
            u'education': [u'h-event', u'p-education'],
            u'experience': [u'h-event', u'p-experience'],
            u'skill': [u'p-skill'],
            u'affiliation': [u'p-affiliation', u'h-card'],
        },
    },
    u'vevent': {
        u'classes': {
            u'dtstart': [u'dt-start'],
            u'dtend': [u'dt-end'],
            u'duration': [u'dt-duration'],
            u'description': [u'p-description'],
            u'summary': [u'p-summary'],
            u'url': [u'u-url'],
            u'category': [u'p-category'],
            u'location': [u'h-card'],
            u'geo': [u'p-location h-geo'],
        },
    },
    u'hreview': {
        u'classes': {
            u'summary': [u'p-name'],
            # doesn't work properly, see spec
            u'fn': [u'p-item', u'h-item', u'p-name'],
            # of the item being reviewed (p-item h-item u-photo)
            u'photo': [u'u-photo'],
            # of the item being reviewed (p-item h-item u-url)
            u'url': [u'u-url'],
            u'reviewer': [u'p-reviewer', u'p-author', u'h-card'],
            u'dtreviewed': [u'dt-reviewed'],
            u'rating': [u'p-rating'],
            u'best': [u'p-best'],
            u'worst': [u'p-worst'],
            u'description': [u'p-description'],
        },
    },
    u'hproduct': {
        u'classes': {
            u'fn': [u'p-name'],
            u'photo': [u'u-photo'],
            u'brand': [u'p-brand'],
            u'category': [u'p-category'],
            u'description': [u'p-description'],
            u'identifier': [u'u-identifier'],
            u'url': [u'u-url'],
            u'review': [u'p-review', u'h-review', u'e-description'],
            u'price': [u'p-price'],
        },
    }
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
                child[u'class'] = child_class
            # recurse if it's not a nested root
            if not any(cls in CLASSIC_ROOT_MAP
                       for cls in child.get('class', [])):
                update_child_properties(child, properties)

    for old_root, new_root in CLASSIC_ROOT_MAP.items():
        for el in doc.find_all(lambda el: old_root in el.get('class', [])
                               and new_root not in el.get('class', [])):
            el[u'class'].append(new_root)

    for old_root, properties in CLASSIC_PROPERTY_MAP.items():
        for el in doc.find_all(class_=old_root):
            update_child_properties(el, properties)
