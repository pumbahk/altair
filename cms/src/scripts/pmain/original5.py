# -*- coding:utf-8 -*-
"""
template with inheritance
"""

import datetime
import os
from contextlib import contextmanager

from pyramid.testing import DummyRequest
import transaction

from altaircms.models import DBSession
from altaircms.models import Base


def append_to_json_structure(page, key, data):
    import json
    structure = json.loads(page.structure)
    if structure.get(key) is None:
        structure[key] = []
    structure[key].append(data)
    page.structure = json.dumps(structure)
    return page

@contextmanager
def block(message):
    yield

here = os.path.abspath(os.path.dirname(__file__))

def _image_asset():
    from altaircms.asset.helpers import create_asset
    fname = os.path.join(here, "data/original5.image.jpg")
    captured = dict(type="image", 
                    uploadfile=dict(filename=fname, 
                                    fp = open(fname, "rb")))
    asset = create_asset(captured)
    DBSession.add(asset)
    DBSession.flush()
    return asset

def add_widget(page):
    with block("title"):
        ## title
        title = u'<h1 class="title" style="float: left;">松下奈緒コンサートツアー2012　for me</h1>'
        from altaircms.plugins.widget.freetext.views import FreetextWidgetView
        from altaircms.plugins.widget.freetext.models import FreetextWidgetResource
        request = DummyRequest()
        request.json_body = dict(page_id=page.id, data=dict(freetext=title))
        context = FreetextWidgetResource(request)
        request.context = context
        r = FreetextWidgetView(request).create()
        append_to_json_structure(page, "page_main_title", 
                                 {"name": "freetext", "pk": r["pk"]})
    with block("image"):
        from altaircms.plugins.widget.image.views import ImageWidgetView
        from altaircms.plugins.widget.image.models import ImageWidgetResource
        asset = _image_asset()
        request = DummyRequest()
        request.json_body = dict(page_id=page.id, data=dict(asset_id=asset.id))
        context = ImageWidgetResource(request)
        request.context = context
        r = ImageWidgetView(request).create()
        append_to_json_structure(page, "page_main_image", 
                                 {"name": "image", "pk": r["pk"]})

    with block("calendar"):
        ## title
        from altaircms.plugins.widget.calendar.views import CalendarWidgetView
        from altaircms.plugins.widget.calendar.models import CalendarWidgetResource
        request = DummyRequest()
        request.json_body = dict(page_id=page.id, 
                                 data=dict(calendar_type="term", 
                                           from_date="2012-6-3", 
                                           to_date="2012-7-16"))
        context = CalendarWidgetResource(request)
        request.context = context
        r = CalendarWidgetView(request).create()
        append_to_json_structure(page, "page_main_main", 
                                 {"name": "calendar", "pk": r["pk"]})
    with block("performancelist"):
        ## title
        from altaircms.plugins.widget.performancelist.views import PerformancelistWidgetView
        from altaircms.plugins.widget.performancelist.models import PerformancelistWidgetResource
        request = DummyRequest()
        request.json_body = dict(page_id=page.id, 
                                 data=dict())
        context = PerformancelistWidgetResource(request)
        request.context = context
        r = PerformancelistWidgetView(request).create()
        append_to_json_structure(page, "page_main_main", 
                                 {"name": "performancelist", "pk": r["pk"]})

    with block("detail"):
        ## title
        from altaircms.plugins.widget.detail.views import DetailWidgetView
        from altaircms.plugins.widget.detail.models import DetailWidgetResource
        request = DummyRequest()
        request.json_body = dict(page_id=page.id, 
                                 data=dict(kind="description_and_image"))
        context = DetailWidgetResource(request)
        request.context = context
        r = DetailWidgetView(request).create()
        append_to_json_structure(page, "page_main_main", 
                                 {"name": "detail", "pk": r["pk"]})

def init():
    Base.metadata.create_all()

    with block("create role model"):
        from altaircms.auth.initial_data import insert_initial_authdata
        insert_initial_authdata()

    with block("create event"):
        from altaircms.event.models import Event
        D = {
            "title": "", 
            "subtitle": "", 
            "description": "", 
            "place": "",  ##evue?
            "inquiry_for": "",  ##?
            "event_open": datetime.datetime.now(), 
            "event_close": datetime.datetime.now(), 
            "deal_open": datetime.datetime.now(), 
            "deal_close": datetime.datetime.now(), 
            "is_searchable": 0, 
            }
        event = Event.from_dict(D)
        DBSession.add(event)
        DBSession.flush()

        ## performance
        from altaircms.models import Performance
        D = {
            "backend_performance_id": 1, 
            "event_id": event.id, 
            "title": u"松下奈緒コンサートツアー2012　for me", 
            "venue": u"岸和田市立浪切ホール 大ホール", 
            "open_on": datetime.datetime(2012, 6, 3, 17),  ##
            "start_on": datetime.datetime(2012, 6, 3, 17), 
            "close_on": None
            }
        DBSession.add(Performance.from_dict(D))
        D = {
            "backend_performance_id": 2, 
            "event_id": event.id, 
            "title": u"松下奈緒コンサートツアー2012　for me", 
            "venue": u"神戸国際会館　こくさいホール ", 
            "open_on": datetime.datetime(2012, 7, 16, 17),  ##
            "start_on": datetime.datetime(2012, 7, 16, 17), 
            "close_on": None
            }
        DBSession.add(Performance.from_dict(D))

        ## page
        from altaircms.page.models import Page
        D = {'created_at': datetime.datetime(2012, 2, 14, 15, 13, 26, 438062),
             'description': u'松下奈緒コンサートツアー2012　for meの公演についての詳細、チケット予約',
             'event_id': event.id,
             'id': 2,
             'keywords': u'チケット,演劇,クラシック,オペラ,コンサート,バレエ,ミュージカル,野球,サッカー,格闘技',
             'layout_id': 1,
             'parent_id': None,
             'site_id': None,
             'title': u'松下奈緒コンサートツアー2012　for me - 楽天チケット',
             'updated_at': datetime.datetime(2012, 2, 14, 15, 13, 26, 438156),
             'url': u'sample_page',
             "structure": "{}", 
             'version': None}
        page = Page.from_dict(D)
        add_widget(page)
        DBSession.add(page)


    with block("create layout model"):
        from altaircms.layout.models import Layout
        layout0 = Layout()
        layout0.id = 1
        layout0.title = "original"
        layout0.template_filename = "original5.mako"
        layout0.blocks = '[["content"],["footer"]]'
        layout0.site_id = 1 ##
        layout0.client_id = 1 ##
        DBSession.add(layout0)
    transaction.commit()
    
def main(app):
    init()
    import sys
    from altaircms.front.views import rendering_page
    from altaircms.front.resources import PageRenderingResource

    request = DummyRequest()
    request.matchdict = dict(page_name="sample_page")
    import pdb; pdb.set_trace()
    context = PageRenderingResource(request)
    result = rendering_page(context, request)
    sys.stdout.write(result.body)
