def get_url(mf):
    """parses the mf dictionary obtained as returns the URL"""

    urls = []
    for item in mf:
        if isinstance(item, basestring):
            urls.append(item)
        else:
            itemtype = [x for x in item.get('type',[]) if x.startswith('h-')]
            if itemtype is not []:
                urls.extend(item.get('properties',{}).get('url',[]))

    return urls
