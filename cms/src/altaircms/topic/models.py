# -*- coding:utf-8 -*-

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime

from altaircms.models import Base, BaseOriginalMixin
from altaircms.models import DBSession
from altaircms.page.models import PageSet
from altaircms.event.models import Event
from altaircms.lib.modelmixin import AboutPublishMixin


"""
topicはtopicウィジェットで使われる。
以下のような内容の表示に使われる。

2011:2/11 講演者変更:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
2011:2/18 講演者変更:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
2011:2/19 講演者変更:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
2011:2/20 講演者中止:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx


要件として

1. 公開可否を指定できること
2. 最新N件を取得できること
3. (2.より優先して)表示順序を指定できること
    表示順序の範囲は　1 〜 100
    デフォルトでは50
4. 自動的に、ページ、イベントに紐ついたページ, 同カテゴリのものが表示される。

ができる必要がある。


"""

## 
_where = object()

class Topic(AboutPublishMixin, 
            BaseOriginalMixin,
            Base):
    """
    トピック
    """
    query = DBSession.query_property()

    __tablename__ = "topic"
    KIND_CANDIDATES = [u"公演中止情報", u"トピックス", u"その他", u"ヘルプ", u"特集", u"特集(サブカテゴリ)"]

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

    client_id = sa.Column(sa.Integer, sa.ForeignKey("client.id")) #?
    site_id = sa.Column(sa.Integer, sa.ForeignKey("site.id"))   
    kind = sa.Column(sa.Unicode(255))
    subkind = sa.Column(sa.Unicode(255))
    title = sa.Column(sa.Unicode(255))
    text = sa.Column(sa.UnicodeText)
    event_id = sa.Column(sa.Integer, sa.ForeignKey("event.id"), nullable=True)
    event = orm.relationship(Event, backref="topic")
    
    ## topic をlinkとして利用したときの飛び先
    linked_page_id = sa.Column(sa.Integer, sa.ForeignKey("pagesets.id"), nullable=True)
    linked_page = orm.relationship(PageSet, backref="linked_topics", primaryjoin="Topic.linked_page_id==PageSet.id")

    ## topicが表示されるページ
    bound_page_id = sa.Column(sa.Integer, sa.ForeignKey("pagesets.id"), nullable=True)
    bound_page = orm.relationship(PageSet, backref="bound_topics", primaryjoin="Topic.bound_page_id==PageSet.id")
    is_global = sa.Column(sa.Boolean, default=False)

    def __repr__(self):
        return "topic: %s title=%s" % (self.kind, self.title)

    @property
    def topic_type(self):
        """ topicがどんな種類で関連付けられているか調べる
        pageよりeventが優先 => eventが存在＝event詳細ページのどれか
        """
        if self.is_global:
            return "global"
        elif self.event:
            return "event:%d" % self.event.id
        elif self.bound_page:
            return "page:%d" % self.bound_page_id
        else:
            return None

    @classmethod
    def matched_topic_type(cls, page=None, event=None, qs=None):
        if qs is None:
            qs = cls.query

        where = _where
        if page:
            where = (Topic.bound_page==page) if where  == _where else where & (Topic.bound_page==page)
        if event:
            where = (Topic.event==event) if where   == _where else where & (Topic.event==event)

        if where  == _where: 
            return qs.filter(cls.is_global==True)
        else:
            return qs.filter(where | (cls.is_global==True))

    @classmethod
    def matched_qs(cls, d=None, page=None, event=None, qs=None, kind=None, subkind=None):
        """ 下にある内容の通りのtopicsを返す
        """
        qs = cls.publishing(d=d, qs=qs)
        qs = cls.matched_topic_type(qs=qs, page=page, event=event)

        if kind:
            qs = qs.filter_by(kind=kind)
        if subkind:
            qs = qs.filter_by(subkind=subkind)
        return qs

