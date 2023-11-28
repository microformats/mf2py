"""Metaformats parser.

https://microformats.org/wiki/metaformats
"""
from . mf2_classes import filter_classes
from .dom_helpers import try_urljoin


OGP_TO_MF2 = {
    "article:author": "author",
    "article:published_time": "published",
    "article:modified_time": "updated",
    "og:audio": "audio",
    "og:description": "summary",
    "og:image": "photo",
    "og:title": "name",
    "og:video": "video",
}
OGP_TYPE_TO_MF2 = {
    "article": "h-entry",
    "movie": "h-cite",
    "music": "h-cite",
    "profile": "h-card",
}
OGP_URL_PROPERTIES = {
    "article:author",
    "og:audio",
    "og:image",
    "og:video",
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

    if ogp_type := soup.head.find("meta", property="og:type"):
        if content := ogp_type.get("content"):
            if mf2_type := OGP_TYPE_TO_MF2.get(content.split(".")[0]):
                parsed["type"] = [mf2_type]

    for ogp, mf2 in OGP_TO_MF2.items():
        if val := soup.head.find("meta", property=ogp):
            if content := val.get("content"):
                if ogp in OGP_URL_PROPERTIES:
                    content = try_urljoin(url, content)
                print(ogp, mf2, val, content)
                parsed.setdefault("properties", {})[mf2] = [content]

    return parsed or None
