# -*- coding:utf-8 -*-

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime

from altaircms.models import Base
from altaircms.models import DBSession
from altaircms.page.models import Page
from altaircms.models import Event

class AboutPublishMixin(object):
    publish_open_on = sa.Column(sa.DateTime)
    publish_close_on = sa.Column(sa.DateTime)
    orderno = sa.Column(sa.Integer, default=50)
    is_vetoed = sa.Column(sa.Boolean, default=False)
    
    @classmethod
    def publishing(cls, d=None, qs=None):
        if d is None:
            d = datetime.now()
        if qs is None:
            qs = cls.query
        return cls._has_permissions(cls._orderby_logic(cls._publishing(qs, d)))

    @classmethod
    def _has_permissions(cls, qs):
        """ 公開可能なもののみ
        """
        return qs.filter(cls.is_vetoed==False)

    @classmethod
    def _publishing(cls, qs, d):
        """ 掲載期間のもののみ
        """
        qs = qs.filter(cls.publish_open_on  <= d)
        return qs.filter(d <= cls.publish_close_on)

    @classmethod
    def _orderby_logic(cls, qs):
        """ 表示順序で並べた後、公開期間で降順
        """
        table = cls.__tablename__
        return qs.order_by(sa.asc(table+".orderno"),
                           sa.desc(table+".publish_open_on"), 
                           )


class AboutTopicTypeMixin(object):
    is_global = sa.Column(sa.Boolean, default=False)
    # category = sa.Column(sa.String(255), nullable=True)

    @classmethod
    def matched_topic_type(cls, page=None, event=None, category=None, qs=None):
        if qs is None:
            qs = cls.query
        where = (cls.has_global())
        if page:
            where = where | (cls.same_page(page))
        if event:
            where = where | (cls.same_event(event))
        # if category:
        #     where = where | (cls.has_category(category))
        return qs.filter(where)
        
    @declared_attr
    def event_id(cls):
        return sa.Column(sa.Integer, sa.ForeignKey("event.id"), nullable=True)
    @declared_attr
    def page_id(cls):
        return sa.Column(sa.Integer, sa.ForeignKey("page.id"), nullable=True)
    @declared_attr
    def event(cls):
        return orm.relationship(Event, backref="topic", uselist=False)
    @declared_attr
    def page(cls):
        return orm.relationship(Page, backref="topic", uselist=False)

    # @classmethod
    # def has_category(cls, category):
    #     return cls.category == category

    @classmethod
    def has_global(cls):
        return cls.is_global==True

    @classmethod
    def same_page(cls, page):
        return cls.page==page

    @classmethod
    def same_event(cls, event):
        return cls.event==event

    @property
    def topic_type(self):
        """ topicがどんな種類で関連付けられているか調べる
        eventよりpageが優先 => eventが存在＝event詳細ページのどれか
        """
        if self.is_global:
            return "global"
        elif self.event:
            return "event:%d" % self.event.id
        elif self.page:
            return "page:%d" % self.page_id
        # else:
        #     return self.category

class Topic(AboutPublishMixin, AboutTopicTypeMixin, 
            Base):    
    """
    トピック
    """
    __tablename__ = "topic"
    query = DBSession.query_property()
    TYPE_CANDIDATES = [u"公演中止情報", u"お知らせ", u"その他"]

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

    client_id = sa.Column(sa.Integer, sa.ForeignKey("client.id")) #?
    site_id = sa.Column(sa.Integer, sa.ForeignKey("site.id"))   

    kind = sa.Column(sa.Unicode(255))
    title = sa.Column(sa.Unicode)
    text = sa.Column(sa.Unicode)
    
    def __repr__(self):
        return "topic: %s title=%s" % (self.kind, self.title)

    @classmethod
    def matched_qs(cls, d=None, page=None, event=None, qs=None, kind=None):
        """ 下にある内容の通りのtopicsを返す
        """
        qs = cls.publishing(d=d, qs=qs)
        qs = cls.matched_topic_type(qs=qs, page=page, event=event)
        return qs.filter(cls.kind==kind) if kind else qs


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


topic widget(移動予定):

1. 画像を挿入（アセットから選択)
2. この時、tagでアセットから絞りこまれた内容の画像から選択できるようにする。
"""
        

