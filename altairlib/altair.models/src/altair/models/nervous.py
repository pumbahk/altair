import weakref
import json.decoder
import six
from . import _json_scanner

class NullReceiverObject(object):
    def _changed(self, modified):
        pass

NullReceiver = NullReceiverObject()

class NervousContainerMixin(object):
    def _changed(self, modified):
        for callback in self._callbacks:
            callback(modified)

    def _bind(self, callback):
        self._callbacks.add(callback)

    def _unbind(self, callback):
        self._callbacks.remove(callback)

    def __mixin_init__(self, *args, **kwargs):
        self._callbacks = set()
        self._weak_cb = None

    @property
    def _weak_callback(self):
        if self._weak_cb is None:
            r = weakref.ref(self)
            self._weak_cb = lambda modified: (r() or NullReceiver)._changed(modified)
        return self._weak_cb

    def _make_bond(self, v):
        if isinstance(v, NervousContainerMixin):
            v._bind(self._weak_callback)

    def _remove_bond(self, v):
        if isinstance(v, NervousContainerMixin):
            v._unbind(self._weak_callback)


class NervousList(list, NervousContainerMixin):
    def __init__(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)
        self.__mixin_init__(*args, **kwargs)
        for v in self:
            self._make_bond(v) 

    def __setitem__(self, i, v):
        if isinstance(self[i], NervousContainerMixin):
            self[i]._unbind(self._weak_callback)
        list.__setitem__(self, i, v)
        self._changed(self)

    def __delitem__(self, i):
        if isinstance(self[i], NervousContainerMixin):
            self[i]._unbind(self._weak_callback)  
        list.__delitem__(self, i)
        self._changed(self)

    def __setslice__(self, s, e, i):
        l = len(self)
        if s < 0:
            s += len(self)
        elif s >= l:
            s = l
        if e < 0:
            e += len(self)
        elif e >= l:
            e = l
        if e < s:
            e = s
        j = s
        for v in i:
            self._make_bond(v)
            if j < e:
                self._remove_bond(self[j])
                list.__setitem__(self, j, v)
            else:
                list.insert(self, j, v)
            j += 1
        self._changed(self)

    def __delslice__(self, s, e):
        l = len(self)
        if s < 0:
            s += len(self)
        elif s >= l:
            s = l
        if e < 0:
            e += len(self)
        elif e >= l:
            e = l
        if e < s:
            e = s
        j = 0
        while j < e:
            self._remove_bond(j)
            j += 1
        list.__delslice__(self, *args)
        self._changed(self)

    def append(self, v):
        self._make_bond(v)
        list.append(self, v)
        self._changed(self)

    def extend(self, i):
        for v in i:
            self._make_bond(v)
            list.append(self, v)
        self._changed(self)

    def insert(self, i, v):
        self._make_bond(v)
        list.insert(self, i, v)
        self._changed(self)

    def pop(self, i=-1):
        l = len(self)
        if i < 0:
            i += l
        elif i >= l:
            raise IndexError('pop index out of range')
        v = list.pop(self, i)
        self._remove_bond(v)
        self._changed(self)
        return v

    def remove(self, v):
        i = self.index(v)
        self._remove_bond(self[i])
        del self[i]
        self._changed(self)

    def reverse(self, *args):
        list.reverse(self, *args)
        self._changed(self)

    def sort(self, *args):
        list.sort(self, *args)
        self._changed(self)

    def __reduce__(self):
        return (list, (), None, iter(self), None)


class NervousDict(dict, NervousContainerMixin):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__mixin_init__(*args, **kwargs)
        for k, v in six.iteritems(self):
            self._make_bond(v) 

    def __setitem__(self, k, v):
        try:
            ov = self[k]
            self._remove_bond(ov)
        except KeyError:
            pass
        self._make_bond(v)
        dict.__setitem__(self, k, v)
        self._changed(self)

    def __delitem__(self, k):
        ov = self[k]
        self._remove_bond(ov)
        dict.__delitem__(self, k)
        self._changed(self)

    def setdefault(self, k, default=None):
        try:
            return self[k]
        except KeyError:
            pass
        self._make_bond(default)
        self[k] = default
        self._changed(self)
        return default

    def pop(self, *args):
        l = len(args)
        retval = None
        if l == 1:
            retval = dict.pop(self, args[0])
            self._remove_bond(retval)
        elif l == 2:
            try:
                retval = dict.pop(self, args[0])
                self._remove_bond(retval)
            except KeyError:
                retval = args[1]
        elif l < 1:
            raise TypeError('pop extpected at least 1 arguments, got %d' % len(args))
        elif l > 2:
            raise TypeError('pop extpected at most 2 arguments, got %d' % len(args))
        self._changed(self)
        return retval

    def popitem(self, *args):
        retval = dict.popitem(self, *args)
        self._remove_bond(retval[1])
        self._changed(self)
        return retval

    def update(self, i=None, **kwargs):
        if i is not None:
            if isinstance(i, dict):
                i = six.iteritems(i)
            for k, v in i:
                self[k] = v
        for k, v in six.iteritems(kwargs):
            self[k] = v
        self._changed(self)

    def clear(self):
        for k, v in six.iteritems(self):
            self._remove_bond(v)
        dict.clear(self)
        self._changed(self)

    def __reduce__(self):
        return (dict, (), None, None, six.iteritems(self))

class NervousJSONObject(object):
    def __init__(self, dict_class):
        self.dict_class = dict_class

    def __call__(self, s_and_end, encoding, strict, scan_once, object_hook,
               object_pairs_hook, _w=json.decoder.WHITESPACE.match, _ws=json.decoder.WHITESPACE_STR):
        return json.decoder.JSONObject(s_and_end, encoding, strict, scan_once, None, self.dict_class, _w=_w, _ws=_ws)
 

class NervousJSONArray(object):
    def __init__(self, list_class):
        self.list_class = list_class

    def __call__(self, s_and_end, scan_once, _w=json.decoder.WHITESPACE.match, _ws=json.decoder.WHITESPACE_STR):
        s, end = s_and_end
        values = self.list_class()
        nextchar = s[end:end + 1]
        if nextchar in _ws:
            end = _w(s, end + 1).end()
            nextchar = s[end:end + 1]
        # Look-ahead for trivial empty array
        if nextchar == ']':
            return values, end + 1
        _append = values.append
        while True:
            try:
                value, end = json.decoder.scan_once(s, end)
            except StopIteration:
                raise ValueError(errmsg("Expecting object", s, end))
            _append(value)
            nextchar = s[end:end + 1]
            if nextchar in _ws:
                end = _w(s, end + 1).end()
                nextchar = s[end:end + 1]
            end += 1
            if nextchar == ']':
                break
            elif nextchar != ',':
                raise ValueError(errmsg("Expecting ',' delimiter", s, end))
            try:
                if s[end] in _ws:
                    end += 1
                    if s[end] in _ws:
                        end = _w(s, end + 1).end()
            except IndexError:
                pass

        return values, end


class NervousJSONDecoder(json.decoder.JSONDecoder):
    def __init__(self, encoding=None, strict=True, dict_class=NervousDict, list_class=NervousList):
        super(NervousJSONDecoder, self).__init__(
            encoding=encoding,
            strict=strict
            )
        self.parse_object = NervousJSONObject(dict_class)
        self.parse_array = NervousJSONArray(list_class)
        self.array_hook = self.parse_array.list_class
        self.object_pairs_hook = self.parse_object.dict_class
        # re-create scanner
        self.scan_once = _json_scanner.make_scanner(self)

    def decode(self, s, _w=json.decoder.WHITESPACE.match):
        return json.decoder.JSONDecoder.decode(self, s, _w)
