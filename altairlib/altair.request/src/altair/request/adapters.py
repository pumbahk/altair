from webob.compat import PY3, text_, bytes_
from webob.multidict import MultiDict

class UnicodeMultiDictAdapter(object):
    def __init__(self, inner, charset='utf-8', errors='strict'):
        self.inner = inner
        self.charset = charset
        self.errors = errors

    def _e(self, v):
        return bytes_(v, self.charset, self.errors)

    def _d(self, v):
        return text_(v, self.charset, self.errors)

    def __getitem__(self, key):
        encoded_key = self._e(key)
        decoded_key = self._d(key)
        for k, v in reversed(self.inner.items()):
            if k == encoded_key:
                return v
            elif k == decoded_key:
                return v
        raise KeyError(key)

    def __setitem__(self, key, value):
        decoded_key = self._d(key)
        try:
            del self[key]
        except KeyError:
            pass
        self.inner.add(decoded_key, value)

    def __delitem__(self, key):
        encoded_key = self._e(key)
        decoded_key = self._d(key)
        items = self.inner._items
        if isinstance(self.inner, MultiDict):
            for i in range(len(items) - 1, -1, -1):
                p = items[i]
                if p[0] == encoded_key or p[0] == decoded_key:
                    del items[i]
                    found = True
            if not found:
                raise KeyError(key)
        else:
            try:
                del self.inner[encoded_key]
            except KeyError:
                del self.inner[decoded_key] 

    def __contains__(self, key):
        encoded_key = self._e(key)
        decoded_key = self._d(key)
        for k, v in self.items():
            if k == encoded_key or k == decoded_key:
                return True
        return False

    def add(self, key, value):
        encoded_key = self._e(key)
        decoded_key = self._d(key)
        if encoded_key in self.inner:
            self.inner.add(encoded_key, value)
        else:
            self.inner.add(decoded_key, value)

    def getall(self, key):
        encoded_key = self._e(key)
        decoded_key = self._d(key)
        return [v for k, v in self.inner.items() if k == encoded_key or k == decoded_key]

    def getone(self, key):
        v = self.getall(key)
        if not v:
            raise KeyError('Key not found: %r' % key)
        if len(v) > 1:
            raise KeyError('Multiple values match %r: %r' % (key, v))
        return v[0]

    def mixed(self):
        result = {}
        multi = {}
        for key, value in self.items():
            decoded_key = self._d(key)
            if decoded_key in result:
                if decoded_key in multi:
                    result[decoded_key].append(value)
                else:
                    result[decoded_key] = [result[decoded_key], value]
                    multi[decoded_key] = True
            else:
                result[decoded_key] = value
        return result

    def dict_of_lists(self):
        r = {}
        for key, val in self.items():
            decoded_key = self._d(key)
            r.setdefault(decoded_key, []).append(val)
        return r

    has_key = __contains__

    def clear(self):
        self.inner.clear()

    def copy(self):
        return self.inner.copy()

    def setdefault(self, key, default=None):
        encoded_key = self._e(key)
        decoded_key = self._d(key)
        for k, v in self._items:
            if key == encoded_key or key == decoded_key:
                return v
        self._items.append((decoded_key, default))
        return default

    def pop(self, key, *args):
        if len(args) > 1:
            raise TypeError("pop expected at most 2 arguments, got %s"
                             % repr(1 + len(args)))
        encoded_key = self._e(key)
        decoded_key = self._d(key)
        if isinstance(self.inner, MultiDict):
            items = self.inner._items
            for i in range(len(items)):
                p = items[i]
                if p[0] == encoded_key or p[0] == decoded_key:
                    v = items[i][1]
                    del items[i]
                    return v
            if args:
                return args[0]
            else:
                raise KeyError(key) 
        else:
            if encoded_key in self.inner:
                return self.inner.pop(encoded_key, *args)
            else:
                return self.inner.pop(decoded_key, *args)

    def popitem(self):
        return self.inner.popitem()

    def update(self, *args, **kwargs):
        if args:
            args = [(self._d(k), v) for k, v in args]
        if kwargs:
            kwargs = dict((self._d(k), v) for k, v in kwargs.items())
        self.inner.update(*args, **keargs)


    def extend(self, other=None, **kwargs):
        if not other:
            return None
        elif hasattr(other, 'items'):
            for k, v in other.items():
                self.inner.add(self._d(k), v)
        elif hasattr(other, 'keys'):
            for k in other.keys():
                self.inner.add(self._d(k), other[k])
        else:
            for k, v in other:
                self.inner.add(self._d(k), v)
        if kwargs:
            self.update(kwargs)

    def __len__(self):
        return len(self.inner)

    def iterkeys(self):
        return (self._d(k) for k, v in self.inner.items())

    if PY3:
        keys = iterkeys
    else:
        def keys(self):
            return list(self.iterkeys())

    def iteritems(self):
        return ((self._d(k), v) for k, v in self.inner.items())

    if PY3:
        items = iteritems
    else:
        def items(self):
            return list(self.iteritems())

    def itervalues(self):
        return self.inner.itervalues()

    def values(self):
        return self.inner.values()
