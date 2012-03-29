# -*- coding:utf-8 -*-

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime

from altaircms.models import Base
from altaircms.models import DBSession
from altaircms.event.models import Event
from altaircms.asset.models import ImageAsset
from altaircms.lib.modelmixin import AboutPublishMixin

from altaircms.topic.models import OrderableItem
class Topcontent(AboutPublishMixin, OrderableItem):    
    """
    Topページの画像つきtopicのようなもの
    """
    __tablename__ = "topcontent"
    type = "topcontent"
    query = DBSession.query_property()
    __mapper_args__ = {"polymorphic_identity": type}
    COUNTDOWN_CANDIDATES = [("event_open",u"公演開始まで"),("event_close",u"公演終了まで"),
                            ( "deal_open",u"販売開始まで"),( "deal_close",u"販売終了まで")]
    KIND_CANDIDATES = [u"注目のイベント"]

    id = sa.Column(sa.Integer, sa.ForeignKey("orderableitem.id"), primary_key=True)
    kind = sa.Column(sa.Unicode(255))
    title = sa.Column(sa.Unicode)
    text = sa.Column(sa.Unicode)

    ## extend
    image_asset_id = sa.Column(sa.Integer, sa.ForeignKey("image_asset.id"), nullable=True)
    image_asset = orm.relationship(ImageAsset, backref="topcontent")
    event_id = sa.Column(sa.Integer, sa.ForeignKey("event.id"))
    event = orm.relationship(Event)
    countdown_type = sa.Column(sa.String(255))

    def __repr__(self):
        return "topcontent: %s title=%s" % (self.kind, self.title)

    @property
    def countdown_type_ja(self):
        return self.COUNTDOWN_CANDIDATES[self.countdown_type]
    @classmethod
    def matched_qs(cls, d=None, event=None, qs=None, kind=None):
        """ 下にある内容の通りのtopcontentsを返す
        """
        qs = cls.publishing(d=d, qs=qs)
        qs = qs.filter(cls.event==event) if event else qs
        return qs.filter(cls.kind==kind) if kind else qs

