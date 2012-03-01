class Struct(object):
    """
    >>> struct = Struct()
    >>> struct.define("foo", 1)
    >>> struct.define("foo", 2)
    >>> struct.define("bar", 2)
    >>> struct
    {'foo': [1, 2], 'bar': [2]}

    >>> struct = Struct(gen=set, add="add")
    >>> struct.define("foo", 1)
    >>> struct.define("foo", 1)
    >>> struct.define("foo", 1)
    >>> struct.define("foo", 1)
    >>> struct
    {'foo': set([1])}

    >>> struct["foo"]
    set([1])

    >>> struct["foo"] = 2
    >>> struct["foo"]
    set([1, 2])
    """
    def __init__(self, gen=list, add="append", keywords=None):
        self._keywords = set()

        self.default_gen = gen
        self.add = add
        for k in keywords or []:
            self._predefine(k)

    def __repr__(self):
        return str(self.as_dict())

    def as_dict(self):
        return {k: getattr(self, k)for k in self._keywords}

    def _predefine(self, keyword):
        if not hasattr(self, keyword):
            self._keywords.add(keyword)
            setattr(self, keyword, self.default_gen())

    def define(self, keyword, value):
        self._predefine(keyword)
        getattr(getattr(self, keyword), self.add)(value)

    __setitem__ = define
    def __getitem__(self, k):
        return getattr(self, k)


def struct(default_keywords=None):
    return Struct(keywords=default_keywords)

def uniq_struct(default_keywords=None):
    return Struct(gen=set, add="add", keywords=default_keywords)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
