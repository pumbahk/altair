# coding: utf-8
import logging
logger = logging.getLogger(__name__)
import json
from sqlalchemy.ext.declarative import declared_attr
from altaircms.modelmanager.ancestors import HasAncestorMixin
from datetime import datetime
from pyramid.decorator import reify
import sqlalchemy as sa
from altaircms import helpers as h
import sqlalchemy.orm as orm
from .nameresolver import GenrePageInfoResolver
from .nameresolver import EventPageInfoResolver
from .nameresolver import OtherPageInfoResolver
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

from altaircms.models import Base, BaseOriginalMixin
from altaircms.models import DBSession
from altaircms.models import model_to_dict
from altaircms.layout.models import Layout
from altaircms.models import WithOrganizationMixin


class PublishStatusMixin(object):
    def publish_status(self, dt):
        dt = dt or datetime.now()
        if not self.published:
            return u"非公開(期間:%s)" % h.term_datetime(self.publish_begin, self.publish_end)
        
        if self.publish_begin and self.publish_begin > dt:
            return u"公開前(%sに公開)" % h.base.jdatetime(self.publish_begin)
        elif self.publish_end is None:
            return u"公開中"
        elif self.publish_end < dt:
            return u"公開終了(%sに終了)"% h.base.jdatetime(self.publish_end)
        else:
            return u"公開中(期間:%s)" % h.term_datetime(self.publish_begin, self.publish_end)

    ### page access
    def publish(self):
        self.published = True

    def unpublish(self):
        self.published = False


    
class PageSet(Base, 
              WithOrganizationMixin, 
              HasAncestorMixin):
    __tablename__ = 'pagesets'
    type = "page"

    query = DBSession.query_property()
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255))
    version_counter = Column(Integer, default=0)
    url = Column(String(255))
    short_url_keyword = Column(String(255), default=None)
    event_id = Column(Integer, ForeignKey('event.id'))
    event = relationship('Event', backref='pagesets')

    parent_id = Column(Integer, ForeignKey('pagesets.id'))
    parent = orm.relationship("PageSet", remote_side=[id], uselist=False)

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

    pagetype_id = Column(sa.Integer, ForeignKey("pagetype.id"))
    pagetype = orm.relationship("PageType", backref="pagesets", uselist=False)

    genre_id = Column(sa.Integer, ForeignKey("genre.id"))
    genre = orm.relationship("Genre",  backref="pageset",  uselist=False, primaryjoin="PageSet.genre_id==Genre.id")

    def delete(self):
        ##全部消す
        for t in list(self.tags):
            self.tags.remove(t)
        for page in self.pages:
            for w in page.widgets:
                w.delete()

    @declared_attr
    def __table_args__(cls):
        return (sa.schema.UniqueConstraint("url", "organization_id"), )

    @property
    def taglabel(self):
        return u"pageset:%s" % self.id

    @classmethod
    def publishing(cls, d=None, qs=None):
        qs = qs or cls.query
        qs = qs.filter(PageSet.id==Page.pageset_id)
        return qs.filter(Page.in_term(d)).filter(Page.published==True)

    
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
            pageset = cls(url=url, short_url_keyword=page.short_url_keyword, name=page.name, event=page.event, version_counter=0)
            page.pageset = pageset
        else:
            pageset = page.pageset
            page.url = pageset.url

            assert pageset.event == page.event
        pageset.pagetype = page.pagetype
        page.version = pageset.gen_version()
        return pageset

    # @classmethod
    # def unpublished_pageset(cls, dt, qs=None):
    #     """dt時点で掲載されていないページを探す"""
    #     qs = qs or cls.query
    #     where = (Page.in_term(dt)) | ((Page.publish_begin <= dt) & (Page.publish_end==None))
    #     qs = qs.filter(sa.not_(where & (Page.published==True) & (PageSet.id==Page.pageset_id)))
    #     return qs

    def current(self, dt=None, published=True):
        dt = dt or datetime.now()
        where = (Page.in_term(dt)) | ((Page.publish_begin==None) & (Page.publish_end==None))
        if published:
            where = where & (Page.published == published)
        qs = Page.query.filter(Page.pageset==self).filter(where)
        return qs.order_by(sa.desc("page.publish_begin"), "page.publish_end").limit(1).first()

    def create_page(self, published=None, force=False):
        base_page = self.current(published=published)
        if base_page is None:
            if force:
                logger.info("pageset_id=%s,  base page is not found. but force=True, base page as latest updated page." % self.id)
                base_page = Page.query.filter(Page.pageset_id==self.id).order_by(sa.desc(Page.updated_at)).first()
            if base_page is None:
                logger.warn("pageset_id=%s,  base page is not found." % self.id)
                return None
        created = Page(pageset=self, version=self.gen_version())
        created.event = base_page.event
        created.name = base_page.name
        created.title = base_page.title
        created.keywords = base_page.keywords
        created.description = base_page.description
        created.url = base_page.url
        created.layout = base_page.layout
        created.pagetype = base_page.pagetype
        created.organization_id = base_page.organization_id
        return created

    def take_in_event(self, event):
        self.event = event
        for p in self.pages:
            p.event = event
        if event is None:
            self.pagetype = PageType.query.filter(PageType.organization_id==self.organization_id, PageType.page_role!="event_detail").first()
        else:
            self.pagetype = PageType.query.filter(PageType.organization_id==self.organization_id, PageType.page_role=="event_detail").first()

    @property
    def public_tags(self):
        return [tag for tag in self.tags if tag.publicp == True]

    @property
    def private_tags(self):
        return [tag for tag in self.tags if tag.publicp == False]

    def to_dict(self): #for slackoff update view
        params = model_to_dict(self)
        params.update(id=self.id, 
                      tags_string=u", ".join(t.label for t in self.public_tags if t.organization_id), 
                      private_tags_string=u", ".join(t.label for t in self.private_tags if t.organization_id),
                      mobile_tags_string=u", ".join(t.label for t in self.mobile_tags if t.organization_id),
                      genre_id=self.genre_id,
                      )
        return params
    
    def kick_genre(self):
        from altaircms.models import Genre
        Genre.query.filter(Genre.category_top_pageset_id==self.id).update({"category_top_pageset_id": None})
        self.genre_id = None

    # @property
    # def page_proxy(self):
    #     if hasattr(self, "_page_proxy"):
    #         return self._page_proxy
    #     self._page_proxy = self.get_current_page()

    # def getc_urrent_page(self):
    #     ## not tested
    #     ## パフォーマンス上げるために本当はここキャッシュしておけたりすると良いのかなと思う
    #     return Page.filter(Page.version==self.version_counter).one()

class StaticPageSet(Base, 
                    WithOrganizationMixin, 
                    HasAncestorMixin):
    __tablename__ = 'static_pagesets'

    query = DBSession.query_property()
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255))
    version_counter = Column(Integer, default=0)
    url = Column(String(255), unique=True)

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

    pagetype_id = Column(sa.Integer, ForeignKey("pagetype.id"))
    pagetype = orm.relationship("PageType", backref="static_pagesets", uselist=False)
    hash = sa.Column(sa.String(length=32), nullable=False)

    def current(self, dt=None, published=True):
        dt = dt or datetime.now()
        where = (StaticPage.in_term(dt)) | ((StaticPage.publish_begin==None) & (StaticPage.publish_end==None))
        if published:
            where = where & (StaticPage.published == published)
        qs = StaticPage.query.filter(StaticPage.pageset==self).filter(where)
        return qs.order_by(sa.desc(StaticPage.publish_begin), StaticPage.publish_end).limit(1).first()

    @declared_attr
    def __table_args__(cls):
        return (sa.schema.UniqueConstraint("url", "organization_id", "pagetype_id"), )


class StaticPage(BaseOriginalMixin, 
                 WithOrganizationMixin, 
                 PublishStatusMixin, 
                 Base):
    query = DBSession.query_property()
    __tablename__ = "static_pages"

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)
    file_structure_text = orm.deferred(sa.Column(sa.Text, default="", nullable=False))
    uploaded_at = sa.Column(sa.DateTime)
    name = sa.Column(sa.String(255), doc="directory name(internal)")
    label = sa.Column(sa.Unicode(255), doc=u"日本語名", default=u"")
    publish_begin = Column(DateTime)
    publish_end = Column(DateTime)
    published = Column(sa.Boolean, default=False)
    last_editor = Column(sa.String(255), doc=u'最終編集者')
    pageset_id = Column(sa.Integer, ForeignKey("static_pagesets.id"))
    pageset = relationship('StaticPageSet', backref=orm.backref('pages', order_by=sa.asc("publish_begin")), uselist=False)
    layout_id = Column(Integer, ForeignKey("layout.id"))    
    layout = relationship(Layout, backref='static_pages', uselist=False)
    interceptive = Column(sa.Boolean, default=False)

    @reify
    def file_structure(self):
        return json.loads(self.file_structure_text)
    
    @property
    def prefix(self):
        return self.pageset.hash

    @property
    def description(self):
        return self.label or self.name or u""

    @hybrid_method
    def in_term(self, dt):
        return (((self.publish_begin == None) or (self.publish_begin <= dt))
                and ((self.publish_end == None) or (self.publish_end > dt)))

    def __copy__(self):
        copied = super(StaticPage, self).__copy__()
        copied.uploaded_at = None
        copied.file_structure_text = ""
        return copied

    @in_term.expression
    def in_term(self, dt):
        return sa.sql.and_(sa.sql.or_((self.publish_begin == None), (self.publish_begin <= dt)), 
                           sa.sql.or_((self.publish_end == None), (self.publish_end > dt)))

class Page(BaseOriginalMixin,
           WithOrganizationMixin, 
           PublishStatusMixin, 
           Base):
    """
    ページ
    """

    query = DBSession.query_property()
    __tablename__ = "page"
    id = Column(Integer, primary_key=True)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    name = Column(Unicode(255), default=u"")
    title = Column(Unicode(255), default=u"")
    keywords = Column(Unicode(500), default=u"")
    description = Column(Unicode(255), default=u"")
    url = Column(String(255), index=True) ##todo: delete
    short_url_keyword = Column(String(255), default=None)
    version = Column(Integer, default=1)

    layout_id = Column(Integer, ForeignKey("layout.id"))
    layout = relationship(Layout, backref='pages', uselist=False)
    DEFAULT_STRUCTURE = "{}"
    structure = Column(Text, default=DEFAULT_STRUCTURE)
    # hash_url = Column(String(length=32), default=lambda : uuid.uuid4().hex)

    event_id = Column(Integer, ForeignKey('event.id')) ## todo: delete?
    event = relationship('Event', backref=orm.backref('pages', order_by=sa.asc("publish_begin")), uselist=False)

    pageset_id = Column(Integer, ForeignKey('pagesets.id'))
    pageset = relationship('PageSet', backref=orm.backref('pages', order_by=sa.asc("publish_begin")), uselist=False)

    pagetype_id = Column(sa.Integer, ForeignKey("pagetype.id"))
    pagetype = orm.relationship("PageType", backref="pages", uselist=False)

    publish_begin = Column(DateTime)
    publish_end = Column(DateTime)
    published = Column(sa.Boolean, default=False)

    @declared_attr
    def __table_args__(cls):
        return (sa.schema.UniqueConstraint("url", "organization_id"), )

    @hybrid_method
    def in_term(self, dt):
        return (((self.publish_begin == None) or (self.publish_begin <= dt))
                and ((self.publish_end == None) or (self.publish_end > dt)))

    @in_term.expression
    def in_term(self, dt):
        return sa.sql.and_(sa.sql.or_((self.publish_begin == None), (self.publish_begin <= dt)), 
                           sa.sql.or_((self.publish_end == None), (self.publish_end > dt)))

    def __repr__(self):
        return '<%s id=%s %s>' % (self.__class__.__name__, self.id, self.url)

    def has_widgets(self):
        return self.structure != self.DEFAULT_STRUCTURE

    def clone(self, session, request=None):
        from . import clone
        cloned = clone.page_clone(request, self, session)
        now = datetime.now()
        cloned.created_at = now
        cloned.updated_at = now
        return cloned

    @classmethod
    def get_or_create_by_name(cls, name):
        page = cls.query.filter_by(name=name).first()
        if page:
            return page
        else:
            return cls(name=name)

    def publish_status(self, dt):
        if not self.published:
            return u"非公開(期間:%s)" % h.term_datetime(self.publish_begin, self.publish_end)
        
        if self.publish_begin and self.publish_begin > dt:
            return u"公開前(%sに公開)" % h.base.jdatetime(self.publish_begin)
        elif self.publish_end is None:
            return u"公開中"
        elif self.publish_end < dt:
            return u"公開終了(%sに終了)"% h.base.jdatetime(self.publish_end)
        else:
            return u"公開中(期間:%s)" % h.term_datetime(self.publish_begin, self.publish_end)

    ### page access
    def publish(self):
        self.published = True

    def unpublish(self):
        self.published = False

    def valid_layout(self):
        if self.layout is None:
            return True
        if self.layout.template_filename is None:
            raise ValueError("*layout validation* page(id=%s) layout(id=%s) don't have template" % (self.id,  self.layout.id))
        if not self.layout.valid_block():
            raise ValueError("*layout validation* page(id=%s) layout(id=%s) layout is broken" % (self.id, self.layout.id))
        return True

    @property
    def kind(self):
        return self.pagetype.kind

class PageType(WithOrganizationMixin, Base):
    query = DBSession.query_property()
    __tablename__ = "pagetype"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(255))
    label = sa.Column(sa.Unicode(255), doc=u"日本語表記")
    page_default_role = "normal"
    page_role = sa.Column(sa.String(16), doc=u"pageの利用方法など", default=page_default_role)
    ## 小カテゴリはportalではないが、カテゴリトップにしたいため
    page_role_candidates = [("portal", u"カテゴリトップに利用"), 
                            ("event_detail", u"イベント詳細ページに利用"), 
                            ("static", u"静的ページに利用"), ]

    page_rendering_type = sa.Column(sa.String(16), doc=u"pageのレンダリング方法", default="widget")
    page_rendering_type_candidates = [("widget", u"widget利用"), 
                                      ("search", u"検索利用")]
    is_important = sa.Column(sa.Boolean, default=False, doc=u"重要なページ", nullable=False) #boolean is good?
    @declared_attr
    def __table_args__(cls):
        return (sa.schema.UniqueConstraint("name", "organization_id"), )

    DEFAULTS = (u"portal",
                u"event_detail",
                u"document", 
                u"static", 
                u"search")

    DEFAULTS_LABELS = (u"ポータル", 
                       u"イベント詳細", 
                       u"ドキュメント", 
                       u"静的ページ"
                       u"検索利用"
                       )
    @property
    def is_portal(self):
        return self.page_role == "portal"

    @property
    def is_static_page(self):
        return self.page_role == "static"

    @property
    def is_event_detail(self):
        return self.name == "event_detail" or self.page_role == "event_detail"
    
    @classmethod
    def get_or_create(cls, **kwargs):
        return cls.query.filter_by(**kwargs).first() or cls(**kwargs)

    @classmethod
    def create_default_pagetypes(cls, organization_id=None):
        qs = cls.query.filter(cls.organization_id==organization_id, cls.name.in_(cls.DEFAULTS)).all()
        cached = {o.name: o for o in qs}
        r = []
        for name, label in zip(cls.DEFAULTS, cls.DEFAULTS_LABELS):
            if name in ("portal", "search"):
                if name == "search":
                    r.append(cached.get(name) or cls(name=name, label=label, organization_id=organization_id, page_role="portal", page_rendering_type="search"))
                else:
                    r.append(cached.get(name) or cls(name=name, label=label, organization_id=organization_id, page_role="portal"))
            elif name == "event_detail":
                r.append(cached.get(name) or cls(name=name, label=label, organization_id=organization_id, page_role="event_detail"))                
            elif name == "static":
                r.append(cached.get(name) or cls(name=name, label=label, organization_id=organization_id, page_role="static"))                
            else:
                r.append(cached.get(name) or cls(name=name, label=label, organization_id=organization_id, page_role="normal"))
        return r

    ## backward compabirity. this is deprecated property
    @property
    def kind(self):
        if self.is_event_detail:
            return "event"
        else:
            return "other"

## master    
class PageDefaultInfo(WithOrganizationMixin, Base):
    query = DBSession.query_property()
    __tablename__ = "page_default_info"
    id = sa.Column(sa.Integer, primary_key=True)
    title_prefix = sa.Column(sa.Unicode(255), default=u"")
    title_suffix = sa.Column(sa.Unicode(255), default=u"")
    url_prefix = sa.Column(sa.Unicode(255), default=u"")

    keywords = Column(Unicode(255), default=u"")
    description = Column(Unicode(255), default=u"")
    pagetype_id = sa.Column(sa.Integer, sa.ForeignKey("pagetype.id"))
    pagetype = orm.relationship("PageType", uselist=False, backref="default_info")

    @reify
    def resolver_genre(self):
        return GenrePageInfoResolver(self)

    @reify
    def resolver_event(self):
        return EventPageInfoResolver(self)

    @reify
    def resolver_other(self):
        return OtherPageInfoResolver(self)

    def get_page_info(self, pagetype, genre=None, event=None):
        if event:
            return self.resolver_event.resolve(genre, event)
        elif genre:
            return self.resolver_genre.resolve(genre)
        else:
            return self.resolver_other.resolve()

class PageTag2Page(Base):
    __tablename__ = "pagetag2pageset"
    query = DBSession.query_property()
    object_id = sa.Column(sa.Integer, sa.ForeignKey("pagesets.id"), primary_key=True)
    tag_id = sa.Column(sa.Integer, sa.ForeignKey("pagetag.id"), primary_key=True)
    __tableargs__ = (
        sa.UniqueConstraint("object_id", "tag_id") 
        )

class MobileTag2Page(Base):
    __tablename__ = "mobiletag2pageset"
    query = DBSession.query_property()
    object_id = sa.Column(sa.Integer, sa.ForeignKey("pagesets.id"), primary_key=True)
    tag_id = sa.Column(sa.Integer, sa.ForeignKey("mobiletag.id"), primary_key=True)
    __tableargs__ = (
        sa.UniqueConstraint("object_id", "tag_id")
    )

class PageTag(WithOrganizationMixin, Base):
    CLASSIFIER = "page"

    __tablename__ = "pagetag"
    query = DBSession.query_property()
    id = sa.Column(sa.Integer, primary_key=True)
    label = sa.Column(sa.Unicode(255), index=True)
    pages = orm.relationship("PageSet", secondary="pagetag2pageset", backref="tags")
    publicp = sa.Column(sa.Boolean, default=False)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)
    @declared_attr
    def __tableargs__(cls):
        return  ((sa.schema.UniqueConstraint(cls.label,cls.organization_id)))        

#def delete_orphan_pagetag(mapper, connection, target):
#    PageTag.query.filter(~PageTag.pages.any()).delete(synchronize_session=False)
#sa.event.listen(Page, "after_delete", delete_orphan_pagetag)

class MobileTag(WithOrganizationMixin, Base):
    __tablename__ = "mobiletag"
    query = DBSession.query_property()
    id = sa.Column(sa.Integer, primary_key=True)
    label = sa.Column(sa.Unicode(255), index=True)
    pages = orm.relationship("PageSet", secondary="mobiletag2pageset", backref="mobile_tags")
    publicp = sa.Column(sa.Boolean, default=False)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)
    @declared_attr
    def __tableargs__(cls):
        return  ((sa.schema.UniqueConstraint(cls.label,cls.organization_id)))

