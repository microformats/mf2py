from xml.dom.minidom import Element

def getElementsByClassName(self, classname):
    return [x for x in self.getElementsByTagName("*") if x.hasAttribute("class") and classname in x.getAttribute("class").split(" ")]

def addClassName(self, classname):
    classnames = set(self.getAttribute("class").split(" "))
    classnames.add(classname)
    self.setAttribute("class", ' '.join(list(classnames)))

Element.__dict__.update({'getElementsByClassName': getElementsByClassName})
Element.__dict__.update({'addClassName': addClassName})

