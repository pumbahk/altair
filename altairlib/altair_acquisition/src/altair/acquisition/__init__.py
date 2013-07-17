# This package may contain traces of nuts

def getattr_ex(obj, name):
    names = name.split(".")
    o = obj
    for name in names:
        if not hasattr(o, name):
            return None
        o = getattr(o, name)
    return o


def lineage_acquires(obj, acquire_order):
    return [obj] + [getattr_ex(obj, acquire) 
                    for acquire in acquire_order]

class Acquisition(object):
    def __init__(self, obj, acquire_order):
        self.lines = lineage_acquires(obj, acquire_order)


    def __getattr__(self, name):
        for o in self.lines:
            if hasattr(o, name):
                v = getattr(o, name)
                if v is not None:
                    return v

                
