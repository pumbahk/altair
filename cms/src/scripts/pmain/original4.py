# -*- coding:utf-8 -*-
"""
template with inheritance
"""

from contextlib import contextmanager
import transaction
import datetime

@contextmanager
def block(message):
    yield


def init():
    from altaircms.models import DBSession
    from altaircms.models import Base
    Base.metadata.create_all()

    with block("create role model"):
        from altaircms.auth.initial_data import insert_initial_authdata
        insert_initial_authdata()

    with block("create page model"):
        from altaircms.page.models import Page
        D = {'created_at': datetime.datetime(2012, 2, 14, 15, 13, 26, 438062),
             'description': u'boo',
             'event_id': None,
             'id': 2,
             'keywords': u'oo',
             'layout_id': 1,
             'parent_id': None,
             'site_id': None,
             'title': u'fofoo',
             'updated_at': datetime.datetime(2012, 2, 14, 15, 13, 26, 438156),
             'url': u'sample_page',
             'version': None}
        DBSession.add( Page.from_dict(D))

    with block("create layout model"):
        from altaircms.layout.models import Layout
        layout0 = Layout()
        layout0.id = 1
        layout0.title = "two"
        layout0.template_filename = "original4.mako"
        layout0.blocks = '[["content"],["footer"]]'
        layout0.site_id = 1 ##
        layout0.client_id = 1 ##
        DBSession.add(layout0)
    transaction.commit()
    

def main(app):
    init()
    import codecs
    import sys
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
    from altaircms.front.views import rendering_page
    from altaircms.front.resources import PageRenderingResource
    from pyramid.testing import DummyRequest

    request = DummyRequest()
    request.matchdict = dict(page_name="sample_page")
    context = PageRenderingResource(request)
    return rendering_page(context, request)

