# coding: utf-8
from datetime import datetime
from formalchemy import Column

import transaction

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Unicode, String
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base, declared_attr

from sqlalchemy.orm import scoped_session, relationship
from sqlalchemy.orm import sessionmaker

from zope.sqlalchemy import ZopeTransactionExtension
from altaircms.models import Base
from altaircms.tag.models import Tag
from altaircms.models import DBSession
from altaircms.layout.models import Layout

class Page(Base):
    """
    ページ
    """
    query = DBSession.query_property()
    __tablename__ = "page"

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('page.id'))
    event_id = Column(Integer, ForeignKey('event.id'))

    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    title = Column(Unicode)
    keyword = Column(Unicode)
    description = Column(Unicode)
    url = Column(String)
    version = Column(Integer)

    site_id = Column(Integer, ForeignKey("site.id"))
    layout_id = Column(Integer, ForeignKey("layout.id"))

    relationship('Layout', backref='pages')

    @property
    def layout(self):
        return Layout.query.filter(Layout.id==self.layout_id).one()

    def __repr__(self):
        return '<%s %s %s>' % (self.__class__.__name__, self.url, self.title)

    """
    def __str__(self):
        return '%s'  % self.id

    def __unicode__(self):
        return u'%s' % self.title
            """
