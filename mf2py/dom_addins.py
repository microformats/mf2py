from xml.dom.minidom import Element

def getElementsByClassName(self, classname):
    return [x for x in self.getElementsByTagName("*") if x.hasAttribute("class") and classname in x.getAttribute("class").split(" ")]

def addClassName(self, classname):
    classnames = set(self.getAttribute("class").split(" "))
    classnames.add(classname)
    self.setAttribute("class", ' '.join(list(classnames)))

def hasClassName(self, classname_or_lambda):
    classnames = set(self.getAttribute("class").split(" "))
    if type(classname_or_lambda) == str:
        return classname_or_lambda in classnames
    elif hasattr(classname_or_lambda, '__call__'):
        for classname in classnames:
            result = classname_or_lambda(classname)
            if result == True:
                return True
        return False

def getText(self):
    out = ''
    if self.hasChildNodes():
        for child in self.childNodes:
            if 'wholeText' in dir(child):
                if child.wholeText is not None:
                    out = out + child.wholeText
            elif 'childNodes' in dir(child):
                out = out + child.getText()
    else:
        if self.nodeValue is not None:
            out = out + self.nodeValue
    return out

Element.__dict__.update({'getElementsByClassName': getElementsByClassName})
Element.__dict__.update({'addClassName': addClassName})
Element.__dict__.update({'hasClassName': hasClassName})
Element.__dict__.update({'getText': getText})
