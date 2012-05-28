# -*- coding:utf-8 -*-

import sqlalchemy as sa
import sqlalchemy.orm as orm
from datetime import datetime

from altaircms.models import Base, BaseOriginalMixin
from altaircms.models import DBSession
from altaircms.page.models import PageSet
from altaircms.asset.models import ImageAsset
from altaircms.event.models import Event

import altaircms.helpers as h

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

class AboutPublishMixin(object):
    """ 表示順序を定義可能なmodelが持つ
    """
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
    linked_page = orm.relationship(PageSet, primaryjoin="Topic.linked_page_id==PageSet.id")

    ## topicが表示されるページ
    bound_page_id = sa.Column(sa.Integer, sa.ForeignKey("pagesets.id"), nullable=True)
    bound_page = orm.relationship(PageSet, primaryjoin="Topic.bound_page_id==PageSet.id")
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
            return "page:%d" % self.bound_page.id
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

class Topcontent(AboutPublishMixin,
                 BaseOriginalMixin,
                 Base):
    """
    Topページの画像つきtopicのようなもの
    """
    __tablename__ = "topcontent"
    query = DBSession.query_property()
    COUNTDOWN_CANDIDATES = h.base.COUNTDOWN_KIND_MAPPING.items()
    KIND_CANDIDATES = [u"注目のイベント"]

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

    client_id = sa.Column(sa.Integer, sa.ForeignKey("client.id")) #?
    site_id = sa.Column(sa.Integer, sa.ForeignKey("site.id"))   
    kind = sa.Column(sa.Unicode(255))
    subkind = sa.Column(sa.Unicode(255))
    title = sa.Column(sa.Unicode(255))
    text = sa.Column(sa.Unicode(255))

    ## topcontent をlinkとして利用したときの飛び先
    linked_page_id = sa.Column(sa.Integer, sa.ForeignKey("pagesets.id"), nullable=True)
    linked_page = orm.relationship(PageSet, primaryjoin="Topcontent.linked_page_id==PageSet.id")

    ## topcontentが表示されるページ
    bound_page_id = sa.Column(sa.Integer, sa.ForeignKey("pagesets.id"), nullable=True)
    bound_page = orm.relationship(PageSet, primaryjoin="Topcontent.bound_page_id==PageSet.id")

    ## extend
    image_asset_id = sa.Column(sa.Integer, sa.ForeignKey("image_asset.id"), nullable=True)
    image_asset = orm.relationship(ImageAsset, backref="topcontent")
    countdown_type = sa.Column(sa.String(255)) #todo: fixme
    is_global = sa.Column(sa.Boolean, default=True)

    def __repr__(self):
        return "topcontent: %s title=%s" % (self.kind, self.title)

    @property
    def countdown_type_ja(self):
        return h.base.countdown_kind_ja(self.countdown_type)

    @property
    def countdown_limit(self):
        return getattr(self.page.event, self.countdown_type)

    @classmethod
    def matched_qs(cls, d=None, page=None, qs=None, kind=None, subkind=None):
        """ 下にある内容の通りのtopcontentsを返す
        """
        qs = cls.publishing(d=d, qs=qs)
        qs = cls.matched_topcontent_type(qs=qs, page=page)
        if kind:
            qs = qs.filter_by(kind=kind)
        if subkind:
            qs =  qs.filter_by(subkind=subkind)
        return qs

    @property
    def topcontent_type(self):
        """ topcontentがどんな種類で関連付けられているか調べる
        pageよりeventが優先 => eventが存在＝event詳細ページのどれか
        """
        if self.is_global:
            return "global"
        elif self.page:
            return "page:%d" % self.page_id
        else:
            return None

    @classmethod
    def matched_topcontent_type(cls, page=None, event=None, qs=None):
        if qs is None:
            qs = cls.query

        where = _where
        if page:
            where = (Topcontent.page==page) if where  == _where else where & (Topcontent.page==page)
        if event:
            where = (Topcontent.event==event) if where   == _where else where & (Topcontent.event==event)

        if where  == _where: 
            return qs.filter(cls.is_global==True)
        else:
            return qs.filter(where | (cls.is_global==True))

