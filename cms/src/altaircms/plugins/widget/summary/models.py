# -*- coding:utf-8 -*-

"""
problem: attrを設定できない。
"""
from zope.interface import implements
import json

import sqlalchemy as sa
import sqlalchemy.orm as orm
from pyramid.renderers import render

###
import codecs
import sys
sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
###

from altaircms.interfaces import IWidget
from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.page.models import Page
from altaircms.security import RootFactory

"""
公演期間
    2012年06月03日(日) 〜 07月16日(月) (講演カレンダーを見る) 
説明／注意事項
    ※未就学児童のご入場はお断りいたします。
料金
    席種	料金
    全席指定 	￥6,300
お問い合わせ先
    【お問合せ】
    サウンドクリエーター　06-6357-4400 / www.sound-c.co.jp
    ≪浪切公演≫浪切ホールチケットカウンター　072-439-4915 / www.namikiri.jp
    ≪神戸公演≫神戸国際会館　078-231-8162 / www.kih.co.jp 
販売期間
    2012年03月03日(土) 〜 07月12日(木) 
"""

##
## ここではattributeを返しているけれど、これをりようできるようになっていない
"""
todo:
   classを指定する方法
   登録した文字列を編集する方法
   改行への対応
"""

def _items_from_page(page):
    import altaircms.helpers as h
    event = page.event
    return [ # todo: fixme
        dict(label=u"講演期間", attr='class=performance_period', content=h.base.term(event.event_open, event.event_close)), 
        dict(label=u"説明／注意事項", attr='class=notice', content=u"※未就学児童のご入場はお断りいたします。"), 
        dict(label=u"お問い合わせ先", attr='class=contact', content=event.inquiry_for.replace("\n", " ")),  ##newline not supported
        dict(label=u"販売期間", attr="class=sales_period", content=h.base.term(event.deal_open,event.deal_close))
        ]

class SummaryWidget(Widget):
    implements(IWidget)
    type = "summary"

    template_name = "altaircms.plugins.widget:summary/render.mako"
    __tablename__ = "widget_summary"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    items = sa.Column(sa.UnicodeText) #json string
    """
    items attribute structure::

       [{label: "講演期間", content: u"2012年06月03日(日) 〜 07月16日(月) (講演カレンダーを見る)", attr="class='performance_period'"}, 
        {label: "説明／注意事項", content: u"※未就学児童のご入場はお断りいたします。", attr="class='notice'"}]
    """

    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("request")
        items = json.loads(self.items or "[]")

        content = render(self.template_name, {"widget": self,  "items": items}) 
        bsettings.add(bname, content)

    @classmethod
    def from_page(cls, page):
        event = page.event
        if event is None:
            return cls(page_id=page.id)
        else:
            return cls(page_id=page.id, items=json.dumps(_items_from_page(page), ensure_ascii=False))

class SummaryWidgetResource(HandleSessionMixin,
                            UpdateDataMixin,
                            HandleWidgetMixin,
                            RootFactory
                          ):
    WidgetClass = SummaryWidget

    def get_widget(self, widget_id):
        return self._get_or_create(SummaryWidget, widget_id)

    def _items_from_page(self, page):
        return json.dumps(_items_from_page(page), ensure_ascii=False)

    def get_items(self, page_id):
        page = Page.query.filter(Page.id==page_id).one()
        return self._items_from_page(page) if page.event else "[]"


