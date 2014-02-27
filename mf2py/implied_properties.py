from bs4 import BeautifulSoup
import mf2_classes

## function to find an implied name property
def name(el):
    # if image use alt text if not empty
    if el.name == 'img' and "alt" in el.attrs and not el["alt"] == "":
        return [el["alt"]]
    # if abbreviation use the title if not empty
    if el.name == 'abbr' and "title" in el.attrs and not el["title"] == "":
        return [el["title"]]
    # if only one image child then use alt text if not empty
    if len(el.find_all("img")) == 1 and "alt" in el.find_all("img")[0].attrs and not el.find_all("img")[0]["alt"] == "":
        return [el.find_all("img")[0]["alt"]]
    # if only one abbreviation child use abbreviation if not empty
    if len(el.find_all("abbr")) == 1 and "title" in el.find_all("abbr")[0].attrs and not el.find_all("abbr")[0]["title"] == "":
        return [el.find_all("abbr")[0]["title"]]
    # TODO(tommorris): implement the rest of http://microformats.org/wiki/microformats2-parsing#parsing_for_implied_properties
    # use text if all else fails
    return [el.get_text()]

## function to find implied photo property
def photo(el):
    # if element is an image use source if exists
    if el.name == 'img' and "src" in el.attrs:
        return [el["src"]]
    # if element has one image child use source if exists (check existence of src?)
    if len(el.find_all("img")) == 1 and "src" in el.find_all("img")[0].attrs :
        return [el.find_all("img")[0]["src"]]
    # TODO(tommorris): implement the other implied photo finders from http://microformats.org/wiki/microformats2-parsing#parsing_for_implied_properties
    return None

## function to find implied url
def url(el):
    # if element is a link use its href if exists
    if el.name == 'a' and "href" in el.attrs:
        return el["href"]
    # if one link child use its href 
    if len(el.find_all("a")) == 1 and "href" in el.find_all("a")[0].attrs and mf2_classes.root(el.find_all("a")[0].get('class',[])) == []:
        return el.find_all("a")[0]["href"]
    return None 
