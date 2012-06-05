# coding: utf-8
import urllib
from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy import (Column, 
                        Integer, 
                        Unicode, 
                        String, 
                        Text, 
                        ForeignKey, 
                        DateTime)

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

from zope.interface import implements
from altaircms.interfaces import IHasSite
from altaircms.interfaces import IHasTimeHistory

from altaircms.models import Base, BaseOriginalMixin
from altaircms.models import DBSession
from altaircms.layout.models import Layout

import uuid
from datetime import datetime

class PublishUnpublishMixin(object):
    def is_published(self):
        return self.hash_url is None

    def to_unpublished(self):
        if self.hash_url is None:
            self.hash_url = uuid.uuid4().hex

    def to_published(self):
        self.hash_url = None

class HasAncestorMixin(object):
    ## require self.parent
    @property
    def ancestors(self, includeme=False): ## fixme rename `includeme' keyword
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
    
class PageSet(Base, 
              HasAncestorMixin):
    __tablename__ = 'pagesets'
    query = DBSession.query_property()
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255))
    version_counter = Column(Integer, default=0)
    url = Column(String(255), unique=True)
    event_id = Column(Integer, ForeignKey('event.id'))
    event = relationship('Event', backref='pagesets')

    parent_id = Column(Integer, ForeignKey('pagesets.id'))
    parent = orm.relationship("PageSet", remote_side=[id], uselist=False)
    
    def gen_version(self):
        if self.version_counter is None:
            self.version_counter = 0
        self.version_counter += 1
        return self.version_counter

    @property
    def sorted_pages(self):
        return sorted(self.pages, key=lambda p: p.publish_begin.strftime('%Y-%m-%d %H:%M:%S') if p.publish_begin else '')

    @classmethod
    def get_or_create(cls, page):
        if page.pageset is None:
            url = page.url
            pageset = cls(url=url, name=page.title + u" ページセット", event=page.event, version_counter=0)
            page.pageset = pageset
        else:
            pageset = page.pageset
            page.url = pageset.url

            assert pageset.event == page.event

        page.version = pageset.gen_version()
        return pageset

    def current(self, dt=None):
        dt = dt or datetime.now()
        where = (Page.in_term(dt)) | ((Page.publish_begin==None) & (Page.publish_end==None))
        return Page.query.filter(Page.pageset==self).filter(where).order_by("page.publish_begin").limit(1).first()

    # @property
    # def page_proxy(self):
    #     if hasattr(self, "_page_proxy"):
    #         return self._page_proxy
    #     self._page_proxy = self.get_current_page()

    # def getc_urrent_page(self):
    #     ## not tested
    #     ## パフォーマンス上げるために本当はここキャッシュしておけたりすると良いのかなと思う
    #     return Page.filter(Page.version==self.version_counter).one()


class Page(PublishUnpublishMixin, 
           BaseOriginalMixin,
           Base):
    """
    ページ
    """
    implements(IHasTimeHistory, IHasSite)

    query = DBSession.query_property()
    __tablename__ = "page"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('event.id'))
    event = relationship('Event', backref='pages')


    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    name = Column(Unicode(255), default=u"")
    title = Column(Unicode(255), default=u"")
    keywords = Column(Unicode(255), default=u"")
    description = Column(Unicode(255), default=u"")
    url = Column(String(255), unique=True, index=True) ##todo: delete
    version = Column(Integer, default=1)

    site_id = Column(Integer, ForeignKey("site.id"))
    layout_id = Column(Integer, ForeignKey("layout.id"))
    layout = relationship(Layout, backref='page', uselist=False)
    DEFAULT_STRUCTURE = "{}"
    structure = Column(Text, default=DEFAULT_STRUCTURE)
    hash_url = Column(String(length=32), default=lambda : uuid.uuid4().hex)

    event_id = Column(Integer, ForeignKey('event.id')) ## todo: delete?
    event = relationship('Event', backref='pages')

    pageset_id = Column(Integer, ForeignKey('pagesets.id'))
    pageset = relationship('PageSet', backref='pages', uselist=False)

    publish_begin = Column(DateTime)
    publish_end = Column(DateTime)

    @hybrid_method
    def in_term(self, dt):
        return (((self.publish_begin == None) or (self.publish_begin <= dt))
                and ((self.publish_end == None) or (self.publish_end > dt)))
    @in_term.expression
    def in_term(self, dt):
        return sa.sql.and_(sa.sql.or_((self.publish_begin == None), (self.publish_begin <= dt)), 
                           sa.sql.or_((self.publish_end == None), (self.publish_end > dt)))


    @property
    def public_tags(self):
        return [tag for tag in self.tags if tag.publicp == True]

    @property
    def private_tags(self):
        return [tag for tag in self.tags if tag.publicp == False]

    def __repr__(self):
        return '<%s id=%s %s>' % (self.__class__.__name__, self.id, self.url)

    def has_widgets(self):
        return self.structure != self.DEFAULT_STRUCTURE

    def clone(self, session, request=None):
        from . import clone
        return clone.page_clone(request, self, session)

    @classmethod
    def get_or_create_by_name(cls, name):
        page = cls.query.filter_by(name=name).first()
        if page:
            return page
        else:
            return cls(name=name)
    
## master    
class PageDefaultInfo(Base):
    __tablename__ = "page_default_info"
    id = sa.Column(sa.Integer, primary_key=True)
    title_fmt = sa.Column(sa.Unicode(255))
    url_fmt = sa.Column(sa.Unicode(255))

    pageset_id = sa.Column(sa.Integer, sa.ForeignKey("pagesets.id"))
    pageset = orm.relationship("PageSet", uselist=False)

    keywords = Column(Unicode(255), default=u"")
    description = Column(Unicode(255), default=u"")
    
    def _urlprefix_from_category(self, connector=u"/"):
        category = self.category
        r = []
        while category:
            r.append(category.label)
            category = category.parent
        return connector.join(reversed(r))
 
    def url(self, part):
        """ pageを作成するときに使う"""
        string = self.url_fmt % {"url": part}
        if isinstance(string, unicode):
            string = string.encode("utf-8")
        return urllib.quote(string)


    def title(self, title):
        return self.title_fmt % {"title": title,  "self": self}



    def create_pageset(self, name, category=None, url=None):
        url = self.url(url or name)
        pageset = PageSet(parent=self.pageset, url=url, name=name)
        if category:
            category.pageset = pageset
        return pageset

        
    def create_page(self, name, category=None, keywords=None, description=None, url=None, layout=None):
        pageset = self.create_pageset(name, category=category, url=url)
        title = self.title(name)
        return Page(pageset=pageset, 
                    url=pageset.url, 
                    name=name, 
                    title=title, 
                    layout=layout, 
                    keywords=keywords or self.keywords, 
                    description=description or self.description)

    
    def clone_with_pageset(self, pageset, url_fmt=None, title_fmt=None, 
                          keywords=None, description=None):
        return self.__class__(pageset=pageset,
                              url_fmt=url_fmt or self.url_fmt, 
                              title_fmt=title_fmt or self.title_fmt, 
                              keywords=keywords or self.keywords, 
                              description=description or self.description)

