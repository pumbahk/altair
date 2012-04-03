# coding: utf-8
from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

from zope.interface import implements
from altaircms.interfaces import IHasSite
from altaircms.interfaces import IHasTimeHistory

from altaircms.models import Base
from altaircms.models import DBSession
from altaircms.layout.models import Layout

class PublishUnpublishMixin(object):
    def is_published(self):
        return self.hash_url is None

    def to_unpublished(self):
        if self.hash_url is None:
            import uuid
            self.hash_url = uuid.uuid4().hex

    def to_published(self):
        self.hash_url = None

class HasAncestorMixin(object):
    ## require self.parent
    @property
    def ancestors(self, includeme=False): 
        """ return ancestors (order: parent, grand parent, ...)
        """
        r = []
        me = self
        while me.parent:
            r.append(me)
            me = me.parent
        r.append(me)
        
        ## not include self iff includeme is false
        if not includeme:
            r.pop(0)
        return r
    
class Page(PublishUnpublishMixin, 
           HasAncestorMixin, 
           Base):
    """
    ページ
    """
    implements(IHasTimeHistory, IHasSite)

    query = DBSession.query_property()
    __tablename__ = "page"

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('page.id'))
    @declared_attr
    def parent(cls):
        return relationship(cls, backref=orm.backref("child", remote_side=[cls.id]), uselist=False)
    event_id = Column(Integer, ForeignKey('event.id'))
    event = relationship('Event', backref='pages')


    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    title = Column(Unicode, default=u"")
    keywords = Column(Unicode, default=u"")
    description = Column(Unicode, default=u"")
    url = Column(String)
    version = Column(Integer)

    site_id = Column(Integer, ForeignKey("site.id"))
    layout_id = Column(Integer, ForeignKey("layout.id"))
    layout = relationship(Layout, backref='page', uselist=False)
    DEFAULT_STRUCTURE = "{}"
    structure = Column(String, default=DEFAULT_STRUCTURE)
    hash_url = Column(String(length=32), default=None)

    # def __repr__(self):
    #     return '<%s id=%s %s>' % (self.__class__.__name__, self.id, self.url)

    def __repr__(self):
        return unicode(self.title)

    def __unicode__(self):
        return u'%s(%s)' % (self.title, self.url)

    def has_widgets(self):
        return self.structure != self.DEFAULT_STRUCTURE

    def clone(self, session):
        from . import clone
        return clone.page_clone(self, session)


    """
    def __str__(self):
        return '%s'  % self.id

    def __unicode__(self):
        return u'%s' % self.title
            """
