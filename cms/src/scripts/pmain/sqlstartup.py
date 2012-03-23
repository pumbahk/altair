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

    with block("create image asset"):
        from altaircms.asset.models import ImageAsset
        imga = ImageAsset("/static/img/samples/Abstract_Desktop_290.jpg")
        DBSession.add(imga)
        imga = ImageAsset("/static/img/samples/2.jpg")
        DBSession.add(imga)
    
    with block("create layout model"):
        from altaircms.layout.models import Layout
        layout0 = Layout()
        layout0.id = 2
        layout0.title = "two"
        layout0.template_filename = "2.mako"
        layout0.blocks = '[["content"],["footer"]]'
        layout0.site_id = 1 ##
        layout0.client_id = 1 ##
        DBSession.add(layout0)

        layout1 = Layout()
        layout1.id = 1
        layout1.title = "one"
        layout1.template_filename = "1.mako"
        layout1.blocks = '[["fulltitle"], ["description"], ["keywords"], ["js"], ["jquery"], ["style"], ["page"], ["content"],["footer"], ["js_foot"]]'
        layout1.site_id = 1 ##
        layout1.client_id = 1 ##
        DBSession.add(layout1)

    with block("create dummy movie"):
        from altaircms.asset.models import MovieAsset
        for name in ["foo.avi", "foo.wmv", "boo.mov", "boo.mp4"]:
            movie = MovieAsset(name)
            DBSession.add(movie)
        from altaircms.asset.models import FlashAsset
        for name in ["foo.swf", "boo.swf"]:
            movie = FlashAsset(name)
            DBSession.add(movie)

    with block("create role model"):
        from altaircms.auth.initial_data import insert_initial_authdata
        insert_initial_authdata()

    transaction.commit()


