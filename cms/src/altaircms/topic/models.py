# -*- coding:utf-8 -*-

import sqlalchemy as sa
from datetime import datetime
from altaircms.models import Base
from altaircms.models import DBSession

class Topic(Base):    
    """
    トピック
    """
    __tablename__ = "topic"
    query = DBSession.query_property()
    TYPE_CANDIDATES = [u"公演中止情報", u"お知らせ", u"その他"]
    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, default=datetime.now())
    updated_at = sa.Column(sa.DateTime, default=datetime.now())

    client_id = sa.Column(sa.Integer, sa.ForeignKey("client.id")) #?
    site_id = sa.Column(sa.Integer, sa.ForeignKey("site.id"))    #?

    kind = sa.Column(sa.Unicode(255))
    title = sa.Column(sa.Unicode)
    text = sa.Column(sa.Unicode)
    is_public = sa.Column(sa.Integer, default=0) #?
    publish_at = sa.Column(sa.DateTime)

    def __repr__(self):
        return u"トピック: %s タイトル=%s (%s)" % (self.kind, self.title, self.publish_at)
