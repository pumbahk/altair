# -*- coding:utf-8 -*-

"""
テスト用の決済プラグインなど
"""

import webtest
import functools
from pyramid.path import DottedNameResolver
resolver = DottedNameResolver('ticketing.core.models')

class BoosterTestApp(webtest.TestApp):

    def __init__(self, settings):
        from . import main
        app = main({}, **settings)
        super(BoosterTestApp, self).__init__(app)

    base_url = ""
    def get_index(self):
        return self.get('/')

    def post_index(self, params):
        return self.post('/', params=params)
        

def t_data(cls_name, **kwargs):
    from ticketing.models import DBSession
    cls = resolver.maybe_resolve(cls_name)
    d = cls(**kwargs)
    DBSession.add(d)
    return d

def setup():
    import ticketing.master.models
    import ticketing.core.models
    import ticketing.users.models
    from ticketing.models import Base, DBSession

def flush():
    from ticketing.models import Base, DBSession
    Base.metadata.create_all(bind=DBSession.bind)
    DBSession.flush()
