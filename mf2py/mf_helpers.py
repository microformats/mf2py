def get_url(mf):
    """Given a property value that may be a list of simple URLs or complex
    h-* dicts (with a url property), extract a list of URLs. This is useful
    when parsing e.g., in-reply-to.

    Args:
      mf (string or dict): URL or h-cite-style dict

    Returns:
      list: a list of URLs
    """
    urls = []
    for item in mf:
        if isinstance(item, basestring):
            urls.append(item)
        elif (isinstance(item, dict)
              and any(x.startswith('h-') for x in item.get('type', []))):
            urls.extend(item.get('properties', {}).get('url', []))

    return urls
