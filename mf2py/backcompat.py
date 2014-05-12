from bs4 import BeautifulSoup

## add modern classnames for older mf classnames
def apply_rules(doc):
    for el in doc.find_all(class_="hcard"):
        el["class"].append("h-card")
