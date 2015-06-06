from __future__ import unicode_literals, print_function


def root(classes):
    """get all root classnames
    """
    return [c for c in classes if c.startswith("h-")]


def properties(classes):
    """get all property (p-*, u-*, e-*, dt-*) classnames
    """
    return [c.partition("-")[2] for c in classes if c.startswith("p-")
            or c.startswith("u-") or c.startswith("e-") or c.startswith("dt-")]


def text(classes):
    """get text property (p-*) names
    """
    return [c.partition("-")[2] for c in classes if c.startswith("p-")]


def url(classes):
    """get URL property (u-*) names
    """
    return [c.partition("-")[2] for c in classes if c.startswith("u-")]


def datetime(classes):
    """get datetime property (dt-*) names
    """
    return [c.partition("-")[2] for c in classes if c.startswith("dt-")]


def embedded(classes):
    """get embedded property (e-*) names
    """
    return [c.partition("-")[2] for c in classes if c.startswith("e-")]
