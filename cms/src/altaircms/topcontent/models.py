# -*- coding:utf-8 -*-

import sqlalchemy as sa
import sqlalchemy.orm as orm
from datetime import datetime

import altaircms.helpers as h
from altaircms.models import Base, BaseOriginalMixin
from altaircms.models import DBSession
from altaircms.page.models import Page
from altaircms.asset.models import ImageAsset
from altaircms.lib.modelmixin import AboutPublishMixin


#ugly
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

    ## extend
    image_asset_id = sa.Column(sa.Integer, sa.ForeignKey("image_asset.id"), nullable=True)
    image_asset = orm.relationship(ImageAsset, backref="topcontent")
    page_id = sa.Column(sa.Integer, sa.ForeignKey("page.id"))
    page = orm.relationship(Page)
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
        """ 下にある内容の通りのtopicsを返す
        """
        qs = cls.publishing(d=d, qs=qs)
        qs = cls.matched_topic_type(qs=qs, page=page)
        if kind:
            qs = qs.filter_by(kind=kind)
        if subkind:
            qs =  qs.filter_by(subkind=subkind)
        return qs

    @property
    def topic_type(self):
        """ topicがどんな種類で関連付けられているか調べる
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

