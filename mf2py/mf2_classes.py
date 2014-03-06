## function to get all root classnames
def root(classes):
    return [c for c in classes if c.startswith("h-")]

##  function to get all property classnames        
def properties(classes):
    return [c for c in classes if c.startswith("p-") or c.startswith("u-") or c.startswith("e-") or c.startswith("dt-")]

## function to get text property names
def text(classes):
    return [c for c in classes if c.startswith("p-")]

## function to get URL property names
def url(classes):
    return [c for c in classes if c.startswith("u-")]

## function to get date/time property names
def datetime(classes):
    return [c for c in classes if c.startswith("dt-")]

## function to get embedded property names
def embedded(classes):
    return [c for c in classes if c.startswith("e-")]

## function to get names of properties from classnames i.e. without microformat prefix
def property_names(classes):
    return [c.partition("-")[2] for c in properties(classes)]
