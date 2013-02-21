# coding: utf-8
# -*- coding:utf-8 -*-

import sqlalchemy as sa


from datetime import datetime
import sqlahelper
import sqlalchemy.orm as orm
from sqlalchemy.orm import relationship

from sqlalchemy.sql.operators import ColumnOperators
from sqlalchemy.ext.declarative import declared_attr

import pkg_resources
def import_symbol(symbol):
    return pkg_resources.EntryPoint.parse("x=%s" % symbol).load(False)
from altaircms.seeds.saleskind import SALESKIND_CHOICES

def model_to_dict(obj):
    return {k: getattr(obj, k) for k, v in obj.__class__.__dict__.iteritems() \
                if isinstance(v, ColumnOperators)}

def model_from_dict(modelclass, D):
    instance = modelclass()
    items_fn = D.iteritems if hasattr(D, "iteritems") else D.items
    for k, v in items_fn():
        setattr(instance, k, v)
    return instance

def model_column_items(obj):
    return [(k, v) for k, v in obj.__class__.__dict__.items()\
                if isinstance(v, ColumnOperators)]

def model_column_iters(modelclass, D):
    for k, v in modelclass.__dict__.items():
        if isinstance(v, ColumnOperators):
            yield k, D.get(k)

def model_clone(obj):
    cls = obj.__class__
    cloned = cls()
    pk_keys = set([c.key for c in orm.class_mapper(cls).primary_key])
    for p in  orm.class_mapper(cls).iterate_properties:
        if p.key not in  pk_keys:
            setattr(cloned, p.key, getattr(obj, p.key, None))
    return cloned
            
class BaseOriginalMixin(object):

    def to_dict(self):
        return model_to_dict(self)

    def column_items(self):
        return model_column_items(self)

    @classmethod
    def column_iters(cls, D):
        return model_column_iters(cls, D)

    @classmethod
    def from_dict(cls, D):
        return model_from_dict(cls, D)

class WithOrganizationMixin(object):
    organization_id = sa.Column(sa.Integer, index=True) ## need FK?(organization.id)
    
Base = sqlahelper.get_base()
DBSession = sqlahelper.get_session()


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

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

    title = sa.Column(sa.Unicode(255))
    venue = sa.Column(sa.Unicode(255)) #開催地
    prefecture = sa.Column(sa.Enum(*import_symbol("altaircms.seeds.prefecture:PREFECTURE_ENUMS"))) #開催地(県)
    open_on = sa.Column(sa.DateTime)  # 開場
    start_on = sa.Column(sa.DateTime)  # 開始
    end_on = sa.Column(sa.DateTime)  # 終了

    calendar_content = sa.Column(sa.UnicodeText, default=u"")
    purchase_link = sa.Column(sa.UnicodeText)
    mobile_purchase_link = sa.Column(sa.UnicodeText)
    canceld = sa.Column(sa.Boolean, default=False)
    event = relationship("Event", backref=orm.backref("performances", order_by=start_on, cascade="all"))

    @property
    def salessegments(self):
        return self.sales

    @property
    def jprefecture(self):
        return PDICT.name_to_label.get(self.prefecture, u"--")

class SalesSegmentGroup(BaseOriginalMixin, Base):
    """ 販売条件のためのマスターテーブル"""
    __tablename__ = "salessegment_group"
    query = DBSession.query_property()    

    id = sa.Column(sa.Integer, primary_key=True)
    event_id = sa.Column(sa.Integer, sa.ForeignKey('event.id'))
    event  = relationship("Event")
    name = sa.Column(sa.Unicode(length=255))
    kind = sa.Column(sa.Unicode(length=255))

    start_on = sa.Column(sa.DateTime)
    end_on = sa.Column(sa.DateTime)

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

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
    group = orm.relationship("SalesSegmentGroup")

    start_on = sa.Column(sa.DateTime)
    end_on = sa.Column(sa.DateTime)

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

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

    def __repr__(self):
        return "<name=%s %s>" % (self.name, self.organization_id)


    def query_descendant(self, hop=None):
        qs = self.query_join_path_from_self
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
    def ancestors(self):
        return self.query_ancestors(hop=None).all()

    def _add_parent(self, genre, hop):
        self.is_root = False
        self._parents.append(_GenrePath(genre=self, next_genre=genre, hop=hop))        

    def add_parent(self, genre, hop):
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
