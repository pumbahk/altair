# -*- coding:utf-8 -*-

from altaircms.models import DBSession
from altaircms.models import Base
import transaction

from contextlib import contextmanager
@contextmanager
def block(message):
    yield

def setup():
    Base.metadata.bind.echo = True
    Base.metadata.drop_all();
    Base.metadata.create_all();

def main(env):
    setup()
    with block("create client"):
        import altaircms.auth.models as m
        client = m.Client()
        client.id = 1
        client.name = u"master"
        client.prefecture = u"tokyo"
        client.address = u"000"
        client.email = "foo@example.jp"
        client.contract_status = 0
        DBSession.add(client)


    with block("create page"):
        from altaircms.page.models import Page
        page = Page()
        def set_with_dict(obj, D):
            for k, v in D.items():
                setattr(obj, k, v)
            return obj
        params = {'description': u'boo',
                  'keywords': u'oo',
                  'tags': u'ooo',
                  'url': u'sample/page',
                  'layout_id': 1,
                  'title': u'boo',
                  # 'structure': u'{}'
                  }
        page = set_with_dict(page, params)
        DBSession.add(page)

    with block("create role model"):
        from altaircms.auth.initial_data import insert_initial_authdata
        insert_initial_authdata()
        
        from altaircms.auth.models import Operator
        debug_user = Operator(auth_source="debug", user_id=1, id=1, role_id=1, screen_name="debug user")
        DBSession.add(debug_user)

    ##
    from . import demo
    demo.add_initial_junk_data()
    transaction.commit()


