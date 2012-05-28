# -*- coding:utf-8 -*-
import datetime
import json
import os
import functools
from pyramid import testing
import transaction

import altaircms.helpers as h
from altaircms.models import (
    DBSession, Base
)
from altaircms.layout.models import Layout
from altaircms.event.models import Event
from altaircms.auth.models import (
    Client, 
    Operator
)
from altaircms.page.models import (
    Page, PageSet
)
from altaircms.models import (
    Performance, Ticket
)
from altaircms.asset.models import ImageAsset
from altaircms.topic.models import Topic
from altaircms.topcontent.models import Topcontent
from altaircms.plugins.widget.promotion.models import (
    Promotion, PromotionUnit
)
from altaircms.models import(
    Site, 
    Category
)

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

def make_image_asset(path, **params):
    captured = dict(type="image", 
                    filepath=Objlike(filename=path, 
                                     file=open(path, "rb")))
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

add_topic_widget = functools.partial(
    add_widget, 
    import_symbol("altaircms.plugins.widget.topic.views:TopicWidgetView"), 
    import_symbol("altaircms.plugins.widget.topic.models:TopicWidgetResource"), 
    import_symbol("altaircms.plugins.widget.topic.models:TopicWidget").type, 
    )

add_linklist_widget = functools.partial(
    add_widget, 
    import_symbol("altaircms.plugins.widget.linklist.views:LinklistWidgetView"), 
    import_symbol("altaircms.plugins.widget.linklist.models:LinklistWidgetResource"), 
    import_symbol("altaircms.plugins.widget.linklist.models:LinklistWidget").type, 
    )

add_heading_widget = functools.partial(
    add_widget, 
    import_symbol("altaircms.plugins.widget.heading.views:HeadingWidgetView"), 
    import_symbol("altaircms.plugins.widget.heading.models:HeadingWidgetResource"), 
    import_symbol("altaircms.plugins.widget.heading.models:HeadingWidget").type, 
    )

add_promotion_widget = functools.partial(
    add_widget, 
    import_symbol("altaircms.plugins.widget.promotion.views:PromotionWidgetView"), 
    import_symbol("altaircms.plugins.widget.promotion.models:PromotionWidgetResource"), 
    import_symbol("altaircms.plugins.widget.promotion.models:PromotionWidget").type, 
    )

add_anchorlist_widget = functools.partial(
    add_widget, 
    import_symbol("altaircms.plugins.widget.anchorlist.views:AnchorlistWidgetView"), 
    import_symbol("altaircms.plugins.widget.anchorlist.models:AnchorlistWidgetResource"), 
    import_symbol("altaircms.plugins.widget.anchorlist.models:AnchorlistWidget").type, 
    )

add_purchase_widget = functools.partial(
    add_widget, 
    import_symbol("altaircms.plugins.widget.purchase.views:PurchaseWidgetView"), 
    import_symbol("altaircms.plugins.widget.purchase.models:PurchaseWidgetResource"), 
    import_symbol("altaircms.plugins.widget.purchase.models:PurchaseWidget").type, 
    )

class Objlike(dict):
    __getattr__ = dict.__getitem__

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
                end_on=datetime.datetime(2011, 12, 4, 18), 
                backend_id=9999, 
                prefecture="tokyo", 
                event=event
                ), 
    Performance(venue=u"幕張メッセイベントホール", 
                title=event.title, 
                open_on=datetime.datetime(2011, 12, 11, 10), 
                start_on=datetime.datetime(2011, 12, 11, 10), 
                end_on=datetime.datetime(2011, 12, 11, 18), 
                backend_id=10000, 
                prefecture="tokyo", 
                event=event
                ), 
    Performance(venue=u"幕張メッセイベントホール", 
                title=event.title, 
                open_on=datetime.datetime(2011, 12, 18, 10), 
                start_on=datetime.datetime(2011, 12, 18, 10), 
                end_on=datetime.datetime(2011, 12, 18, 18), 
                backend_id=10001, 
                prefecture="tokyo", 
                event=event
                ), 
    Performance(venue=u"幕張メッセイベントホール", 
                title=event.title, 
                open_on=datetime.datetime(2011, 12, 18, 19), 
                start_on=datetime.datetime(2011, 12, 18, 19), 
                end_on=datetime.datetime(2011, 12, 18, 23), 
                backend_id=10001, 
                prefecture="tokyo", 
                event=event
                ), 
    Performance(venue=u"幕張メッセイベントホール", 
                title=event.title, 
                open_on=datetime.datetime(2011, 12, 25, 10), 
                start_on=datetime.datetime(2011, 12, 25, 10), 
                end_on=datetime.datetime(2011, 12, 25, 18), 
                backend_id=10002, 
                prefecture="tokyo", 
                event=event
                ), 
    Performance(venue=u"幕張メッセイベントホール", 
                title=event.title, 
                open_on=datetime.datetime(2012, 5, 25, 10), 
                start_on=datetime.datetime(2012, 5, 25, 10), 
                end_on=datetime.datetime(2012, 5, 25, 18), 
                backend_id=10002, 
                prefecture="gunma", 
                event=event
                ), 
    ]
    

def detail_event():
    event = Event(title= u"ブルーマングループ IN 東京", 
                  backend_id=1,  ##todo:バックエンド側のidを保持するはず。ここで直接指定するのはあまりよくない
                  event_open=u"2012-12-04", 
                  event_close=u"2013-5-25", 
                  deal_open=u"2013-10-1", 
                  deal_close=u"2013-5-17")
    return event


def detail_page(layout, event):
    ## for breadcrumbs
    top_page = Page.get_or_create_by_title(u"TOP")
    other_page = Page.get_or_create_by_title(title= u"イベント・その他")
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
    return detail_page



def add_header_widgets(page):
    ## bread crumbs
    add_breadcrumbs_widget(page, "topicPath", {})


def add_side_widgets(page):
    add_countdown_widget(page, "side", {"kind": "event_close"})
    

def add_detail_main_block_widgets(page, asset):
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

    data = {"external_link": None, "kind": "simple"}
    add_purchase_widget(page, "main", data)

    # data = {"external_link": "http://example.com", "kind": "simple"}
    # add_purchase_widget(page, "main", data)


def add_detail_page_settings():
    layout = detail_layout()
    event = detail_event()
    detail_performances(event)
    detail_tickets(event)
    page = detail_page(layout, event)
    
    asset = make_image_asset(os.path.join(here, "data/dummy.jpg"), 
                             created_by_id=1, updated_by_id=1, title=u"イベント詳細トップ画像")
    DBSession.add(page)
    DBSession.add(asset)

    DBSession.flush()
    add_header_widgets(page)
    add_side_widgets(page)
    add_detail_main_block_widgets(page, asset)


### help


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


def help_topics():
    return [
        Topic(kind=u"ヘルプ", 
              subkind=u"会員登録・ログイン", 
              text=u"楽天会員情報の管理よりお手続きください。", 
              title=u"会員ID忘れてしまいました", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 
        Topic(kind=u"ヘルプ", 
              subkind=u"会員登録・ログイン", 
              text=u"回答が入ります", 
              title=u"パスワードを忘れてしまいました。", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 
        Topic(kind=u"ヘルプ", 
              subkind=u"会員登録・ログイン", 
              text=u"回答が入ります", 
              title=u"登録している住所やメールアドレスの変更はできますか？", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 

        Topic(kind=u"ヘルプ", 
              subkind=u"チケット予約・購入", 
              text=u"回答が入ります", 
              title=u"座席を指定しての申し込みはできますか？", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 
        Topic(kind=u"ヘルプ", 
              subkind=u"チケット予約・購入", 
              text=u"回答が入ります", 
              title=u"座席はならびで取ることはできますか？", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 
        Topic(kind=u"ヘルプ", 
              subkind=u"チケット予約・購入", 
              text=u"回答が入ります", 
              title=u"一般予約の申し込み方法を教えてください。", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 
        Topic(kind=u"ヘルプ", 
              subkind=u"チケット予約・購入", 
              text=u"回答が入ります", 
              title=u"申し込みしたチケットの座席番号確認はできますか？", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 
        Topic(kind=u"ヘルプ", 
              subkind=u"チケット予約・購入", 
              text=u"回答が入ります", 
              title=u"一度申込みしたチケットの取り消しはできますか？", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 
        Topic(kind=u"ヘルプ", 
              subkind=u"チケット予約・購入", 
              text=u"回答が入ります", 
              title=u"ＰＣから、チケットの申込みができませんでした。", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 
        Topic(kind=u"ヘルプ", 
              subkind=u"チケット予約・購入", 
              text=u"回答が入ります", 
              title=u"チケットの予約・購入履歴を確認したい。", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 

        Topic(kind=u"ヘルプ", 
              subkind=u"支払い方法・引取り方法", 
              text=u"楽天会員情報の管理よりお手続きください。", 
              title=u"会員ID忘れてしまいました", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 
        Topic(kind=u"ヘルプ", 
              subkind=u"支払い方法・引取り方法", 
              text=u"回答が入ります", 
              title=u"パスワードを忘れてしまいました。", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 
        Topic(kind=u"ヘルプ", 
              subkind=u"支払い方法・引取り方法", 
              text=u"回答が入ります", 
              title=u"登録している住所やメールアドレスの変更はできますか？", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 

        Topic(kind=u"ヘルプ", 
              subkind=u"ヘルプ：本人認証サービス(3Dセキュアサービス)について", 
              text=u"楽天会員情報の管理よりお手続きください。", 
              title=u"会員ID忘れてしまいました", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 
        Topic(kind=u"ヘルプ", 
              subkind=u"ヘルプ：本人認証サービス(3Dセキュアサービス)について", 
              text=u"回答が入ります", 
              title=u"パスワードを忘れてしまいました。", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 
        Topic(kind=u"ヘルプ", 
              subkind=u"ヘルプ：本人認証サービス(3Dセキュアサービス)について", 
              text=u"回答が入ります", 
              title=u"登録している住所やメールアドレスの変更はできますか？", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 

        Topic(kind=u"ヘルプ", 
              subkind=u"本人認証サービス(3Dセキュアサービス)について", 
              text=u"楽天会員情報の管理よりお手続きください。", 
              title=u"会員ID忘れてしまいました", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 
        Topic(kind=u"ヘルプ", 
              subkind=u"本人認証サービス(3Dセキュアサービス)について", 
              text=u"回答が入ります", 
              title=u"パスワードを忘れてしまいました。", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 
        Topic(kind=u"ヘルプ", 
              subkind=u"本人認証サービス(3Dセキュアサービス)について", 
              text=u"回答が入ります", 
              title=u"登録している住所やメールアドレスの変更はできますか？", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 

        Topic(kind=u"ヘルプ", 
              subkind=u"セブンーイレブン引取り", 
              text=u"楽天会員情報の管理よりお手続きください。", 
              title=u"会員ID忘れてしまいました", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 
        Topic(kind=u"ヘルプ", 
              subkind=u"セブンーイレブン引取り", 
              text=u"回答が入ります", 
              title=u"パスワードを忘れてしまいました。", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 
        Topic(kind=u"ヘルプ", 
              subkind=u"セブンーイレブン引取り", 
              text=u"回答が入ります", 
              title=u"登録している住所やメールアドレスの変更はできますか？", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 

        ]

def add_help_side_block_widgets(page):
    add_anchorlist_widget(page, "side", {})

def add_help_main_block_widgets(page):
    params = dict(kind=u"チケットスター：ヘルプページ見出し", 
                  text=u"会員登録・ログイン")
    add_heading_widget(page, "main", params)

    params =  {"kind": u"ヘルプ", 
               "subkind": u"会員登録・ログイン", 
               "display_count": 100, 
               "display_global": True, 
               "display_event": True, 
               "display_page": True}
    add_topic_widget(page, "main",  params)

    params = dict(kind=u"チケットスター：ヘルプページ見出し", 
                  text=u"チケット予約・購入")
    add_heading_widget(page, "main", params)

    params =  {"kind": u"ヘルプ", 
               "subkind": u"チケット予約・購入", 
               "display_count": 100, 
               "display_global": True, 
               "display_event": True, 
               "display_page": True}
    add_topic_widget(page, "main",  params)

    params = dict(kind=u"チケットスター：ヘルプページ見出し", 
                  text=u"支払い方法・引取り方法")
    add_heading_widget(page, "main", params)

    params =  {"kind": u"ヘルプ", 
               "subkind": u"支払い方法・引取り方法", 
               "display_count": 100, 
               "display_global": True, 
               "display_event": True, 
               "display_page": True}
    add_topic_widget(page, "main",  params)

    params = dict(kind=u"チケットスター：ヘルプページ見出し", 
                  text=u"本人認証サービス(3Dセキュアサービス)について")
    add_heading_widget(page, "main", params)

    params =  {"kind": u"ヘルプ", 
               "subkind": u"本人認証サービス(3Dセキュアサービス)について", 
               "display_count": 100, 
               "display_global": True, 
               "display_event": True, 
               "display_page": True}
    add_topic_widget(page, "main",  params)

    params = dict(kind=u"チケットスター：ヘルプページ見出し", 
                  text=u"セブンーイレブン引取り")
    add_heading_widget(page, "main", params)

    params =  {"kind": u"ヘルプ", 
               "subkind": u"セブンーイレブン引取り", 
               "display_count": 100, 
               "display_global": True, 
               "display_event": True, 
               "display_page": True}
    add_topic_widget(page, "main",  params)



def add_help_page_settings():
    layout = help_layout()
    topics = help_topics()
    page = help_page(layout)

    DBSession.add(page)
    DBSession.add_all(topics)

    DBSession.flush()

    add_help_main_block_widgets(page)
    add_help_side_block_widgets(page)


### 公演中止・変更情報


def change_layout():
    layout = Layout(
        title = u"ticketstar.change",
        template_filename = "ticketstar.change.mako",
        blocks = '[["main", "side"]]',
        site_id = 1, ##
        client_id = 1 ##
        )
    return layout


def change_page(layout):
    change_page = Page(description=u'チケットの販売、イベントの予約は楽天チケットで！楽天チケットは演劇、バレエ、ミュージカルなどの舞台、クラシック、オペラ、ロックなどのコンサート、野球、サッカー、格闘技などのスポーツ、その他イベントなどのチケットのオンラインショッピングサイトです。',
                       keywords= u"チケット,演劇,クラシック,オペラ,コンサート,バレエ,ミュージカル,野球,サッカー,格闘技", 
                       layout= layout, 
                       title= u'公演の中止・変更情報',
                       url= u'change',
                       structure= "{}", 
                       version= None)
    PageSet.get_or_create(change_page)
    return change_page


def change_topics():
    return [
        Topic(kind=u"公演中止情報", 
              text=u"""平素は楽天チケットをご利用頂き誠にありがとうございます。

4月11日(水)、楽天対西武戦は天候ならびにグラウンドコンディション不良のため、中止が決定しました。
入場券は下記の要領にて払戻しいたします。

■対象試合
・4月11日(水)　楽天イーグルスvs埼玉西武ライオンズ

■払戻期間
・中止翌日より14日間

【クレジットカード決済・セブン-イレブン引取りのお客様】
◆既にセブン-イレブンでチケットにお引換いただいている場合
⇒ご購入店舗にて現金で払い戻しとなります。

◆まだセブン-イレブンでチケットをお引換いただいていない場合
⇒返金時期は、各クレジットカード会社により異なりますので、詳細はカード会社へご確認ください。

【クレジットカード決済・配送引取りのお客様】
⇒クレジットカード会社よりご登録口座へ自動返金となります。
返金時期は、各クレジットカード会社により異なりますので、詳細はカード会社へご確認ください。

【クレジットカード決済・窓口引取りのお客様】
⇒クレジットカード会社よりご登録口座へ自動返金となります。
返金時期は、各クレジットカード会社により異なりますので、詳細はカード会社へご確認ください。

【セブン-イレブン支払・セブン-イレブン引取りのお客様】
⇒チケットをご持参頂き、ご購入店舗で払い戻しを行ってください。

※ご購入の際の各種手数料(発券手数料・サービス利用料等)の返金はいたしません。予めご了承ください。""", 
              title=u"2012/4/11 楽天イーグルス　雨天等中止時の払戻しについて", 
              subkind=u"2012/4/11 楽天イーグルス　雨天等中止時の払戻しについて", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 

        Topic(kind=u"公演中止情報", 
              text=u"""平素は楽天チケットをご利用頂き誠にありがとうございます。

4月11日(水)、楽天対西武戦は天候ならびにグラウンドコンディション不良のため、中止が決定しました。
入場券は下記の要領にて払戻しいたします。

閉じる
""", 
              title=u"2012/1/20 『au presents　オンタマカーニバル2012』払い戻しに関するご案内", 
              subkind=u"2012/1/20 『au presents　オンタマカーニバル2012』払い戻しに関するご案内", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 

        Topic(kind=u"公演中止情報", 
              text=u"""平素は楽天チケットをご利用頂き誠にありがとうございます。

4月11日(水)、楽天対西武戦は天候ならびにグラウンドコンディション不良のため、中止が決定しました。
入場券は下記の要領にて払戻しいたします。

閉じる
""", 
              title=u"2011/9/28 『ボローニャ歌劇場』2011年9月21日(水)「清教徒」公演 払い戻しに関するご案内", 
              subkind=u"2011/9/28 『ボローニャ歌劇場』2011年9月21日(水)「清教徒」公演 払い戻しに関するご案内", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 

        Topic(kind=u"公演中止情報", 
              text=u"""平素は楽天チケットをご利用頂き誠にありがとうございます。

4月11日(水)、楽天対西武戦は天候ならびにグラウンドコンディション不良のため、中止が決定しました。
入場券は下記の要領にて払戻しいたします。

閉じる
""", 
              title=u"2011/9/28 『ボローニャ歌劇場』2011年9月21日(水)「清教徒」公演 払い戻しに関するご案内", 
              subkind=u"2011/9/28 『ボローニャ歌劇場』2011年9月21日(水)「清教徒」公演 払い戻しに関するご案内", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 

        Topic(kind=u"公演中止情報", 
              text=u"""平素は楽天チケットをご利用頂き誠にありがとうございます。

4月11日(水)、楽天対西武戦は天候ならびにグラウンドコンディション不良のため、中止が決定しました。
入場券は下記の要領にて払戻しいたします。

閉じる
""", 
              title=u"2011/9/28 『ボローニャ歌劇場』2011年9月21日(水)「清教徒」公演 払い戻しに関するご案内", 
              subkind=u"2011/9/28 『ボローニャ歌劇場』2011年9月21日(水)「清教徒」公演 払い戻しに関するご案内", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 
        ]

def add_change_side_block_widgets(page):
    add_anchorlist_widget(page, "side", {})

def add_change_main_block_widgets(page):
    params = dict(kind=u"チケットスター：公演中止情報ページ見出し", 
                  text=u"2012/4/11 楽天イーグルス　雨天等中止時の払戻しについて")
    add_heading_widget(page, "main", params)

    params =  {"kind": u"公演中止情報", 
               "subkind": u"2012/4/11 楽天イーグルス　雨天等中止時の払戻しについて", 
               "display_count": 100, 
               "display_global": True, 
               "display_event": True, 
               "display_page": True}
    add_topic_widget(page, "main",  params)

    params = dict(kind=u"チケットスター：公演中止情報ページ見出し", 
                  text=u"2012/1/20 『au presents　オンタマカーニバル2012』払い戻しに関するご案内")
    add_heading_widget(page, "main", params)

    params =  {"kind": u"公演中止情報", 
               "subkind": u"2012/1/20 『au presents　オンタマカーニバル2012』払い戻しに関するご案内", 
               "display_count": 100, 
               "display_global": True, 
               "display_event": True, 
               "display_page": True}
    add_topic_widget(page, "main",  params)

    params = dict(kind=u"チケットスター：公演中止情報ページ見出し", 
                  text=u"2011/9/28 『ボローニャ歌劇場』2011年9月21日(水)「清教徒」公演 払い戻しに関するご案内")
    add_heading_widget(page, "main", params)

    params =  {"kind": u"公演中止情報", 
               "subkind": u"2011/9/28 『ボローニャ歌劇場』2011年9月21日(水)「清教徒」公演 払い戻しに関するご案内", 
               "display_count": 100, 
               "display_global": True, 
               "display_event": True, 
               "display_page": True}
    add_topic_widget(page, "main",  params)



def add_change_page_settings():
    layout = change_layout()
    topics = change_topics()
    page = change_page(layout)

    DBSession.add(page)
    DBSession.add_all(topics)

    DBSession.flush()

    add_change_main_block_widgets(page)
    add_change_side_block_widgets(page)


### first

def first_layout():
    layout = Layout(
        title = u"ticketstar.first",
        template_filename = "ticketstar.first.mako",
        blocks = '[["main", "side"]]',
        site_id = 1, ##
        client_id = 1 ##
        )
    return layout


def first_page(layout):
    first_page = Page(description=u'チケットの販売、イベントの予約は楽天チケットで！楽天チケットは演劇、バレエ、ミュージカルなどの舞台、クラシック、オペラ、ロックなどのコンサート、野球、サッカー、格闘技などのスポーツ、その他イベントなどのチケットのオンラインショッピングサイトです。',
                       keywords= u"チケット,演劇,クラシック,オペラ,コンサート,バレエ,ミュージカル,野球,サッカー,格闘技", 
                       layout= layout, 
                       title= u'初めての方へ',
                       url= u'first',
                       structure= "{}", 
                       version= None)
    PageSet.get_or_create(first_page)
    return first_page


def first_topics():
    return [
        Topic(kind=u"ヘルプ", 
              subkind=u"チケット購入・引取", 
              text=u"楽天会員情報の管理よりお手続きください。", 
              title=u"会員ID忘れてしまいました", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True), 
        ]

def add_first_side_block_widgets(page):
    add_anchorlist_widget(page, "side", {})

def add_first_main_block_widgets(page):
    params = dict(kind=u"チケットスター：ヘルプページ見出し", 
                  text=u"チケット購入・引取")
    add_heading_widget(page, "main", params)

    params =  {"kind": u"ヘルプ", 
               "subkind": u"チケット購入・引取", 
               "display_count": 100, 
               "display_global": True, 
               "display_event": True, 
               "display_page": True}
    add_topic_widget(page, "main",  params)

    params = dict(kind=u"チケットスター：ヘルプページ見出し", 
                  text=u"動作環境・セキュリティ")
    add_heading_widget(page, "main", params)

    params =  {"kind": u"ヘルプ", 
               "subkind": u"動作環境・セキュリティ", 
               "display_count": 100, 
               "display_global": True, 
               "display_event": True, 
                "display_page": True}
    add_topic_widget(page, "main",  params)

    params = dict(kind=u"チケットスター：ヘルプページ見出し", 
                  text=u"ヘルプ")
    add_heading_widget(page, "main", params)

    params =  {"kind": u"ヘルプ", 
               "subkind": u"ヘルプ", 
               "display_count": 100, 
               "display_global": True, 
               "display_event": True, 
               "display_page": True}
    add_topic_widget(page, "main",  params)

def add_first_page_settings():
    layout = first_layout()
    topics = first_topics()
    page = first_page(layout)

    DBSession.add(page)
    DBSession.add_all(topics)

    DBSession.flush()

    add_first_main_block_widgets(page)
    add_first_side_block_widgets(page)



### sports

def sports_layout():
    layout = Layout(
        title = u"ticketstar.sports",
        template_filename = "ticketstar.sports.mako",
        blocks = '[["main"], ["main_left", "main_right"], ["main_bottom"], ["side"]]',
        site_id = 1, ##
        client_id = 1 ##
        )
    return layout


def sports_page(layout):
    sports_page = Page(description=u'チケットの販売、イベントの予約は楽天チケットで！楽天チケットは演劇、バレエ、ミュージカルなどの舞台、クラシック、オペラ、ロックなどのコンサート、野球、サッカー、格闘技などのスポーツ、その他イベントなどのチケットのオンラインショッピングサイトです。',
                       keywords= u"チケット,演劇,クラシック,オペラ,コンサート,バレエ,ミュージカル,野球,サッカー,格闘技", 
                       layout= layout, 
                       title= u'スポーツ',
                       url= u'sports',
                       structure= "{}", 
                       version= None)
    PageSet.get_or_create(sports_page)
    return sports_page


def sports_topics():
    return [
        Topic(kind=u"トピックス", 
              subkind=u"スポーツ", 
              text=u"#", 
              title=u"ポイント10倍キャンペーン実施中！『大相撲三月場所』マス席の他、希少な溜まり席も販売！", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True, 
              orderno=1), 
        Topic(kind=u"トピックス", 
              subkind=u"スポーツ", 
              text=u"#", 
              title=u"きゃりーぱみゅぱみゅ、倖田來未 、CNBLUE ら出演♪「オンタマカーニバル2012」1/14発売！", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True, 
              orderno=2), 

        ]



def sports_promotion():
    img_path = os.path.join(os.path.dirname(__file__), "../../static/mock/img/")
    N = 6
    def make_materials(i, imgname, thumbname):
        main_image = (ImageAsset.query.filter_by(title=imgname).first() or 
                      make_image_asset(os.path.join(img_path, imgname), title=imgname))
        thumbnail = (ImageAsset.query.filter_by(title=thumbname).first() or 
                     make_image_asset(os.path.join(img_path, thumbname),title=thumbname))
        return PromotionUnit(main_image=main_image,
                             thumbnail=thumbnail, 
                             link="http://www.google.com", 
                             text=u"何かここにメッセージ書く。ファイル名:%s" % imgname, 
                             )
    punits = [make_materials(i, "%d.jpg" % i, "thumb.%d.jpg" % i) for i in range(1, N)]
    return Promotion(promotion_units=punits, 
                     name=u"スポーツ promotioin枠")
    

def add_sports_main_block_widgets(page, promotion):
    params =  {"kind": u"トピックス", 
               "display_count": 2, 
               "display_global": True, 
               "display_event": False, 
               "display_page": False}
    add_topic_widget(page, "main", params)

    add_promotion_widget(page, "main", {"promotion": promotion.id, 
                                        "kind": u"チケットスター:カテゴリTopプロモーション枠"})

    params = dict(kind=u"チケットスター：スポーツ見出し", 
                  text=u"トピックス")
    add_heading_widget(page, "main", params)

    params =  {"kind": u"トピックス", 
               "subkind": u"スポーツ", 
               "display_count": 5, 
               "display_global": True, 
               "display_event": False, 
               "display_page": False}
    add_topic_widget(page, "main", params)

    params = dict(kind=u"チケットスター：スポーツ見出し", 
                  text=u"注目のイベント")
    add_heading_widget(page, "main", params)

    params =  {"kind": u"注目のイベント", 
               "topic_type": "hasimage", 
               "display_count": 8, 
               "display_global": True, 
               "display_event": True, 
               "display_page": True}
    add_topic_widget(page, "main", params)

    params = dict(kind=u"チケットスター：トップページ見出し", 
                  text=u"今週発売のチケット")
    add_heading_widget(page, "main_left", params)

    params = {"finder_kind": "thisWeek", 
              "delimiter": u"/"}
    add_linklist_widget(page, "main_left", params)

    params = dict(kind=u"チケットスター：トップページ見出し", 
                  text=u"販売終了間近")
    add_heading_widget(page, "main_right", params)

    params = {"finder_kind": "nearTheEnd", 
              "delimiter": u"/"}
    add_linklist_widget(page, "main_right", params)


    ## sidebar
    params = dict(kind=u"チケットスター：サイドバー見出し", 
                  text=u"特集")
    add_heading_widget(page, "side", params)

    params =  {"kind": u"特集(サブカテゴリ)", 
               "display_count": 3, 
               "display_global": False, 
               "display_event": False, 
               "display_page": True}
    add_topic_widget(page, "side", params)

def add_sports_page_settings():
    layout = sports_layout()
    topics = sports_topics()
    promotion = sports_promotion()
    page = sports_page(layout)

    DBSession.add(page)
    DBSession.add(promotion)
    DBSession.add_all(topics)

    DBSession.flush()
    
    add_sports_main_block_widgets(page, promotion)#



### 音楽カテゴリ


def music_layout():
    layout = Layout(
        title = u"ticketstar.music",
        template_filename = "ticketstar.music.mako",
        blocks = '[["main"], ["main_left", "main_right"], ["main_bottom"], ["side"]]',
        site_id = 1, ##
        client_id = 1 ##
        )
    return layout


def music_page(layout):
    music_page = Page(description=u'チケットの販売、イベントの予約は楽天チケットで！楽天チケットは演劇、バレエ、ミュージカルなどの舞台、クラシック、オペラ、ロックなどのコンサート、野球、サッカー、格闘技などの音楽、その他イベントなどのチケットのオンラインショッピングサイトです。',
                       keywords= u"チケット,演劇,クラシック,オペラ,コンサート,バレエ,ミュージカル,野球,サッカー,格闘技", 
                       layout= layout, 
                       title= u'音楽',
                       url= u'music',
                       structure= "{}", 
                       version= None)
    PageSet.get_or_create(music_page)
    return music_page


def music_topics(page):
    return [
        Topic(kind=u"トピックス", 
              subkind=u"音楽", 
              text=u"#", 
              title=u"ポイント10倍キャンペーン実施中！『大相撲三月場所』マス席の他、希少な溜まり席も販売！", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True, 
              orderno=1), 
        Topic(kind=u"トピックス", 
              subkind=u"音楽", 
              text=u"#", 
              title=u"きゃりーぱみゅぱみゅ、倖田來未 、CNBLUE ら出演♪「オンタマカーニバル2012」1/14発売！", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True, 
              orderno=2), 

        ## sidebar
        Topic(kind=u"特集(サブカテゴリ)", 
              text=u"#", 
              page=page, 
              title=u"特集/ライブハウスへ行こう!!", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=False, 
              orderno=1), 
        Topic(kind=u"特集(サブカテゴリ)", 
              text=u"#", 
              page=page, 
              title=u"ロックフェス特集", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=False, 
              orderno=2), 
        Topic(kind=u"特集(サブカテゴリ)", 
              text=u"#", 
              page=page, 
              title=u"アニメぴあ", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=False, 
              orderno=3), 
        ]

def music_promotion():
    img_path = os.path.join(os.path.dirname(__file__), "../../static/mock/img/")
    N = 6
    def make_materials(i, imgname, thumbname):
        main_image = (ImageAsset.query.filter_by(title=imgname).first() or 
                      make_image_asset(os.path.join(img_path, imgname), title=imgname))
        thumbnail = (ImageAsset.query.filter_by(title=thumbname).first() or 
                     make_image_asset(os.path.join(img_path, thumbname),title=thumbname))
        return PromotionUnit(main_image=main_image,
                             thumbnail=thumbnail, 
                             link="http://www.google.com", 
                             text=u"何かここにメッセージ書く。ファイル名:%s" % imgname, 
                             )
    punits = [make_materials(i, "%d.jpg" % i, "thumb.%d.jpg" % i) for i in range(1, N)]
    return Promotion(promotion_units=punits, 
                     name=u"音楽 promotioin枠")
    

def add_music_main_block_widgets(page, promotion):
    params =  {"kind": u"トピックス", 
               "display_count": 2, 
               "display_global": True, 
               "display_event": False, 
               "display_page": False}
    add_topic_widget(page, "main", params)

    add_promotion_widget(page, "main", {"promotion": promotion.id, 
                                        "kind": u"チケットスター:カテゴリTopプロモーション枠"})

    params = dict(kind=u"チケットスター：音楽見出し", 
                  text=u"トピックス")
    add_heading_widget(page, "main", params)

    params =  {"kind": u"トピックス", 
               "subkind": u"音楽", 
               "display_count": 5, 
               "display_global": True, 
               "display_event": False, 
               "display_page": False}
    add_topic_widget(page, "main", params)

    params = dict(kind=u"チケットスター：音楽見出し", 
                  text=u"注目のイベント")
    add_heading_widget(page, "main", params)

    params =  {"kind": u"注目のイベント", 
               "topic_type": "hasimage", 
               "display_count": 8, 
               "display_global": True, 
               "display_event": True, 
               "display_page": True}
    add_topic_widget(page, "main", params)

    params = dict(kind=u"チケットスター：トップページ見出し", 
                  text=u"今週発売のチケット")
    add_heading_widget(page, "main_left", params)

    params = {"finder_kind": "thisWeek", 
              "delimiter": u"/"}
    add_linklist_widget(page, "main_left", params)

    params = dict(kind=u"チケットスター：トップページ見出し", 
                  text=u"販売終了間近")
    add_heading_widget(page, "main_right", params)

    params = {"finder_kind": "nearTheEnd", 
              "delimiter": u"/"}
    add_linklist_widget(page, "main_right", params)


    ## sidebar
    params = dict(kind=u"チケットスター：サイドバー見出し", 
                  text=u"特集")
    add_heading_widget(page, "side", params)

    params =  {"kind": u"特集(サブカテゴリ)", 
               "display_count": 3, 
               "display_global": False, 
               "display_event": False, 
               "display_page": True}
    add_topic_widget(page, "side", params)

    

def add_music_page_settings():
    layout = music_layout()
    promotion = music_promotion()
    page = music_page(layout)
    topics = music_topics(page)

    DBSession.add(page)
    DBSession.add(promotion)
    DBSession.add_all(topics)

    DBSession.flush()
    
    add_music_main_block_widgets(page, promotion)#




###　演劇演カテゴリ

def stage_layout():
    layout = Layout(
        title = u"ticketstar.stage",
        template_filename = "ticketstar.stage.mako",
        blocks = '[["main"], ["main_left", "main_right"], ["main_bottom"], ["side"]]',
        site_id = 1, ##
        client_id = 1 ##
        )
    return layout


def stage_page(layout):
    stage_page = Page(description=u'チケットの販売、イベントの予約は楽天チケットで！楽天チケットは演劇、バレエ、ミュージカルなどの舞台、クラシック、オペラ、ロックなどのコンサート、野球、サッカー、格闘技などの演劇、その他イベントなどのチケットのオンラインショッピングサイトです。',
                       keywords= u"チケット,演劇,クラシック,オペラ,コンサート,バレエ,ミュージカル,野球,サッカー,格闘技", 
                       layout= layout, 
                       title= u'演劇',
                       url= u'stage',
                       structure= "{}", 
                       version= None)
    PageSet.get_or_create(stage_page)
    return stage_page


def stage_topics():
    return [
        Topic(kind=u"トピックス", 
              subkind=u"演劇", 
              text=u"#", 
              title=u"ポイント10倍キャンペーン実施中！『大相撲三月場所』マス席の他、希少な溜まり席も販売！", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True, 
              orderno=1), 
        Topic(kind=u"トピックス", 
              subkind=u"演劇", 
              text=u"#", 
              title=u"きゃりーぱみゅぱみゅ、倖田來未 、CNBLUE ら出演♪「オンタマカーニバル2012」1/14発売！", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True, 
              orderno=2), 

        ]



def stage_promotion():
    img_path = os.path.join(os.path.dirname(__file__), "../../static/mock/img/")
    N = 6
    def make_materials(i, imgname, thumbname):
        main_image = (ImageAsset.query.filter_by(title=imgname).first() or 
                      make_image_asset(os.path.join(img_path, imgname), title=imgname))
        thumbnail = (ImageAsset.query.filter_by(title=thumbname).first() or 
                     make_image_asset(os.path.join(img_path, thumbname),title=thumbname))
        return PromotionUnit(main_image=main_image,
                             thumbnail=thumbnail, 
                             link="http://www.google.com", 
                             text=u"何かここにメッセージ書く。ファイル名:%s" % imgname, 
                             )
    punits = [make_materials(i, "%d.jpg" % i, "thumb.%d.jpg" % i) for i in range(1, N)]
    return Promotion(promotion_units=punits, 
                     name=u"演劇 promotioin枠")
    

def add_stage_main_block_widgets(page, promotion):
    params =  {"kind": u"トピックス", 
               "display_count": 2, 
               "display_global": True, 
               "display_event": False, 
               "display_page": False}
    add_topic_widget(page, "main", params)

    add_promotion_widget(page, "main", {"promotion": promotion.id, 
                                        "kind": u"チケットスター:カテゴリTopプロモーション枠"})

    params = dict(kind=u"チケットスター：演劇見出し", 
                  text=u"トピックス")
    add_heading_widget(page, "main", params)

    params =  {"kind": u"トピックス", 
               "subkind": u"演劇", 
               "display_count": 5, 
               "display_global": True, 
               "display_event": False, 
               "display_page": False}
    add_topic_widget(page, "main", params)

    params = dict(kind=u"チケットスター：演劇見出し", 
                  text=u"注目のイベント")
    add_heading_widget(page, "main", params)

    params =  {"kind": u"注目のイベント", 
               "topic_type": "hasimage", 
               "display_count": 8, 
               "display_global": True, 
               "display_event": True, 
               "display_page": True}
    add_topic_widget(page, "main", params)

    params = dict(kind=u"チケットスター：トップページ見出し", 
                  text=u"今週発売のチケット")
    add_heading_widget(page, "main_left", params)

    params = {"finder_kind": "thisWeek", 
              "delimiter": u"/"}
    add_linklist_widget(page, "main_left", params)

    params = dict(kind=u"チケットスター：トップページ見出し", 
                  text=u"販売終了間近")
    add_heading_widget(page, "main_right", params)

    params = {"finder_kind": "nearTheEnd", 
              "delimiter": u"/"}
    add_linklist_widget(page, "main_right", params)


    ## sidebar
    params = dict(kind=u"チケットスター：サイドバー見出し", 
                  text=u"特集")
    add_heading_widget(page, "side", params)

    params =  {"kind": u"特集(サブカテゴリ)", 
               "display_count": 3, 
               "display_global": False, 
               "display_event": False, 
               "display_page": True}
    add_topic_widget(page, "side", params)


def add_stage_page_settings():
    layout = stage_layout()
    topics = stage_topics()
    promotion = stage_promotion()
    page = stage_page(layout)

    DBSession.add(page)
    DBSession.add(promotion)
    DBSession.add_all(topics)

    DBSession.flush()
    
    add_stage_main_block_widgets(page, promotion)#


#### イベント・その他

def event_layout():
    layout = Layout(
        title = u"ticketstar.event",
        template_filename = "ticketstar.event.mako",
        blocks = '[["main"], ["main_left", "main_right"], ["main_bottom"], ["side"]]',
        site_id = 1, ##
        client_id = 1 ##
        )
    return layout


def event_page(layout):
    event_page = Page.get_or_create_by_title(u'イベント・その他')
    params = dict (description=u'チケットの販売、イベントの予約は楽天チケットで！楽天チケットは演劇、バレエ、ミュージカルなどの舞台、クラシック、オペラ、ロックなどのコンサート、野球、サッカー、格闘技などのその他、その他イベントなどのチケットのオンラインショッピングサイトです。',
                   keywords= u"チケット,演劇,クラシック,オペラ,コンサート,バレエ,ミュージカル,野球,サッカー,格闘技", 
                   layout= layout, 
                   url= u'event',
                   structure= "{}", 
                   version= None)
    for k, v in params.iteritems():
        setattr(event_page, k, v)
    PageSet.get_or_create(event_page)
    return event_page


def event_topics():
    return [
        Topic(kind=u"トピックス", 
              subkind=u"その他", 
              text=u"#", 
              title=u"ポイント10倍キャンペーン実施中！『大相撲三月場所』マス席の他、希少な溜まり席も販売！", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True, 
              orderno=1), 
        Topic(kind=u"トピックス", 
              subkind=u"その他", 
              text=u"#", 
              title=u"きゃりーぱみゅぱみゅ、倖田來未 、CNBLUE ら出演♪「オンタマカーニバル2012」1/14発売！", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True, 
              orderno=2), 

        ]



def event_promotion():
    img_path = os.path.join(os.path.dirname(__file__), "../../static/mock/img/")
    N = 6
    def make_materials(i, imgname, thumbname):
        main_image = (ImageAsset.query.filter_by(title=imgname).first() or 
                      make_image_asset(os.path.join(img_path, imgname), title=imgname))
        thumbnail = (ImageAsset.query.filter_by(title=thumbname).first() or 
                     make_image_asset(os.path.join(img_path, thumbname),title=thumbname))
        return PromotionUnit(main_image=main_image,
                             thumbnail=thumbnail, 
                             link="http://www.google.com", 
                             text=u"何かここにメッセージ書く。ファイル名:%s" % imgname, 
                             )
    punits = [make_materials(i, "%d.jpg" % i, "thumb.%d.jpg" % i) for i in range(1, N)]
    return Promotion(promotion_units=punits, 
                     name=u"その他 promotioin枠")
    

def add_event_main_block_widgets(page, promotion):
    params =  {"kind": u"トピックス", 
               "display_count": 2, 
               "display_global": True, 
               "display_event": False, 
               "display_page": False}
    add_topic_widget(page, "main", params)

    add_promotion_widget(page, "main", {"promotion": promotion.id, 
                                        "kind": u"チケットスター:カテゴリTopプロモーション枠"})

    params = dict(kind=u"チケットスター：その他見出し", 
                  text=u"トピックス")
    add_heading_widget(page, "main", params)

    params =  {"kind": u"トピックス", 
               "subkind": u"その他", 
               "display_count": 5, 
               "display_global": True, 
               "display_event": False, 
               "display_page": False}
    add_topic_widget(page, "main", params)

    params = dict(kind=u"チケットスター：その他見出し", 
                  text=u"注目のイベント")
    add_heading_widget(page, "main", params)

    params =  {"kind": u"注目のイベント", 
               "topic_type": "hasimage", 
               "display_count": 8, 
               "display_global": True, 
               "display_event": True, 
               "display_page": True}
    add_topic_widget(page, "main", params)

    params = dict(kind=u"チケットスター：トップページ見出し", 
                  text=u"今週発売のチケット")
    add_heading_widget(page, "main_left", params)

    params = {"finder_kind": "thisWeek", 
              "delimiter": u"/"}
    add_linklist_widget(page, "main_left", params)

    params = dict(kind=u"チケットスター：トップページ見出し", 
                  text=u"販売終了間近")
    add_heading_widget(page, "main_right", params)

    params = {"finder_kind": "nearTheEnd", 
              "delimiter": u"/"}
    add_linklist_widget(page, "main_right", params)

    ## sidebar
    params = dict(kind=u"チケットスター：サイドバー見出し", 
                  text=u"特集")
    add_heading_widget(page, "side", params)

    params =  {"kind": u"特集(サブカテゴリ)", 
               "display_count": 3, 
               "display_global": False, 
               "display_event": False, 
               "display_page": True}
    add_topic_widget(page, "side", params)


def add_event_page_settings():
    layout = event_layout()
    topics = event_topics()
    promotion = event_promotion()
    page = event_page(layout)

    DBSession.add(page)
    DBSession.add(promotion)
    DBSession.add_all(topics)

    DBSession.flush()
    
    add_event_main_block_widgets(page, promotion)#



### トップページ


def top_layout():
    layout = Layout(
        title = u"ticketstar.top",
        template_filename = "ticketstar.top.mako",
        blocks = '[["main"], ["main_left", "main_right"], ["main_bottom"], ["side_top"], ["side_bottom"]]',
        site_id = 1, ##
        client_id = 1 ##
        )
    return layout


def top_page(layout):
    top_page = Page.get_or_create_by_title(u'トップページ')
    params = dict(description=u'チケットの販売、イベントの予約は楽天チケットで！楽天チケットは演劇、バレエ、ミュージカルなどの舞台、クラシック、オペラ、ロックなどのコンサート、野球、サッカー、格闘技などのスポーツ、その他イベントなどのチケットのオンラインショッピングサイトです。',
                  keywords= u"チケット,演劇,クラシック,オペラ,コンサート,バレエ,ミュージカル,野球,サッカー,格闘技", 
                  layout= layout, 
                  url= u'top',
                  structure= "{}", 
                  version= None)
    for k, v in params.iteritems():
        setattr(top_page, k, v)
    PageSet.get_or_create(top_page)
    return top_page


def top_promotion(layout):
    img_path = os.path.join(os.path.dirname(__file__), "../../static/mock/img/")
    def make_materials(i, imgname, thumbname):
        main_image = (ImageAsset.query.filter_by(title=imgname).first() or
                      make_image_asset(os.path.join(img_path, imgname), title=imgname))
        thumbnail = (ImageAsset.query.filter_by(title=thumbname).first() or 
                     make_image_asset(os.path.join(img_path, thumbname),title=thumbname))
        
        page = Page(description=u'for promotion',
                    keywords= u"promotion", 
                    layout= layout, 
                    title= u"%s for promotion" % imgname,
                    url= imgname,
                    structure= "{}", 
                    version= None)
        pageset = PageSet.get_or_create(page)

        
        return PromotionUnit(main_image=main_image, thumbnail=thumbnail, 
                  text=u"何かここにメッセージ書く。ファイル名:%s" % imgname, 
                  pageset=pageset)
    punits = [make_materials(i, "%d.jpg" % i, "thumb.%d.jpg" % i) for i in range(1, 16)]
    return Promotion(promotion_units=punits, 
                     name=u"トップページ promotioin枠")


def top_topics(page):
    return [
        Topic(kind=u"トピックス", 
              subkind=u"Top", 
              text=u"#", 
              title=u"ポイント10倍キャンペーン実施中！『大相撲三月場所』マス席の他、希少な溜まり席も販売！", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True, 
              orderno=1), 
        Topic(kind=u"トピックス", 
              subkind=u"Top", 
              text=u"#", 
              title=u"きゃりーぱみゅぱみゅ、倖田來未 、CNBLUE ら出演♪「オンタマカーニバル2012」1/14発売！", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True, 
              orderno=2), 
        Topic(kind=u"トピックス", 
              subkind=u"Top", 
              text=u"#", 
              title=u"47年ぶりに日本上陸のツタンカーメン展！1/31購入分まで、もれなくポイント10倍！", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True, 
              orderno=3), 
        Topic(kind=u"トピックス", 
              subkind=u"Top", 
              text=u"#", 
              title=u"東京、大阪で過去最高の動員を記録したKOOZAが福岡へ上陸！楽チケならポイント10倍！", 
              publish_open_on=datetime.datetime(2011, 1, 1),
              publish_close_on=datetime.datetime(2013, 1, 1), 
              is_global=True, 
              orderno=4), 
        ]


def top_topcontents(page):
    link_page = Page.query.filter(Page.event!=None).first() ##
    img_path = os.path.join(os.path.dirname(__file__), "./data/dummy.jpg")
    image_asset = make_image_asset(img_path, title="dummy")
    return [
        Topcontent(kind=u"注目のイベント", 
                   publish_open_on=datetime.datetime(2011, 1, 1),
                   publish_close_on=datetime.datetime(2013, 1, 1), 
                   page=link_page, #本当はpageset
                   is_global=True, 
                   title=link_page.title, 
                   text=u"ここになにか説明を加える。これはデフォルトの文章を表示するようにしても良いかもしれない。", 
                   orderno=50, 
                   image_asset = image_asset,  ##
                   countdown_type = "deal_close"
                   ), 
        Topcontent(kind=u"注目のイベント", 
                   publish_open_on=datetime.datetime(2011, 1, 1),
                   publish_close_on=datetime.datetime(2013, 1, 1), 
                   page=link_page, #本当はpageset
                   is_global=True, 
                   title=link_page.title, 
                   text=u"ここになにか説明を加える。これはデフォルトの文章を表示するようにしても良いかもしれない。", 
                   orderno=50, 
                   image_asset = image_asset,  ##
                   countdown_type = "deal_close"
                   ), 
        Topcontent(kind=u"注目のイベント", 
                   publish_open_on=datetime.datetime(2011, 1, 1),
                   publish_close_on=datetime.datetime(2013, 1, 1), 
                   page=link_page, #本当はpageset
                   is_global=True, 
                   title=link_page.title, 
                   text=u"ここになにか説明を加える。これはデフォルトの文章を表示するようにしても良いかもしれない。", 
                   orderno=50, 
                   image_asset = image_asset,  ##
                   countdown_type = "deal_close"
                   ), 
        Topcontent(kind=u"注目のイベント", 
                   publish_open_on=datetime.datetime(2011, 1, 1),
                   publish_close_on=datetime.datetime(2013, 1, 1), 
                   page=link_page, #本当はpageset
                   is_global=True, 
                   title=link_page.title, 
                   text=u"ここになにか説明を加える。これはデフォルトの文章を表示するようにしても良いかもしれない。", 
                   orderno=50, 
                   image_asset = image_asset,  ##
                   countdown_type = "deal_close"
                   ), 
        Topcontent(kind=u"注目のイベント", 
                   publish_open_on=datetime.datetime(2011, 1, 1),
                   publish_close_on=datetime.datetime(2013, 1, 1), 
                   page=link_page, #本当はpageset
                   is_global=True, 
                   title=link_page.title, 
                   text=u"ここになにか説明を加える。これはデフォルトの文章を表示するようにしても良いかもしれない。", 
                   orderno=50, 
                   image_asset = image_asset,  ##
                   countdown_type = "deal_close"
                   ), 
        Topcontent(kind=u"注目のイベント", 
                   publish_open_on=datetime.datetime(2011, 1, 1),
                   publish_close_on=datetime.datetime(2013, 1, 1), 
                   page=link_page, #本当はpageset
                   is_global=True, 
                   title=link_page.title, 
                   text=u"ここになにか説明を加える。これはデフォルトの文章を表示するようにしても良いかもしれない。", 
                   orderno=50, 
                   image_asset = image_asset,  ##
                   countdown_type = "deal_close"
                   )
        ]


def add_top_main_block_widgets(page, promotion):
    add_promotion_widget(page, "main", {"promotion": promotion.id, 
                                        "kind": u"チケットスター:Topプロモーション枠"})

    params = dict(kind=u"チケットスター：トップページ見出し", 
                  text=u"トピックス")
    add_heading_widget(page, "main", params)

    params =  {"kind": u"トピックス", 
               "subkind": u"Top", 
               "display_count": 5, 
               "display_global": True, 
               "display_event": True, 
               "display_page": True}
    add_topic_widget(page, "main", params)

    params = dict(kind=u"チケットスター：トップページ見出し", 
                  text=u"注目のイベント")
    add_heading_widget(page, "main", params)

    params =  {"kind": u"注目のイベント", 
               "topic_type": "hasimage", 
               "display_count": 6, 
               "display_global": True, 
               "display_event": True, 
               "display_page": True}
    add_topic_widget(page, "main", params)

    params = dict(kind=u"チケットスター：トップページ見出し", 
                  text=u"今週発売のチケット")
    add_heading_widget(page, "main_left", params)

    params = {"finder_kind": "thisWeek", 
              "delimiter": u"/"}
    add_linklist_widget(page, "main_left", params)

    params = dict(kind=u"チケットスター：トップページ見出し", 
                  text=u"販売終了間近")
    add_heading_widget(page, "main_right", params)

    params = {"finder_kind": "nearTheEnd", 
              "delimiter": u"/"}
    add_linklist_widget(page, "main_right", params)


def top_event_and_page_for_linklist_widget(layout):
    today = datetime.datetime.today()
    def create_material(title, offset):
        delta = datetime.timedelta(days=offset)
        event = Event(title= title, 
                      event_open=delta+today, 
                      event_close=datetime.timedelta(100)+today, 
                      deal_open=delta+today, 
                      deal_close=datetime.timedelta(100)+today)
        page = Page(layout=layout, ##
                    url=title,  ##
                    title=title, 
                    event=event)
        PageSet.get_or_create(page)
        return page
    return [create_material(u"明日つくられるイベント", 1), 
            create_material(u"今日作られたイベント", 0), 
            create_material(u"昨日つくられたイベント", -1), 
            create_material(u"一昨日つくられたイベント", -2)
            ]


def add_top_page_settings():
    layout = top_layout()
    materials = top_event_and_page_for_linklist_widget(layout)
    page = top_page(layout)
    topics = top_topics(page)
    topcontents = top_topcontents(page)
    promotion = top_promotion(layout)
    DBSession.add(page)
    DBSession.add_all(materials)
    DBSession.add_all(topics)
    DBSession.add_all(topcontents)
    DBSession.add(promotion)
 
    DBSession.flush()
    add_top_main_block_widgets(page, promotion)


def add_materials_settings():
    """ siteなど
    """
    client = Client.query.filter_by(name=u"master").first()
    if client is None:
        client = Client(
            id = 1,
            name = u"master",
            prefecture = u"tokyo",
            address = u"000",
            email = "foo@example.jp",
            contract_status = 0
            )
        DBSession.add(client)
    site = Site.query.filter_by(name=u"ticketstar").first()
    if site is None:
        site = Site(name=u"ticketstar",
                    description=u"ticketstar ticketstar",
                    url="http://example.com",
                    client=client)
        DBSession.add(site)

    from altaircms.usersetting.models import User
    user = User(is_administrator=1)
    debug_user = Operator(auth_source="debug", user=user, role_id=1, screen_name="debug user")

    ## simple layout
    layout_col2 = Layout(
        title = "col2", 
        template_filename = "col2.mako", 
        blocks = '[["header"],["left", "right"],["footer"]]', 
        site = site,  ##
        client = client,  ##
        )
    
    layout_col3 = Layout(
        title = "col3",
        template_filename = "col3.mako",
        blocks = '[["header"],["left1", "right1"],["left2", "center", "right2"], ["footer"]]',
        site = site,  ##
        client = client,  ##,
        )

    DBSession.add(debug_user)
    DBSession.add(layout_col2)
    DBSession.add(layout_col3)


def bind_category_to_pageset():
    Category.query.filter_by(label=u"チケットトップ").update({"pageset_id": PageSet.query.filter_by(name=u"トップページ ページセット").one().id}, synchronize_session="fetch")
    Category.query.filter_by(label=u"音楽").update({"pageset_id": PageSet.query.filter_by(name=u"音楽 ページセット").first().id}, synchronize_session="fetch")
    Category.query.filter_by(label=u"スポーツ").update({"pageset_id": PageSet.query.filter_by(name=u"スポーツ ページセット").one().id}, synchronize_session="fetch")
    Category.query.filter_by(label=u"演劇").update({"pageset_id": PageSet.query.filter_by(name=u"演劇 ページセット").one().id}, synchronize_session="fetch")
    Category.query.filter_by(label=u"イベント・その他").update({"pageset_id": PageSet.query.filter_by(name=u"イベント・その他 ページセット").one().id}, synchronize_session="fetch")

    Category.query.filter_by(label=u"ヘルプ").update({"pageset_id": PageSet.query.filter_by(name=u"ヘルプ ページセット").one().id}, synchronize_session="fetch")
    Category.query.filter_by(label=u"初めての方へ").update({"pageset_id": PageSet.query.filter_by(name=u"初めての方へ ページセット").one().id}, synchronize_session="fetch")
    Category.query.filter_by(label=u"公演中止・変更情報").update({"pageset_id": PageSet.query.filter_by(name=u"公演の中止・変更情報 ページセット").one().id}, synchronize_session="fetch")

    
def main(env, args):
    # setup()
    add_materials_settings()
    transaction.commit()

    add_sports_page_settings()
    add_music_page_settings()
    add_stage_page_settings()
    add_help_page_settings()
    add_first_page_settings()
    add_event_page_settings()
    add_detail_page_settings()
    add_change_page_settings()
    add_top_page_settings()

    transaction.commit()

    ##
    bind_category_to_pageset()
    transaction.commit()

