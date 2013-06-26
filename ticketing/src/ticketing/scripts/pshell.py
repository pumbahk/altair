# -*- encoding:utf-8 -*-
import os.path
import transaction

def setup(env):
    import ticketing.models
    import ticketing.core.models
    import ticketing.cart.models

    def nonspecial(obj, sym):
        return not sym.startswith('__')

    def declarative_only(obj, sym):
        v = getattr(obj, sym)
        return isinstance(v, type) and issubclass(v, ticketing.models.Base)

    def import_syms(obj, predicate=None):
        if hasattr(obj, '__all__'):
            syms = obj.__all__
        else:
            syms = dir(obj)
        for sym in syms:
            if (not predicate) or predicate(obj, sym):
                env[sym] = getattr(obj, sym)

    for sym in ['begin', 'commit', 'abort']:
        env[sym] = getattr(transaction, sym)
    for sym in ['DBSession', 'Base', 'Identifier']:
        env[sym] = getattr(ticketing.models, sym)
    import_syms(ticketing.core.models, lambda o, x: nonspecial(o, x) and declarative_only(o, x))
    import_syms(ticketing.cart.models, lambda o, x: nonspecial(o, x) and declarative_only(o, x))
