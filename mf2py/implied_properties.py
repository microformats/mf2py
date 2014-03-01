import mf2_classes
from dom_helpers import get_attr 

## function to find an implied name property
def name(el):
    # if image use alt text if not empty
    prop_value = get_attr(el, "alt", check_name="img")
    if prop_value is not None:
        return [prop_value]

    # if abbreviation use the title if not empty
    prop_value = get_attr(el, "title", check_name="abbr")
    if prop_value is not None:
        return [prop_value]

    # if only one image child then use alt text if not empty
    poss_imgs = el.find_all("img")
    if len(poss_imgs) == 1:
        poss_img = poss_imgs[0]

        prop_value = get_attr(poss_img, "alt", check_name="img")
        if prop_value is not None:
            return [prop_value]


    # if only one abbreviation child use abbreviation if not empty
    poss_abbrs = el.find_all("abbr")
    if len(poss_abbrs) == 1:
        poss_abbr = poss_abbrs[0]

        prop_value = get_attr(poss_abbr, "title", check_name="abbr")
        if prop_value is not None:
            return [prop_value]

    # TODO(tommorris): implement the rest of http://microformats.org/wiki/microformats2-parsing#parsing_for_implied_properties
    # use text if all else fails
    return [el.get_text().strip()]

## function to find implied photo property
def photo(el):
    # if element is an image use source if exists
    prop_value = get_attr(el, "src", check_name="img")
    if prop_value is not None:
        return [prop_value]

    # if element has one image child use source if exists (check existence of src?)
    poss_imgs = el.find_all("img")
    if len(poss_imgs) == 1:
        poss_img = poss_imgs[0]

        prop_value = get_attr(poss_img, "src", check_name="img")
        if prop_value is not None:
            return [prop_value]


    # TODO(tommorris): implement the other implied photo finders from http://microformats.org/wiki/microformats2-parsing#parsing_for_implied_properties
    return None

## function to find implied url
def url(el):
    # if element is a link use its href if exists
    prop_value = get_attr(el, "href", check_name="a")
    if prop_value is not None:
        return [prop_value]

    # if one link child use its href 
    poss_as = el.find_all("a")
    if len(poss_as) == 1:
        poss_a = poss_as[0]

        prop_value = get_attr(poss_a, "href", check_name="a")
        if prop_value is not None and mf2_classes.root(poss_a.get('class',[])) == []:
            return [prop_value]

    return None 
