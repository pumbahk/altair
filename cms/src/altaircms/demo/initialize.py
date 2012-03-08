# -*- coding:utf-8 -*-

import datetime
import os
from contextlib import contextmanager

from pyramid.testing import DummyRequest
import transaction

from altaircms.models import DBSession


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
    from altaircms.asset.treat import create_asset
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

    with block("performancelist"):
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

    with block("calendar"):
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

    with block("ticketlist"):
        from altaircms.plugins.widget.ticketlist.views import TicketlistWidgetView
        from altaircms.plugins.widget.ticketlist.models import TicketlistWidgetResource
        request = DummyRequest()
        request.json_body = dict(page_id=page.id, 
                                 data=dict())
        context = TicketlistWidgetResource(request)
        request.context = context
        r = TicketlistWidgetView(request).create()
        append_to_json_structure(page, "page_main_ticket_price", 
                                 {"name": "ticketlist", "pk": r["pk"]})

    with block("detail"):
        from altaircms.plugins.widget.detail.views import DetailWidgetView
        from altaircms.plugins.widget.detail.models import DetailWidgetResource
        request = DummyRequest()
        request.json_body = dict(page_id=page.id, 
                                 data=dict(kind="description"))
        context = DetailWidgetResource(request)
        request.context = context
        r = DetailWidgetView(request).create()
        append_to_json_structure(page, "page_main_description", 
                                 {"name": "detail", "pk": r["pk"]})

def init():
    with block("create role model"):
        from altaircms.auth.initial_data import insert_initial_authdata
        insert_initial_authdata()

    with block("create event"):
        from altaircms.models import Event
        D = {
            "title": u"松下奈緒コンサートツアー2012　for me", 
            "subtitle": u"アイフルホーム presents\n 松下奈緒コンサートツアー2012　for me\n supported by ＪＡバンク", 
            "description": "", 
            "place": "",  ##performance.venue?
            "inquiry_for": u"【お問合せ】\nサウンドクリエーター　06-6357-4400 / www.sound-c.co.jp\n≪浪切公演≫浪切ホールチケットカウンター　072-439-4915 / www.namikiri.jp\n≪神戸公演≫神戸国際会館　078-231-8162 / www.kih.co.jp",  ##お問い合わせ?
            "event_open": datetime.date(2012, 6, 3), 
            "event_close": datetime.date(2012, 7, 16), 
            "deal_open": datetime.date(2012, 3, 3), 
            "deal_close": datetime.date(2012, 7, 12),
            "is_searchable": 0, #?
            }
        event = Event.from_dict(D)
        DBSession.add(event)
        DBSession.flush()

        ## ticket
        from altaircms.models import Ticket
        D = {
            "event": event, 
            "price": 6300, 
            "seattype": u"全席指定"
            }
        ticket = Ticket.from_dict(D)
        DBSession.add(ticket)

        ## performance
        from altaircms.models import Performance
        D = {
            "backend_performance_id": 1, 
            "event_id": event.id, 
            "title": u"松下奈緒コンサートツアー2012　for me", 
            "venue": u"岸和田市立浪切ホール 大ホール", 
            "open_on": datetime.datetime(2012, 6, 3, 16, 30),  ##
            "close_on": datetime.datetime(2012, 6, 3, 17), 
            "end_on": None
            }
        DBSession.add(Performance.from_dict(D))
        D = {
            "backend_performance_id": 2, 
            "event_id": event.id, 
            "title": u"松下奈緒コンサートツアー2012　for me", 
            "venue": u"神戸国際会館こくさいホール ", 
            "open_on": datetime.datetime(2012, 7, 16, 16, 30),  ##
            "close_on": datetime.datetime(2012, 7, 16, 17), 
            "end_on": None
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

    
