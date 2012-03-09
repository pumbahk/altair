# -*- coding:utf-8 -*-

import datetime
import os
from pyramid.testing import DummyRequest
import transaction

from altaircms.models import DBSession
from . import append_to_json_structure
from . import block

here = os.path.abspath(os.path.dirname(__file__))
def _image_asset():
    from altaircms.asset.treat import create_asset
    fname = os.path.join(here, "data/dance.jpg")
    captured = dict(type="image", 
                    uploadfile=dict(filename=fname, 
                                    fp = open(fname, "rb")))
    asset = create_asset(captured)
    DBSession.add(asset)
    DBSession.flush()
    return asset

def add_widget(page):
    DBSession.flush()
    with block("title"):
        title = u'<h1 class="title" style="float: left;">トリニティ・アイリッシュ・ダンス</h1>'
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
                                 data=dict(calendar_type="obi"))
        context = CalendarWidgetResource(request)
        request.context = context
        r = CalendarWidgetView(request).create()
        append_to_json_structure(page, "page_main_main", 
                                 {"name": "calendar", "pk": r["pk"]})
    # with block("calendar"):
    #     from altaircms.plugins.widget.calendar.views import CalendarWidgetView
    #     from altaircms.plugins.widget.calendar.models import CalendarWidgetResource
    #     request = DummyRequest()
    #     request.json_body = dict(page_id=page.id, 
    #                              data=dict(calendar_type="term", 
    #                                        from_date="2012-7-7", 
    #                                        to_date="2012-7-16"))
    #     context = CalendarWidgetResource(request)
    #     request.context = context
    #     r = CalendarWidgetView(request).create()
    #     append_to_json_structure(page, "page_main_main", 
    #                              {"name": "calendar", "pk": r["pk"]})

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

    # with block("describe event"):
    #     describe = u'<div class="describe">芸術監督／マーク・ハワード<br/>プリンシパル・ダンサー／ギャレット・コールマン<br/>フルート・笛・バグパイプ／クリストファー・レイヤー<br/>ギター／ブレンダン・オシェイ<br/>ドラム・太鼓／バレット・ハーヴェイ<br/>※やむをえない事情により、出演者が変更となる場合があります。<br/>　予めご了承ください。</div>'
    #     from altaircms.plugins.widget.freetext.views import FreetextWidgetView
    #     from altaircms.plugins.widget.freetext.models import FreetextWidgetResource
    #     request = DummyRequest()
    #     request.json_body = dict(page_id=page.id, data=dict(freetext=describe))
    #     context = FreetextWidgetResource(request)
    #     request.context = context
    #     r = FreetextWidgetView(request).create()
    #     append_to_json_structure(page, "page_main_description", 
    #                              {"name": "freetext", "pk": r["pk"]})

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
    with block("create event"):
        from altaircms.models import Event
        D = {
            "title": u"トリニティアイリッシュ・ダンス", 
            "subtitle": u"NYタイムズが「空飛ぶ脚」と絶賛！\n世界も認めた極上のタップダンス・エンターテインメント\n待望の再来日！！\n\n", 
            "description": u"\n芸術監督／マーク・ハワード\nプリンシパル・ダンサー／ギャレット・コールマン\nフルート・笛・バグパイプ／クリストファー・レイヤー\nギター／ブレンダン・オシェイ\nドラム・太鼓／バレット・ハーヴェイ\n※やむをえない事情により、出演者が変更となる場合があります。\n　予めご了承ください。", 
            "place": "",  ##performance.venue?
            "inquiry_for": u"テレビ東京チケット事務局　03-3435-7000　（平日12：00－17：00）",  ##お問い合わせ?
            "event_open": datetime.date(2012, 7, 7), 
            "event_close": datetime.date(2012, 7, 16), 
            "deal_open": datetime.date(2012, 3, 3), 
            "deal_close": datetime.date(2012, 7, 13),
            "is_searchable": 0, #?
            }
        event = Event.from_dict(D)
        DBSession.add(event)
        DBSession.flush()

        ## ticket
        from altaircms.models import Ticket
        D = {
            "event": event, 
            "orderno": 1, 
            "price": 10000, 
            "seattype": u"S席"
            }
        ticket = Ticket.from_dict(D)
        DBSession.add(ticket)
        from altaircms.models import Ticket
        D = {
            "event": event, 
            "orderno": 2, 
            "price": 8000, 
            "seattype": u"A席"
            }
        ticket = Ticket.from_dict(D)
        DBSession.add(ticket)
        from altaircms.models import Ticket
        D = {
            "event": event, 
            "orderno": 3, 
            "price": 6000, 
            "seattype": u"B席"
            }
        ticket = Ticket.from_dict(D)
        DBSession.add(ticket)

        ## performance
        from altaircms.models import Performance
        D = {
            "backend_performance_id": 3, 
            "event_id": event.id, 
            "title": u"トリニティ・アイリッシュ・ダンス(横浜公演)", 
            "venue": u"横浜　関内ホール　大ホール", 
            "open_on": None, 
            "start_on": datetime.datetime(2012, 7, 7, 12, 30),
            "close_on": None
            }
        DBSession.add(Performance.from_dict(D))
        from altaircms.models import Performance
        D = {
            "backend_performance_id": 4, 
            "event_id": event.id, 
            "title": u"トリニティ・アイリッシュ・ダンス(横浜公演)", 
            "venue": u"横浜　関内ホール　大ホール", 
            "open_on": None, 
            "start_on": datetime.datetime(2012, 7, 7, 17, 0),
            "close_on": None
            }
        DBSession.add(Performance.from_dict(D))
        D = {
            "backend_performance_id": 5, 
            "event_id": event.id, 
            "title": u"トリニティ・アイリッシュ・ダンス(東京公演)", 
            "venue": u"Bunkamuraオーチャードホール", 
            "open_on": None, 
            "start_on": datetime.datetime(2012, 7, 14, 14, 0),  ##
            "close_on": None
            }
        DBSession.add(Performance.from_dict(D))
        D = {
            "backend_performance_id": 6, 
            "event_id": event.id, 
            "title": u"トリニティ・アイリッシュ・ダンス(東京公演)", 
            "venue": u"Bunkamuraオーチャードホール", 
            "open_on": None, 
            "start_on": datetime.datetime(2012, 7, 15, 13, 0),  ##
            "close_on": None
            }
        DBSession.add(Performance.from_dict(D))
        D = {
            "backend_performance_id": 7, 
            "event_id": event.id, 
            "title": u"トリニティ・アイリッシュ・ダンス(東京公演)", 
            "venue": u"Bunkamuraオーチャードホール", 
            "open_on": None, 
            "start_on": datetime.datetime(2012, 7, 16, 13, 0),  ##
            "close_on": None
            }
        DBSession.add(Performance.from_dict(D))
        ## page
        from altaircms.page.models import Page
        D = {'created_at': datetime.datetime(2012, 2, 14, 15, 13, 26, 438062),
             'description': u'トリニティ・アイリッシュ・ダンスの公演についての詳細、チケット予約',
             'event_id': event.id,
             'keywords': u'チケット,演劇,クラシック,オペラ,コンサート,バレエ,ミュージカル,野球,サッカー,格闘技',
             'layout_id': 1,
             'parent_id': None,
             'site_id': None,
             'title': u'トリニティ・アイリッシュ・ダンス - 楽天チケット',
             'updated_at': datetime.datetime(2012, 2, 14, 15, 13, 26, 438156),
             'url': u'demo2',
             "structure": "{}", 
             'version': None}
        page = Page.from_dict(D)
        DBSession.add(page)
        add_widget(page)
    transaction.commit()

    
