from __future__ import unicode_literals, print_function

from .mf_helpers import unordered_list

import re

def _check_format(prefix, cl):

    # older one does not check hyphens
    #FORMAT_RE = r'%s-([a-z0-9]+-)?[a-z-]+'

    FORMAT_RE = r'%s-([a-z0-9]+-)?[a-z]+(-[a-z]+)*'

    RE = FORMAT_RE % (prefix)

    return re.match(RE + '$', cl)

def root(classes):
    """get all root classnames
    """

    return unordered_list([c for c in classes if _check_format('h', c)])


def properties(classes):
    """get all property (p-*, u-*, e-*, dt-*) classnames
    """

    return unordered_list([c.partition("-")[2] for c in classes if _check_format('(p|u|dt|e)', c)])

def property_classes(classes):
    """get all property (p-*, u-*, e-*, dt-*) classnames with prefix
    """

    return unordered_list([c for c in classes if _check_format('(p|u|dt|e)', c)])

def text(classes):
    """get text property (p-*) names
    """

    return unordered_list([c.partition("-")[2] for c in classes if _check_format('p', c)])


def url(classes):
    """get URL property (u-*) names
    """

    return unordered_list([c.partition("-")[2] for c in classes if _check_format('u', c)])


def datetime(classes):
    """get datetime property (dt-*) names
    """

    return unordered_list([c.partition("-")[2] for c in classes if _check_format('dt', c)])

def embedded(classes):
    """get embedded property (e-*) names
    """

    return unordered_list([c.partition("-")[2] for c in classes if _check_format('e', c)])
