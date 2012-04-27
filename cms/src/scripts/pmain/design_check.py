# -*- coding:utf-8 -*-
import datetime
import json
import os
import functools
from pyramid import testing
import transaction

import altaircms.helpers as h
from altaircms.models import DBSession
from altaircms.models import Base
from altaircms.layout.models import Layout
from altaircms.event.models import Event
from altaircms.page.models import Page, PageSet
from altaircms.models import Performance
from altaircms.models import Ticket
from altaircms.asset.helpers import create_asset

here = os.path.abspath(os.path.dirname(__file__))

def setup():
    Base.metadata.bind.echo = True
    Base.metadata.drop_all();
    Base.metadata.create_all();

def import_symbol(symbol_string):
    """ foo.bar.baz:symbol_name"""
    if ":" in symbol_string:
        module, symbol = symbol_string.split(":", 1)
    else:
        module, symbol  = symbol_string, None

    m = __import__(module)
    if "." in module:
        for k in module.split(".")[1:]:
            m = getattr(m, k)

    if symbol:
        return getattr(m, symbol)
    else:
        return m

def append_to_json_structure(page, key, data):
    structure = json.loads(page.structure)
    if structure.get(key) is None:
        structure[key] = []
    structure[key].append(data)
    page.structure = json.dumps(structure)
    return page

def main_image(fpath, params):
    captured = dict(type="image", 
                    filepath=testing.DummyResource(filename=fpath, 
                                                   file= open(fpath, "rb")))
    return create_asset(captured, params=params)


def add_widget(view, resource, kind, page, block_name, params):
    request = testing.DummyRequest()
    request.json_body = dict(page_id=page.id, data=params)
    context = resource(request)
    request.context = context
    r = view(request).create()
    append_to_json_structure(page, block_name, 
                                  {"name": kind, "pk": r["pk"]})

add_image_widget = functools.partial(
    add_widget, 
    import_symbol("altaircms.plugins.widget.image.views:ImageWidgetView"), 
    import_symbol("altaircms.plugins.widget.image.models:ImageWidgetResource"), 
    import_symbol("altaircms.plugins.widget.image.models:ImageWidget").type, 
    )

add_menu_widget = functools.partial(
    add_widget, 
    import_symbol("altaircms.plugins.widget.menu.views:MenuWidgetView"), 
    import_symbol("altaircms.plugins.widget.menu.models:MenuWidgetResource"), 
    import_symbol("altaircms.plugins.widget.menu.models:MenuWidget").type, 
    )

add_freetext_widget = functools.partial(
    add_widget, 
    import_symbol("altaircms.plugins.widget.freetext.views:FreetextWidgetView"), 
    import_symbol("altaircms.plugins.widget.freetext.models:FreetextWidgetResource"), 
    import_symbol("altaircms.plugins.widget.freetext.models:FreetextWidget").type, 
    )

add_performancelist_widget = functools.partial(
    add_widget, 
    import_symbol("altaircms.plugins.widget.performancelist.views:PerformancelistWidgetView"), 
    import_symbol("altaircms.plugins.widget.performancelist.models:PerformancelistWidgetResource"), 
    import_symbol("altaircms.plugins.widget.performancelist.models:PerformancelistWidget").type, 
    )

add_breadcrumbs_widget = functools.partial(
    add_widget, 
    import_symbol("altaircms.plugins.widget.breadcrumbs.views:BreadcrumbsWidgetView"), 
    import_symbol("altaircms.plugins.widget.breadcrumbs.models:BreadcrumbsWidgetResource"), 
    import_symbol("altaircms.plugins.widget.breadcrumbs.models:BreadcrumbsWidget").type, 
    )

add_calendar_widget = functools.partial(
    add_widget, 
    import_symbol("altaircms.plugins.widget.calendar.views:CalendarWidgetView"), 
    import_symbol("altaircms.plugins.widget.calendar.models:CalendarWidgetResource"), 
    import_symbol("altaircms.plugins.widget.calendar.models:CalendarWidget").type, 
    )

add_ticketlist_widget = functools.partial(
    add_widget, 
    import_symbol("altaircms.plugins.widget.ticketlist.views:TicketlistWidgetView"), 
    import_symbol("altaircms.plugins.widget.ticketlist.models:TicketlistWidgetResource"), 
    import_symbol("altaircms.plugins.widget.ticketlist.models:TicketlistWidget").type, 
    )

add_summary_widget = functools.partial(
    add_widget, 
    import_symbol("altaircms.plugins.widget.summary.views:SummaryWidgetView"), 
    import_symbol("altaircms.plugins.widget.summary.models:SummaryWidgetResource"), 
    import_symbol("altaircms.plugins.widget.summary.models:SummaryWidget").type, 
    )

add_countdown_widget = functools.partial(
    add_widget, 
    import_symbol("altaircms.plugins.widget.countdown.views:CountdownWidgetView"), 
    import_symbol("altaircms.plugins.widget.countdown.models:CountdownWidgetResource"), 
    import_symbol("altaircms.plugins.widget.countdown.models:CountdownWidget").type, 
    )

add_iconset_widget = functools.partial(
    add_widget, 
    import_symbol("altaircms.plugins.widget.iconset.views:IconsetWidgetView"), 
    import_symbol("altaircms.plugins.widget.iconset.models:IconsetWidgetResource"), 
    import_symbol("altaircms.plugins.widget.iconset.models:IconsetWidget").type, 
    )



## settings


def detail_layout():
    layout = Layout(
        title = u"ticketstar.detail",
        template_filename = "ticketstar.detail.mako",
        # blocks = '[["header"], ["main", "side"],["userBox"]]',
        blocks = '[["topicPath"], ["main", "side"],["userBox"]]',
        site_id = 1, ##
        client_id = 1 ##
        )
    return layout

def detail_tickets(event):
    return [
        Ticket(event=event, 
               price=30000, 
               seattype=u"SSA席", 
               orderno=1), 
        Ticket(event=event, 
               price=15000, 
               seattype=u"SA席", 
               orderno=2), 
        Ticket(event=event, 
               price=8000, 
               seattype=u"A席", 
               orderno=3), 
        Ticket(event=event, 
               price=5000, 
               seattype=u"B席", 
               orderno=4), 
        Ticket(event=event, 
               price=3000, 
               seattype=u"C席", 
               orderno=5)
    ]

def detail_performances(event):
    ## performance
    return [
    Performance(venue=u"幕張メッセイベントホール", 
                title=event.title, 
                open_on=datetime.datetime(2011, 12, 4, 10), 
                start_on=datetime.datetime(2011, 12, 4, 10), 
                close_on=datetime.datetime(2011, 12, 4, 18), 
                backend_performance_id=9999, 
                event=event
                ), 
    Performance(venue=u"幕張メッセイベントホール", 
                title=event.title, 
                open_on=datetime.datetime(2011, 12, 11, 10), 
                start_on=datetime.datetime(2011, 12, 11, 10), 
                close_on=datetime.datetime(2011, 12, 11, 18), 
                backend_performance_id=10000, 
                event=event
                ), 
    Performance(venue=u"幕張メッセイベントホール", 
                title=event.title, 
                open_on=datetime.datetime(2011, 12, 18, 10), 
                start_on=datetime.datetime(2011, 12, 18, 10), 
                close_on=datetime.datetime(2011, 12, 18, 18), 
                backend_performance_id=10001, 
                event=event
                ), 
    Performance(venue=u"幕張メッセイベントホール", 
                title=event.title, 
                open_on=datetime.datetime(2011, 12, 18, 19), 
                start_on=datetime.datetime(2011, 12, 18, 19), 
                close_on=datetime.datetime(2011, 12, 18, 23), 
                backend_performance_id=10001, 
                event=event
                ), 
    Performance(venue=u"幕張メッセイベントホール", 
                title=event.title, 
                open_on=datetime.datetime(2011, 12, 25, 10), 
                start_on=datetime.datetime(2011, 12, 25, 10), 
                close_on=datetime.datetime(2011, 12, 25, 18), 
                backend_performance_id=10002, 
                event=event
                ), 
    Performance(venue=u"幕張メッセイベントホール", 
                title=event.title, 
                open_on=datetime.datetime(2012, 5, 25, 10), 
                start_on=datetime.datetime(2012, 5, 25, 10), 
                close_on=datetime.datetime(2012, 5, 25, 18), 
                backend_performance_id=10002, 
                event=event
                ), 
    ]
    
def detail_event():
    event = Event(title= u"ブルーマングループ IN 東京", 
                  event_open=u"2011-12-04", 
                  event_close=u"2012-5-25", 
                  deal_open=u"2011-10-1", 
                  deal_close=u"2012-5-17")
    return event

def detail_page(layout, event):
    ## for breadcrumbs
    top_page = Page.get_or_create_by_title(u"TOP")
    other_page = Page(layout= layout, 
                      title= u"イベント・その他", 
                      url= u"top/other")
    other_page_set = PageSet.get_or_create(other_page)
    other_page_set.parent = top_page.pageset
    

    detail_page = Page(description=u'チケットの販売、イベントの予約は楽天チケットで！楽天チケットは演劇、バレエ、ミュージカルなどの舞台、クラシック、オペラ、ロックなどのコンサート、野球、サッカー、格闘技などのスポーツ、その他イベントなどのチケットのオンラインショッピングサイトです。',
                       keywords= u"チケット,演劇,クラシック,オペラ,コンサート,バレエ,ミュージカル,野球,サッカー,格闘技", 
                       layout= layout, 
                       title= u'ブルーマングループ IN 東京 ',
                       url= u'event/detail',
                       event= event, 
                       structure= "{}", 
                       version= None)
    detail_page_set = PageSet.get_or_create(detail_page)
    detail_page_set.parent = other_page_set
    detail_page_set.event = event

    return detail_page


def add_header_widgets(page):
    ## bread crumbs
    add_breadcrumbs_widget(page, "topicPath", {})

def add_side_widgets(page):
    add_countdown_widget(page, "side", {"kind": "event_close"})
    
def add_main_block_widgets(page, asset):
    add_freetext_widget(page, "main", {"freetext": u"ブルーマンもついに千秋楽決定！！これがラストチャンス"})

    ## detail tab
    request = testing.DummyRequest()
    data = {u"items": json.dumps(
            [{"label": u"チケット購入", "link": h.front.to_publish_page_from_pageset(request, page.pageset)}, 
             {"label": u"ブルーマンの秘密",  "link": u"http://google.co.jp"}, 
             {"label": u"フォトギャラリー",  "link": u"http://google.co.jp"}, 
             ])}

    add_iconset_widget(page, "main", dict(kind="ticket_icon"))

    add_menu_widget(page, "main", data)

    add_image_widget(page, "main", dict(asset_id=asset.id))

    add_performancelist_widget(page, "main", {})

    add_calendar_widget(page, "main", {"calendar_type":"tab"})
    
    add_ticketlist_widget(page, "main", {})

    data = {u"items": json.dumps(
            [{"label": u"開催期間",  "content": u"2011年12月4日(日)　開場17時30分　開演18時30分"}, 
             {"label": u"会場",  "content": u"幕張メッセイベントホール"}, 
             {"label": u"席種・料金（税込）",  "content": u"一般指定　：　6,800円（税込）"}, 
             {"label": u"購入可能枚数",  "content": u"お一人様4枚まで"}, 
             {"label": u"チケット引取り方法",  "content": u"""
配送のみ　※送料別途630円頂戴いたします。

発送日のご案内】
≪10月31日までに購入されたお客様≫ご入金確認後、11月7日以降、随時発送いたします。
≪11月5日以降に購入されたお客様≫ご入金確認後、11月28日以降、随時発送いたします。"""}, 
             {"label": u"お支払い方法",  "content": u"クレジットカード決済・楽天バンク決済"}, 
             {"label": u"販売期間",  "content": u"在庫がなくなり次第、販売を終了させていただきます。"}, 
             {"label": u"注意事項",  "content": u"""年齢制限：3歳以下無料（ただし保護者1名に対し1名まで膝の上で。席が必要な場合はチケットをお買い求め下さい）
							枚数制限：お一人様4枚"""}, 
             {"label": u"お問い合わせ先",  "content": u"DISK GARAGE 03-5436-9600（平日12:00～19:00）"}]
            , ensure_ascii=False)}
    add_summary_widget(page, "main", data)


def add_detail_page_settings():
    layout = detail_layout()
    event = detail_event()
    detail_performances(event)
    detail_tickets(event)
    page = detail_page(layout, event)
    
    asset = main_image(os.path.join(here, "data/dummy.jpg"), 
                       dict(created_by_id=1, updated_by_id=1, title=u"イベント詳細トップ画像"))
    DBSession.add(page)
    DBSession.add(asset)

    DBSession.flush()
    add_header_widgets(page)
    add_side_widgets(page)
    add_main_block_widgets(page, asset)

def help_layout():
    layout = Layout(
        title = u"ticketstar.help",
        template_filename = "ticketstar.help.mako",
        blocks = '[["main", "side"]]',
        site_id = 1, ##
        client_id = 1 ##
        )
    return layout

def help_page(layout):
    help_page = Page(description=u'チケットの販売、イベントの予約は楽天チケットで！楽天チケットは演劇、バレエ、ミュージカルなどの舞台、クラシック、オペラ、ロックなどのコンサート、野球、サッカー、格闘技などのスポーツ、その他イベントなどのチケットのオンラインショッピングサイトです。',
                       keywords= u"チケット,演劇,クラシック,オペラ,コンサート,バレエ,ミュージカル,野球,サッカー,格闘技", 
                       layout= layout, 
                       title= u'ヘルプ',
                       url= u'help',
                       structure= "{}", 
                       version= None)
    PageSet.get_or_create(help_page)
    return help_page

def add_help_page_settings():
    layout = help_layout()
    page = help_page(layout)
    DBSession.add(page)

def top_layout():
    layout = Layout(
        title = u"ticketstar.top",
        template_filename = "ticketstar.top.mako",
        blocks = '[["main", "side"]]',
        site_id = 1, ##
        client_id = 1 ##
        )
    return layout

def top_page(layout):
    top_page = Page(description=u'チケットの販売、イベントの予約は楽天チケットで！楽天チケットは演劇、バレエ、ミュージカルなどの舞台、クラシック、オペラ、ロックなどのコンサート、野球、サッカー、格闘技などのスポーツ、その他イベントなどのチケットのオンラインショッピングサイトです。',
                       keywords= u"チケット,演劇,クラシック,オペラ,コンサート,バレエ,ミュージカル,野球,サッカー,格闘技", 
                       layout= layout, 
                       title= u'トップページ',
                       url= u'top!',
                       structure= "{}", 
                       version= None)
    PageSet.get_or_create(top_page)
    return top_page

def add_top_page_settings():
    layout = top_layout()
    page = top_page(layout)
    DBSession.add(page)

def main(env):
    # setup()
    add_detail_page_settings()
    add_help_page_settings()
    add_top_page_settings()
    transaction.commit()
