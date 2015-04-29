import types
import functools
import inspect
import itertools

__all__ = [
    'override',
    'isoverriding',
    'make_class_factory',
    ]

overriders = set()

def override(fn):
    overriders.add(fn)
    return fn

def isoverriding(fn):
    try:
        return isinstance(fn, types.UnboundMethodType) and fn.im_func in overriders
    except TypeError:
        return False

def make_class_factory(base):
    class class_factory(base):
        def __new__(cls, name, bases, attrs):
            my_init = attrs.get('__init__') or getattr(bases[0], '__init__')
            mixin_init_pre_list = []
            mixin_init_post_list = []
            overrides = {}
            super_metaclass = cls.__base__
            if len(bases) > 0:
                _super_metaclass = getattr(bases[0], '__class__', None)
                if _super_metaclass is not None and _super_metaclass != cls:
                    super_metaclass = _super_metaclass
            for base in bases[1:]:
                mixin_init_pre = getattr(base, '__mixin_init_pre__', None)
                mixin_init_post = getattr(base, '__mixin_init_post__', None)
                if callable(mixin_init_pre):
                    mixin_init_pre_list.append(mixin_init_pre)
                if callable(mixin_init_post):
                    mixin_init_post_list.append(mixin_init_post)
                for k in dir(base):
                    fn = getattr(base, k)
                    if isoverriding(fn):
                        overrides[k] = fn

            argspec = None
            try:
                argspec = inspect.getargspec(my_init)
            except TypeError:
                pass

            def __init__(self, *args, **kwargs):
                if argspec is None:
                    _kwargs = kwargs
                else:
                    _kwargs = dict(kwargs)
                    _kwargs.update(itertools.izip(argspec.args[1:], args))
                for mixin_init_pre in mixin_init_pre_list:
                    _kwargs = mixin_init_pre(self, **_kwargs)
                for k in list(kwargs.keys()):
                    if k not in _kwargs:
                        del kwargs[k]
                if argspec is not None:
                    for i, k in enumerate(argspec.args[1:]):
                        if k in _kwargs and k not in kwargs and i < len(args):
                            if not isinstance(args, list):
                                args = list(args)
                            args[i] = _kwargs[k]
                            del _kwargs[k]
                if my_init is not None:
                    my_init(self, *args, **_kwargs)
                for mixin_init_post in mixin_init_post_list:
                    mixin_init_post(self, **_kwargs)

            def _(attrs, k, fn, override):
                attrs[k] = functools.wraps(fn)(lambda *args, **kwargs: fn(args[0], override, *args[1:], **kwargs))

            for k, fn in overrides.items():
                override = attrs.get(k)
                if override is None:
                    for base in bases:
                        override = getattr(base, k, None)
                        if override is not None:
                            break
                _(attrs, k, fn, override)
            attrs['__init__'] = __init__
            return super_metaclass.__new__(cls, name, bases, attrs)
    return class_factory
