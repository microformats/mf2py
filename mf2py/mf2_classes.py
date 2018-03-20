from __future__ import unicode_literals, print_function

from .mf_helpers import unordered_list

import re

def root(classes):
    """get all root classnames
    """

    # checks for form "h-(letters or numbers)-(letters)-..." 
    RE = r'h-([a-z0-9]+-)?[a-z-]+'

    return unordered_list([c for c in classes if re.match(RE + '$', c)])


def properties(classes):
    """get all property (p-*, u-*, e-*, dt-*) classnames
    """
    # checks for form "(p or u or e or dt)-(letters or numbers)-(letters)-..." 
    RE = r'(p|u|dt|e)-([a-z0-9]+-)?[a-z-]+'

    return unordered_list([c.partition("-")[2] for c in classes if re.match(RE + '$', c)])

def property_classes(classes):
    """get all property (p-*, u-*, e-*, dt-*) classnames with prefix
    """
    # checks for form "(p or u or e or dt)-(letters or numbers)-(letters)-..." 
    RE = r'(p|u|dt|e)-([a-z0-9]+-)?[a-z-]+'

    return unordered_list([c for c in classes if re.match(RE + '$', c)])

def text(classes):
    """get text property (p-*) names
    """

    # checks for form "p-(letters or numbers)-(letters)-..." 
    RE = r'p-([a-z0-9]+-)?[a-z-]+'

    return unordered_list([c.partition("-")[2] for c in classes if re.match(RE + '$', c)])


def url(classes):
    """get URL property (u-*) names
    """

    # checks for form "u-(letters or numbers)-(letters)-..." 
    RE = r'u-([a-z0-9]+-)?[a-z-]+'

    return unordered_list([c.partition("-")[2] for c in classes if re.match(RE + '$', c)])


def datetime(classes):
    """get datetime property (dt-*) names
    """

    # checks for form "dt-(letters or numbers)-(letters)-..." 
    RE = r'dt-([a-z0-9]+-)?[a-z-]+'

    return unordered_list([c.partition("-")[2] for c in classes if re.match(RE + '$', c)])

def embedded(classes):
    """get embedded property (e-*) names
    """

    # checks for form "e-(letters or numbers)-(letters)-..." 
    RE = r'e-([a-z0-9]+-)?[a-z-]+'

    return unordered_list([c.partition("-")[2] for c in classes if re.match(RE + '$', c)])
