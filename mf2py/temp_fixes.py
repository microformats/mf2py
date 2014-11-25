from bs4 import BeautifulSoup

def apply_rules(doc):
    for el in doc.find_all("template"):
        el.extract()
