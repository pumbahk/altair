# -*- encoding:utf-8 -*-
import os.path

def setup(env):
    from altair.sqlahelper import get_global_db_session
    import altair.app.ticketing.famiport.models
    import altair.app.ticketing.famiport.communication.models

    def nonspecial(obj, sym):
        return not sym.startswith('__')

    def declarative_only(obj, sym):
        v = getattr(obj, sym)
        return isinstance(v, type) and issubclass(v, altair.app.ticketing.famiport.models.Base)

    def import_syms(obj, predicate=None):
        if hasattr(obj, '__all__'):
            syms = obj.__all__
        else:
            syms = dir(obj)
        for sym in syms:
            if (not predicate) or predicate(obj, sym):
                env[sym] = getattr(obj, sym)


    env['session'] = get_global_db_session(env['registry'], 'famiport')
    env['comm_session'] = get_global_db_session(env['registry'], 'famiport_comm')
    import_syms(altair.app.ticketing.famiport.models, lambda o, x: nonspecial(o, x) and declarative_only(o, x))
    import_syms(altair.app.ticketing.famiport.communication.models, lambda o, x: nonspecial(o, x) and declarative_only(o, x))
