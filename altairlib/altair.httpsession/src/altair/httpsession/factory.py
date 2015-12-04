from .utils import asbool
import altair.timeparse

def parameters(*inherits, **params):
    def _(factory):
        __params = params
        if inherits:
            _params = {}
            for inherit in inherits:
                _params.update(inherit._altair_httpsession_parameter_annotations)
            _params.update(params)
            __params = _params
        factory._altair_httpsession_parameter_annotations = __params
        return factory
    return _


class BackendFactoryFactory(object):
    default_coercers = {
        'str': unicode,
        'bytes': bytes,
        'int': int,
        'bool': asbool,
        'float': float,
        'class': None,
        'instance': None,
        'callable': None,
        'timedelta': altair.timeparse.parse_time_spec,
        }

    def __init__(self, coercers=default_coercers):
        self.coercers = coercers

    def coerce_args(self, params, kwargs):
        _kwargs = {}
        for k, v in kwargs.items():
            nullable = False
            type_ = params.get(k)
            if type_ is not None:
                if type_.endswith('?'):
                    nullable = True
                    type_ = type_[:-1]
                if not nullable:
                    if v is None:
                        raise TypeError('%s cannot be None' % k)
                coercer = self.coercers.get(type_)
                if coercer is not None:
                    v = coercer(v)
            _kwargs[k] = v
        return _kwargs

    def __call__(self, fn, kwargs):
        params = getattr(fn, '_altair_httpsession_parameter_annotations', None)
        if params is not None:
            kwargs = self.coerce_args(params, kwargs)
        return lambda *args: fn(*args, **kwargs)
