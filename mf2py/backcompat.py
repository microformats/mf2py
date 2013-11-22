from xml.dom.minidom import Element
import dom_addins

def apply_backcompat_rules(self):
    for el in self.getElementsByClassName("hcard"):
        el.addClassName("h-card")

Element.__dict__.update({'apply_backcompat_rules': apply_backcompat_rules})
