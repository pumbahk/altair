# -*- coding:utf-8 -*-

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime

from altaircms.models import Base
from altaircms.models import DBSession
from altaircms.page.models import Page
from altaircms.asset.models import ImageAsset
from altaircms.lib.modelmixin import AboutPublishMixin


#ugly
class Topcontent(AboutPublishMixin,
                 Base):
    """
    Topページの画像つきtopicのようなもの
    """
    __tablename__ = "topcontent"
    query = DBSession.query_property()
    COUNTDOWN_CANDIDATES = [("page_open",u"公演開始まで"),("page_close",u"公演終了まで"),
                            ( "deal_open",u"販売開始まで"),( "deal_close",u"販売終了まで")]
    KIND_CANDIDATES = [u"注目のページ"]

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

    client_id = sa.Column(sa.Integer, sa.ForeignKey("client.id")) #?
    site_id = sa.Column(sa.Integer, sa.ForeignKey("site.id"))   
    kind = sa.Column(sa.Unicode(255))
    title = sa.Column(sa.Unicode)
    text = sa.Column(sa.Unicode)

    ## extend
    image_asset_id = sa.Column(sa.Integer, sa.ForeignKey("image_asset.id"), nullable=True)
    image_asset = orm.relationship(ImageAsset, backref="topcontent")
    page_id = sa.Column(sa.Integer, sa.ForeignKey("page.id"))
    page = orm.relationship(Page)
    countdown_type = sa.Column(sa.String(255))
    is_global = sa.Column(sa.Boolean, default=True)

    def __repr__(self):
        return "topcontent: %s title=%s" % (self.kind, self.title)

    @property
    def countdown_type_ja(self):
        return self.COUNTDOWN_CANDIDATES[self.countdown_type]

    @classmethod
    def has_global(cls):
        return cls.is_global==True

    @classmethod
    def matched_qs(cls, d=None, page=None, qs=None, kind=None):
        """ 下にある内容の通りのtopicsを返す
        """
        qs = cls.publishing(d=d, qs=qs)
        qs = cls.matched_topic_type(qs=qs, page=page)
        return qs.filter(cls.kind==kind) if kind else qs

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
    def matched_topic_type(cls, page=None, event=None, category=None, qs=None):
        if qs is None:
            qs = cls.query
        where = (cls.has_global())
        if page:
            where = where | (Topcontent.page==page)
        return qs.filter(where)
