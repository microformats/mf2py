from xml.dom.minidom import Element

def getElementsByClassName(self, classname):
    return [x for x in self.getElementsByTagName("*") if x.hasAttribute("class") and classname in x.getAttribute("class").split(" ")]

Element.__dict__.update({'getElementsByClassName': getElementsByClassName})
