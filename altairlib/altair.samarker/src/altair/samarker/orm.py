from traceback import extract_stack, format_list
import itertools
import os
import types
import inspect
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.interfaces import MapperOption
from sqlalchemy.orm.query import Query
from .expression import make_marked_clause_element

COMMENT_ATTR_KEY = u'%s.comment' % __name__

def get_files_for(m):
    retval = [inspect.getfile(m)]
    src_file = inspect.getsourcefile(m)
    if src_file is not None:
        retval.append(src_file)
    return retval

def build_base_exclusion():
    import sqlalchemy.orm
    s = set()
    visited = set()
    def _(m):
        if m in visited:
            return
        visited.add(m)
        s.update(get_files_for(m))
        for k, v in inspect.getmembers(sqlalchemy.orm):
            if inspect.ismodule(v):
                _(v)
    _(sqlalchemy.orm)
    return s
            
base_exclusion = build_base_exclusion()

class MarkerOption(MapperOption):
    def __init__(self, comment):
        self.comment = comment

    def process_query(self, query):
        query._attributes[COMMENT_ATTR_KEY] = self.comment

def marker(comment):
    return MarkerOption(comment)

WrapperDescriptorType = type(object.__getattribute__)

class MarkerQuery(Query):
    _inner = None

    def __metaclass__(name, bases, dict_):
        _extra_properties = [
            '_entities',
            'session',
            '_polymorphic_adapters',
            ]

        base = bases[0]

        def make_property_proxy(x):
            def getter(self):
                return object.__getattribute__(self._inner, x)

            def setter(self, value):
                object.__setattr__(self._inner, x, value)
            dict_[x] = property(getter, setter)

        for x in dir(base):
            if x not in dict_:
                def _(x):
                    v = getattr(base, x)
                    if isinstance(v, types.MethodType):
                        dict_[x] = lambda self, *args, **kwargs: object.__getattribute__(self._inner, x)(*args, **kwargs)
                    elif isinstance(v, types.BuiltinMethodType):
                        dict_[x] = lambda self, *args, **kwargs: v(self, *args, **kwargs)
                    elif not isinstance(v, WrapperDescriptorType):
                        make_property_proxy(x)
                _(x)
        for x in _extra_properties:
            make_property_proxy(x)
        return type(name, bases, dict_)

    def __init__(self, inner):
        self._inner = inner
        self._inner_clone = self._inner.__class__._clone
        self._inner_compile_context = self._inner.__class__._compile_context
        self._inner._clone = self._clone
        self._inner._compile_context = self._compile_context

    def _clone(self):
        return MarkerQuery(self._inner_clone(self._inner))

    def _compile_context(self, labels=True):
        context = self._inner_compile_context(self._inner, labels)
        comment = self._attributes.get(COMMENT_ATTR_KEY) 
        if comment is not None:
            context.statement = make_marked_clause_element(context.statement, comment)
        return context


def find_caller(excluded=set()):
    stack = extract_stack()
    x = itertools.dropwhile(lambda e: e[0] in excluded, reversed(stack))
    try:
        entry = x.next()
        return format_list([entry])[0]
    except StopIteration:
        pass
    return None

def build_exclusion(inner):
    excluded = base_exclusion.copy()
    while inner is not None:
        m = inspect.getmodule(inner)
        excluded.update(get_files_for(m))
        if not hasattr(inner, '_inner'):
            break
        inner = inner._inner
    return excluded

def add_location_marker(inner):
    caller = find_caller(build_exclusion(inner))
    if caller:
        comment = caller.strip().partition('\n')[0]
        inner = inner.options(MarkerOption(comment))
    return inner

def SessionFactoryFactory(class_, wrapper=lambda inner: add_location_marker(MarkerQuery(inner))):
    class _(class_):
        def __init__(self, **kwargs):
            query_cls = kwargs.get('query_cls', Query)
            kwargs['query_cls'] = lambda entities, session, **kwargs: wrapper(query_cls(entities, session, **kwargs))
            class_.__init__(self, **kwargs)
    return _
