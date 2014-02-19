from bs4 import BeautifulSoup

def apply_backcompat_rules(self):
    for el in self.find_all(class_="hcard"):
        el["class"].append("h-card")
