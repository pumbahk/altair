# coding: utf-8
from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

from zope.interface import implements
from altaircms.interfaces import IHasSite
from altaircms.interfaces import IHasTimeHistory

from altaircms.models import Base, BaseOriginalMixin
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
    
class PageSet(Base):
    __tablename__ = 'pagesets'
    query = DBSession.query_property()
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255))
    version_counter = Column(Integer, default=0)
    url = Column(String(255), unique=True)
    
    def gen_version(self):
        self.version_counter += 1
        return self.version_counter

class Page(PublishUnpublishMixin, 
           HasAncestorMixin, 
           BaseOriginalMixin,
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


    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    title = Column(Unicode(255), default=u"")
    keywords = Column(Unicode(255), default=u"")
    description = Column(Unicode(255), default=u"")
    url = Column(String(255), unique=True, index=True)
    version = Column(Integer, default=1)

    site_id = Column(Integer, ForeignKey("site.id"))
    layout_id = Column(Integer, ForeignKey("layout.id"))
    layout = relationship(Layout, backref='page', uselist=False)
    DEFAULT_STRUCTURE = "{}"
    structure = Column(Text, default=DEFAULT_STRUCTURE)
    hash_url = Column(String(length=32), default=None)

    event_id = Column(Integer, ForeignKey('event.id'))
    event = relationship('Event', backref='pages')

    pageset_id = Column(Integer, ForeignKey('pagesets.id'))
    pageset = relationship('PageSet', backref='pages')

    publish_begin = Column(DateTime)
    publis_end = Column(DateTime)

    ## todo refactoring?
    @hybrid_property
    def public_tags(self):
        return [tag for tag in self.tags if tag.publicp == True]

    @hybrid_property
    def private_tags(self):
        return [tag for tag in self.tags if tag.publicp == False]

    def __repr__(self):
        return '<%s id=%s %s>' % (self.__class__.__name__, self.id, self.url)

    # def __repr__(self):
    #     return unicode(self.title)

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
