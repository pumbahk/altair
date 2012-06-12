class StrictDict(dict):
    """ subspecies. a value of getitem from this is None raise KeyError
    >>> sd = StrictDict(foo="bar")

    >>> sd["v"] = None
    >>> ## key error sd["v"] 

    >>> sd["v"] = 1
    >>> sd["v"]
    1
    """
    def __getitem__(self, k):
        v = super(StrictDict, self).__getitem__(k)
        if v is None:
            raise KeyError(u".%s is not found (strict dict not support getting None value)" % k)
        return v
        

if __name__ == "__main__":
    import doctest
    doctest.testmod()

## null object
class Nullable(object):
    """
    >>> Nullable(None).x.y.z.value
    None
    >>> Nullable(1).value
    1
    """
    NULL = None #for flyweight
    def __init__(self, obj):
        self.obj = obj

    def __getattr__(self, k):
        obj = self.obj
        if hasattr(obj, k):
            return Nullable(getattr(obj, k))
        else:
            return self.NULL

    @property
    def value(self):
        return self.__dict__["obj"]

Nullable.NULL = Nullable(None)
