# coding: utf-8
# -*- coding:utf-8 -*-

import sqlalchemy as sa
from datetime import datetime
import sqlalchemy.orm as orm
from sqlalchemy.orm import relationship
from pyramid.decorator import reify
#dont remove
from altaircms.modellib import model_to_dict, model_from_dict, model_column_items, model_column_iters
from altaircms.modellib import model_clone, BaseOriginalMixin
from altaircms.modellib import Base, DBSession
# ---

from sqlalchemy.ext.declarative import declared_attr

import pkg_resources
def import_symbol(symbol):
    return pkg_resources.EntryPoint.parse("x=%s" % symbol).load(False)
from altaircms.seeds.saleskind import SALESKIND_CHOICES

class WithOrganizationMixin(object):
    organization_id = sa.Column(sa.Integer, index=True) ## need FK?(organization.id)

def initialize_sql(engine, dropall=False):

    DBSession.remove()
    DBSession.configure(bind=engine)
    if dropall:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return DBSession



###
### ここからCMS用モデル
###

"""
このあたりevent/models.pyに移動した方が良い。
"""

PDICT = import_symbol("altaircms.seeds.prefecture:PrefectureMapping")
class Performance(BaseOriginalMixin, Base):
    """
    パフォーマンス
    """
    __tablename__ = "performance"
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, primary_key=True)
    backend_id = sa.Column(sa.Integer)
    event_id = sa.Column(sa.Integer, sa.ForeignKey('event.id'))

    display_order = sa.Column(sa.Integer, default=50)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

    title = sa.Column(sa.Unicode(255))
    venue = sa.Column(sa.Unicode(255)) #開催地
    prefecture = sa.Column(sa.Enum(*import_symbol("altaircms.seeds.prefecture:PREFECTURE_ENUMS"))) #開催地(県)
    open_on = sa.Column(sa.DateTime)  # 開場
    start_on = sa.Column(sa.DateTime)  # 開始
    end_on = sa.Column(sa.DateTime)  # 終了

    calendar_content = sa.Column(sa.UnicodeText, default=u"")
    code = sa.Column(sa.String(12))  # Organization.code(2桁) + Event.code(3桁) + 7桁(デフォルトはstart.onのYYMMDD+ランダム1桁)
    purchase_link = sa.Column(sa.UnicodeText)
    mobile_purchase_link = sa.Column(sa.UnicodeText)
    canceld = sa.Column(sa.Boolean, default=False)
    public = sa.Column(sa.Boolean, default=True)
    event = relationship("Event", backref=orm.backref("performances", order_by=start_on, cascade="all"))

    @property
    def salessegments(self):
        return self.sales

    @property
    def jprefecture(self):
        return PDICT.name_to_label.get(self.prefecture, u"--")

class SalesSegmentKind(WithOrganizationMixin, Base):
    """ 販売条件のためのマスターテーブル"""
    __tablename__ = "salessegment_kind"
    query = DBSession.query_property()
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(length=255))
    label = sa.Column(sa.Unicode(length=255), default=u"<不明>")
    publicp = sa.Column(sa.Boolean, default=True)

    @declared_attr
    def __table_args__(cls):
        return (sa.UniqueConstraint("name", "organization_id"), )

class SalesSegmentGroup(BaseOriginalMixin, Base):
    """ イベント単位の販売条件"""
    __tablename__ = "salessegment_group"
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, primary_key=True)
    event_id = sa.Column(sa.Integer, sa.ForeignKey('event.id'))
    event  = relationship("Event", uselist=False, backref="salessegment_groups")
    name = sa.Column(sa.Unicode(length=255))
    kind_id = sa.Column(sa.Integer, sa.ForeignKey("salessegment_kind.id"))
    kind = sa.Column(sa.String(length=255)) #backward compability
    publicp = sa.Column(sa.Boolean, default=True)
    master = orm.relationship(SalesSegmentKind, uselist=False)

    start_on = sa.Column(sa.DateTime, default=datetime.now)
    end_on = sa.Column(sa.DateTime, default=datetime.now)

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)
    backend_id = sa.Column(sa.Integer)


    @classmethod
    def create_defaults_from_event(cls, event):
        normal = cls(event=event,
                    name=u"一般販売",
                    kind="normal")
        first = cls(event=event,
                    name=u"一般先行",
                    kind="eary_firstcome")
        normal_kind = (SalesSegmentKind.query.filter_by(organization_id=event.organization_id, name=normal.kind).first() or
                       SalesSegmentKind(organization_id=event.organization_id, name=normal.kind, label=u"一般販売"))
        first_kind = (SalesSegmentKind.query.filter_by(organization_id=event.organization_id, name=first.kind).first() or
                       SalesSegmentKind(organization_id=event.organization_id, name=first.kind, label=u"一般先行"))
        normal.master = normal_kind
        first.master = first_kind
        return [normal, first]

class SalesSegment(BaseOriginalMixin, Base):
    """ 販売区分
    """
    __tablename__ = 'sale'
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, primary_key=True)
    backend_id = sa.Column(sa.Integer)

    performance_id = sa.Column(sa.Integer, sa.ForeignKey('performance.id'))
    performance  = relationship("Performance", backref=orm.backref("sales", cascade="all"))

    group_id = sa.Column(sa.Integer, sa.ForeignKey("salessegment_group.id"))
    group = orm.relationship("SalesSegmentGroup", backref="salessegments", uselist=False)

    start_on = sa.Column(sa.DateTime)
    end_on = sa.Column(sa.DateTime)

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

    publicp = sa.Column(sa.Boolean, default=True)

    SALESKIND_DICT = dict(SALESKIND_CHOICES)
    @property
    def jkind(self):
        return self.SALESKIND_DICT.get(self.type.kind, u"-")

class AliasDescripter(object):
    def __init__(self, alias):
        self.alias = alias

    def __get__(self, wrapper, obj):
        if obj:
            return getattr(obj, self.alias)
        else:
            return getattr(wrapper, self.alias)

class Ticket(BaseOriginalMixin, Base):
    """
    券種
    """
    __tablename__ = "ticket"
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, primary_key=True)
    backend_id = sa.Column(sa.Integer)

    display_order = sa.Column(sa.Integer, default=50)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now)
    price = sa.Column(sa.Integer, default=0)

    sale_id = sa.Column(sa.Integer, sa.ForeignKey("sale.id"))
    salessegment_id = AliasDescripter("sale_id")
    sale = relationship("SalesSegment", backref=orm.backref("tickets", order_by=price.desc(), cascade="all"), uselist=False)
    salessegment = AliasDescripter("sale")

    name = sa.Column(sa.Unicode(255))
    seattype = sa.Column(sa.Unicode(255))


class Genre(Base,  WithOrganizationMixin):
    __tablename__ = "genre"
    __tableargs__ = (
        sa.UniqueConstraint("organizationi_id", "name")
        )
    query = DBSession.query_property()
    is_root = sa.Column(sa.Boolean, default=True)
    id = sa.Column(sa.Integer, primary_key=True)
    display_order = sa.Column(sa.Integer, default=50)
    label = sa.Column(sa.Unicode(length=255))
    name = sa.Column(sa.String(length=255))
    origin = sa.Column(sa.String(length=32), doc="music, sports, event, stage")
    category_top_pageset_id = sa.Column(sa.Integer, sa.ForeignKey("pagesets.id", use_alter=True, name="fk_default_category_top_pageset"), doc=u"カテゴリトップページのid")
    category_top_pageset = orm.relationship("PageSet", uselist=False, primaryjoin="PageSet.id==Genre.category_top_pageset_id")

    @reify
    def origin_genre(self):
        return self.query_ancestors().filter(Genre.name==self.origin).one()

    def kick_category_toppage(self):
        self.category_top_pageset_id = None

    def is_category_toppage(self, pageset):
        return self.category_top_pageset_id == pageset.id

    def has_category_toppage(self):
        return bool(self.category_top_pageset_id)

    def save_as_category_toppage(self, pageset):
        Genre.query.filter(Genre.category_top_pageset_id==pageset.id, Genre.id!=self.id)\
            .update({"category_top_pageset_id": None}, synchronize_session=False)
        self.category_top_pageset_id = pageset.id

    def __repr__(self):
        return "<name=%s %s>" % (self.name, self.organization_id)

    def __unicode__(self):
        suffix = u" -- ページあり"if self.has_category_toppage() else u""
        return u"%s%s" % (self.label, suffix)

    def query_descendant(self, hop=None):
        qs = Genre.query.join(_GenrePath, Genre.id==_GenrePath.genre_id)
        if hop:
            qs = qs.filter(_GenrePath.hop<=hop)
        return qs.filter(_GenrePath.next_id==self.id)

    def query_ancestors(self, hop=None):
        qs = Genre.query.join(_GenrePath, Genre.id==_GenrePath.next_id)
        if hop:
            qs = qs.filter(_GenrePath.hop<=hop)
        return qs.filter(_GenrePath.genre_id==self.id).order_by(sa.asc(_GenrePath.hop))

    @property
    def children(self):
        return self.query_descendant(hop=1).all()

    @property
    def children_with_joined_pageset(self):
        return self.query_descendant(hop=1).options(orm.joinedload(Genre.category_top_pageset)).all()

    @property
    def ancestors_include_self(self):
        xs = list(self.ancestors)
        xs.insert(0, self)
        return xs

    @property
    def ancestors(self):
        return self.query_ancestors(hop=None).all()

    def _add_parent(self, genre, hop):
        self.is_root = False
        self._parents.append(_GenrePath(genre=self, next_genre=genre, hop=hop))

    def add_parent(self, genre, hop=1):
        path = _GenrePath.query.filter_by(genre=self, next_genre=genre).first()
        if path is None:
            self._add_parent(genre, hop)
        return self

    def update_parent(self, genre, hop):
        assert self.id and genre.id
        _GenrePath.query.filter_by(genre_id=self.id, next_id=genre.id).update({"hop": hop})
        return self

    def remove_parent(self, genre):
        assert self.id and genre.id
        _GenrePath.query.filter_by(genre_id=self.id, next_id=genre.id).delete()
        return self

class _GenrePath(Base):
    query = DBSession.query_property()
    __tablename__ = "genre_path"
    __table_args__ = (sa.UniqueConstraint("genre_id", "next_id"), )
    genre_id = sa.Column(sa.Integer, sa.ForeignKey("genre.id"), primary_key=True)
    genre = orm.relationship("Genre", backref=orm.backref("_parents", remote_side=genre_id), primaryjoin="_GenrePath.genre_id==Genre.id")
    next_genre = orm.relationship("Genre", primaryjoin="_GenrePath.next_id==Genre.id")
    next_id = sa.Column(sa.Integer, sa.ForeignKey("genre.id"), primary_key=True)
    hop = sa.Column(sa.Integer,  default=1)

    def __repr__(self):
        return "<%s -> %s (hop=%s)>" % (self.genre_id, self.next_id, self.hop)

## deprecated:
class Category(Base, WithOrganizationMixin): # todo: refactoring
    """
    サイト内カテゴリマスター

    hierarchy:   大      中      小
    　　　　　　  音楽
    　　　　　　　　　　　邦楽
                                  ポップス・ロック（邦楽）

                  スポーツ
　　　　　　　　　　　　　野球
　　　　　　　　　　　　　　　　　プロ野球
　　　　　　　　　演劇
　　　　　　　　　　　　　ミュージカル
                                  劇団四季
                  イベント(static page)

    ※ このオブジェクトは、対応するページへのリンクを持つ(これはCMSで生成されないページへのリンクで有る場合もある)

    nameはhtml要素のclass属性などに使われる(cssで画像を付加するためなどに).
    nameはascii only
    labelはカテゴリ名(imgのalt属性に使われることがある)
    e.g. name=music,  label=音楽
    """
    __tablename__ = "category"
    __table_args__ = (
        sa.UniqueConstraint("organization_id", "name"),
        )
    query = DBSession.query_property()
    id = sa.Column(sa.Integer, primary_key=True)

    parent_id = sa.Column(sa.Integer, sa.ForeignKey("category.id"))
    parent = orm.relationship("Category", remote_side=[id], backref="children", uselist=False)
    #parent = orm.relationship("Category", remote_side=[id], uselist=False, cascade="all")

    label = sa.Column(sa.Unicode(length=255))
    name = sa.Column(sa.String(length=255))
    imgsrc = sa.Column(sa.String(length=255))
    hierarchy = sa.Column(sa.Unicode(length=255), nullable=False)

    url = sa.Column(sa.Unicode(length=255))
    pageset_id = sa.Column(sa.Integer, sa.ForeignKey("pagesets.id"))
    pageset = orm.relationship("PageSet", backref=orm.backref("category", uselist=False), uselist=False)
    display_order = sa.Column(sa.Integer)
    origin = sa.Column(sa.Unicode(length=255),
                       doc=u"祖先を選定するためのフィールド今のところ{music, sports, stage, other}以外入らない。")
    ## originはenumにしても良いかもしれない
    attributes = sa.Column(sa.Unicode(length=255), default=u"")

    @classmethod
    def get_toplevel_categories(cls, hierarchy=u"大", request=None): ## fixme
        query = request.allowable(cls)
        return query.filter(cls.hierarchy==hierarchy, cls.parent==None)

    def ancestors(self, include_self=False): ## fixme rename `include_self' keyword
        """ return ancestors (order: parent, grand parent, ...)
        """
        r = []
        me = self
        while me.parent:
            r.append(me)
            me = me.parent
        r.append(me)

        ## not include self iff include_self is false
        if not include_self:
            r.pop(0)
        return r

class FeatureSetting(Base):
    __tablename__ = "featuresetting"
    __table_args__ = (sa.UniqueConstraint("organization_id", "name"), )

    query = DBSession.query_property()
    id = sa.Column(sa.Integer, primary_key=True)
    organization_id = sa.Column(sa.Integer, sa.ForeignKey('organization.id'))
    name = sa.Column(sa.String(length=255))
    value = sa.Column(sa.String(length=255))
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

    @classmethod
    def get_value_by_name(cls, name, organization_id):
        feature_setting = FeatureSetting.query.filter(cls.name == name, cls.organization_id==organization_id).first()
        if feature_setting is not None:
            return feature_setting.value
        else:
            return None

class WordSearch(Base):
    __tablename__ = "word_search"
    id = sa.Column(sa.Integer, primary_key=True)
    word_id = sa.Column(sa.Integer, sa.ForeignKey('word.id'))
    word = relationship("Word", backref=orm.backref('word_searches', cascade='all, delete-orphan'))
    data = sa.Column(sa.String(length=255))

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_at = sa.Column(sa.DateTime)

    def __init__(self, _str=None, **kwargs):
        if _str is not None:
            kwargs["data"] = _str
        super(WordSearch, self).__init__(**kwargs)

    def __str__(self):
        return self.data

class Event_Word(Base):
    __tablename__ = "event_word"
    id = sa.Column(sa.Integer, primary_key=True)
    event_id = sa.Column(sa.Integer, sa.ForeignKey('event.id'))
    event = relationship("Event", backref=orm.backref('event_word', cascade='all, delete-orphan'))
    word_id = sa.Column(sa.Integer, sa.ForeignKey('word.id'))
    word = relationship("Word", backref=orm.backref('event_word', cascade='all, delete-orphan'))
    #sorting = sa.Column(sa.Integer)
    #subscribable = sa.Column(sa.Boolean, default=False)

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

class Performance_Word(Base):
    __tablename__ = "performance_word"
    id = sa.Column(sa.Integer, primary_key=True)
    performance_id = sa.Column(sa.Integer, sa.ForeignKey('performance.id'))
    performance = relationship("Performance", backref=orm.backref('performance_word', cascade='all, delete-orphan'))
    word_id = sa.Column(sa.Integer, sa.ForeignKey('word.id'))
    word = relationship("Word", backref=orm.backref('performance_word', cascade='all, delete-orphan'))
    #sorting = sa.Column(sa.Integer)
    #subscribable = sa.Column(sa.Boolean, default=False)

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

class Word(Base, WithOrganizationMixin):
    __tablename__ = "word"
    id = sa.Column(sa.Integer, primary_key=True)
    type = sa.Column(sa.String(length=255))
    label = sa.Column(sa.String(length=255), nullable=False)
    label_kana = sa.Column(sa.String(length=255))
    description = sa.Column(sa.String(length=255))
    #link = sa.Column(sa.String(length=255))

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_at = sa.Column(sa.DateTime)

    query = DBSession.query_property()
    def __str__(self):
        return self.label

    performances = relationship("Performance", backref="keywords", secondary=Performance_Word.__tablename__)

    def __setattr__(self, key, value):
        if key == 'word_searches':
            old = dict()
            for a in self.word_searches:
                old[a.data] = a

            fixed = [ ]
            for b in value:
                if b.id is None and b.data in old:
                    fixed.append(old.pop(b.data))
                else:
                    fixed.append(b)
            for obj in old.values():
                DBSession.delete(obj)
            value = fixed

        super(Word, self).__setattr__(key, value)
