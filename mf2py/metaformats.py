"""Metaformats parser.

https://microformats.org/wiki/metaformats
"""
from . mf2_classes import filter_classes
from .dom_helpers import try_urljoin


METAFORMAT_TO_MF2 = [
    # in priority order, descending

    # OGP
    ("property", "article:author", "author"),
    ("property", "article:published_time", "published"),
    ("property", "article:modified_time", "updated"),
    ("property", "og:audio", "audio"),
    ("property", "og:description", "summary"),
    ("property", "og:image", "photo"),
    ("property", "og:title", "name"),
    ("property", "og:video", "video"),

    # Twitter
    ("name", "twitter:title", "name"),
    ("name", "twitter:description", "summary"),
    ("name", "twitter:image", "photo"),
]
OGP_TYPE_TO_MF2 = {
    "article": "h-entry",
    "movie": "h-cite",
    "music": "h-cite",
    "profile": "h-card",
}
URL_PROPERTIES = {
    "article:author",
    "og:audio",
    "og:image",
    "og:video",
    "twitter:image",
}


def parse(soup, url=None):
    """Extracts and returns a metaformats item from a BeautifulSoup parse tree.

    Args:
      soup (bs4.BeautifulSoup): parsed HTML
      url (str): URL of document

    Returns:
      dict: mf2 item, or None if the input is not eligible for metaformats
    """
    if not soup.head:
        return None

    # Is there a microformat2 root class on the html element?
    if filter_classes(soup.get("class", []))["h"]:
        return None

    parsed = {}

    # Properties
    for attr, meta, mf2 in METAFORMAT_TO_MF2:
        if val := soup.head.find("meta", attrs={attr: meta}):
            if content := val.get("content"):
                if meta in URL_PROPERTIES:
                    content = try_urljoin(url, content)
                parsed.setdefault("properties", {}).setdefault(mf2, [content])

    if not parsed:
        # No OGP or Twitter properties
        return None

    # type from OGP or default to h-entry
    parsed["type"] = ["h-entry"]
    if ogp_type := soup.head.find("meta", property="og:type"):
        if content := ogp_type.get("content"):
            if mf2_type := OGP_TYPE_TO_MF2.get(content.split(".")[0]):
                parsed["type"] = [mf2_type]

    return parsed
