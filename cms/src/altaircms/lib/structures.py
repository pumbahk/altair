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
            raise KeyError("strict dict not support getting None value")
        return v
        

if __name__ == "__main__":
    import doctest
    doctest.testmod()

