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
    fname = os.path.join(here, "data/original5.image.jpg")
    captured = dict(type="image", 
                    uploadfile=dict(filename=fname, 
                                    fp = open(fname, "rb")))
    asset = create_asset(captured)
    DBSession.add(asset)
    DBSession.flush()
    return asset

def _get_topic():
    from altaircms.models import Topic
    topic = Topic(kind=u"お知らせ", 
                  title=u"公演内容変更のお知らせ1", 
                  text=u"@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@<br/>@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@<br/>@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@<br/>", 
                  publish_at=datetime.datetime.now())
    DBSession.add(topic)
    topic = Topic(kind=u"お知らせ", 
                  title=u"公演内容変更のお知らせ2", 
                  text=u"@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@<br/>@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@<br/>@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@<br/>", 
                  publish_at=datetime.datetime.now())
    DBSession.add(topic)
    topic = Topic(kind=u"お知らせ", 
                  title=u"公演内容変更のお知らせ3", 
                  text=u"@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@<br/>@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@<br/>@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@<br/>", 
                  publish_at=datetime.datetime.now())
    DBSession.add(topic)
    topic = Topic(kind=u"お知らせ", 
                  title=u"公演内容変更のお知らせ4", 
                  text=u"@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@<br/>@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@<br/>@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@<br/>", 
                  publish_at=datetime.datetime.now())
    DBSession.add(topic)
    topic = Topic(kind=u"お知らせ", 
                  title=u"公演内容変更のお知らせ5", 
                  text=u"@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@<br/>@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@<br/>@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@<br/>", 
                  publish_at=datetime.datetime.now())
    DBSession.add(topic)
    DBSession.flush()
    return topic
    
def add_widget(page):
    DBSession.flush()
    with block("menu"):
        from altaircms.plugins.widget.menu.views import MenuWidgetView
        from altaircms.plugins.widget.menu.models import MenuWidgetResource
        request = DummyRequest()
        items = [dict(label=u"松下奈緒コンサートツアー2012　for me", 
                      link=u"/f/publish/demo1"), 
                 dict(label=u"画像ギャラリー", 
                      link=u"/f/publish/demo1_garalley"), 
                 ]
        import json
        request.json_body = dict(page_id=page.id, data=dict(items=json.dumps(items)))
        context = MenuWidgetResource(request)
        request.context = context
        r = MenuWidgetView(request).create()
        append_to_json_structure(page, "page_main_title", 
                                 {"name": "menu", "pk": r["pk"]})

    with block("topic"):
        topic = _get_topic()
        from altaircms.plugins.widget.topic.views import TopicWidgetView
        from altaircms.plugins.widget.topic.models import TopicWidgetResource
        request = DummyRequest()
        request.json_body = dict(page_id=page.id, data=dict(topic=topic.id))
        context = TopicWidgetResource(request)
        request.context = context
        r = TopicWidgetView(request).create()
        append_to_json_structure(page, "page_main_title", 
                                 {"name": "topic", "pk": r["pk"]})
        
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
    with block("create event"):
        from altaircms.models import Event
        D = {
            "id": 1, 
            "title": u"松下奈緒コンサートツアー2012　for me \n supported by ＪＡバンク", 
            "subtitle": u"アイフルホーム presents\n\n", 
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
            "start_on": datetime.datetime(2012, 6, 3, 17), 
            "close_on": None
            }
        DBSession.add(Performance.from_dict(D))
        D = {
            "backend_performance_id": 2, 
            "event_id": event.id, 
            "title": u"松下奈緒コンサートツアー2012　for me", 
            "venue": u"神戸国際会館こくさいホール ", 
            "open_on": datetime.datetime(2012, 7, 16, 16, 30),  ##
            "start_on": datetime.datetime(2012, 7, 16, 17), 
            "close_on": None
            }
        DBSession.add(Performance.from_dict(D))

        ## page
        from altaircms.page.models import Page
        D = {'created_at': datetime.datetime(2012, 2, 14, 15, 13, 26, 438062),
             'description': u'松下奈緒コンサートツアー2012　for meの公演についての詳細、チケット予約',
             'event_id': event.id,
             'keywords': u'チケット,演劇,クラシック,オペラ,コンサート,バレエ,ミュージカル,野球,サッカー,格闘技',
             'layout_id': 1,
             'parent_id': None,
             'site_id': None,
             'title': u'松下奈緒コンサートツアー2012　for me - 楽天チケット',
             'updated_at': datetime.datetime(2012, 2, 14, 15, 13, 26, 438156),
             'url': u'demo1',
             "structure": "{}", 
             'version': None}
        page = Page.from_dict(D)
        DBSession.add(page)
        add_widget(page)

    transaction.commit()

    
