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

class Topcontent(AboutPublishMixin,Base):    
    """
    Topページの画像つきtopicのようなもの
    """
    __tablename__ = "topcontent"
    query = DBSession.query_property()

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
    event_id = sa.Column(sa.Integer, sa.ForeignKey("event.id"))
    event = orm.relationship(Event)

    def __repr__(self):
        return "topcontent: %s title=%s" % (self.kind, self.title)

    @classmethod
    def matched_qs(cls, d=None, page=None, event=None, qs=None, kind=None):
        """ 下にある内容の通りのtopcontentsを返す
        """
        qs = cls.publishing(d=d, qs=qs)
        qs = cls.matched_topcontent_type(qs=qs, page=page, event=event)
        return qs.filter(cls.kind==kind) if kind else qs

