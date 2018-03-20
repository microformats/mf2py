from __future__ import unicode_literals, print_function

from .mf_helpers import unordered_list


def root(classes):
    """get all root classnames
    """
    return unordered_list([c for c in classes if c.startswith("h-")])


def properties(classes):
    """get all property (p-*, u-*, e-*, dt-*) classnames
    """
    return unordered_list([c.partition("-")[2] for c in classes if c.startswith("p-")
            or c.startswith("u-") or c.startswith("e-") or c.startswith("dt-")])


def text(classes):
    """get text property (p-*) names
    """
    return unordered_list([c.partition("-")[2] for c in classes if c.startswith("p-")])


def url(classes):
    """get URL property (u-*) names
    """
    return unordered_list([c.partition("-")[2] for c in classes if c.startswith("u-")])


def datetime(classes):
    """get datetime property (dt-*) names
    """
    return unordered_list([c.partition("-")[2] for c in classes if c.startswith("dt-")])


def embedded(classes):
    """get embedded property (e-*) names
    """
    return unordered_list([c.partition("-")[2] for c in classes if c.startswith("e-")])

def property_classes(classes):
    """get all property (p-*, u-*, e-*, dt-*) classnames with prefix
    """
    return unordered_list([c for c in classes if c.startswith("p-")
            or c.startswith("u-") or c.startswith("e-") or c.startswith("dt-")])
