# coding: utf-8
# -*- coding:utf-8 -*-

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr

from datetime import datetime
import sqlahelper
import sqlalchemy.orm as orm
from sqlalchemy import (Column, Integer, Unicode, String, ForeignKey, DateTime, Boolean)
from sqlalchemy.orm import relationship

from sqlalchemy.sql.operators import ColumnOperators

import pkg_resources
def import_symbol(symbol):
    return pkg_resources.EntryPoint.parse("x=%s" % symbol).load(False)

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

    id = Column(Integer, primary_key=True)
    backend_id = Column(Integer, nullable=False)
    event_id = Column(Integer, ForeignKey('event.id'))
    client_id = Column(Integer, ForeignKey("client.id"))

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    title = Column(Unicode(255))
    venue = Column(Unicode(255)) #開催地
    prefecture = Column(sa.Enum(*import_symbol("altaircms.seeds.prefecture:PREFECTURE_ENUMS"))) #開催地(県)
    open_on = Column(DateTime)  # 開場
    start_on = Column(DateTime)  # 開始
    end_on = Column(DateTime)  # 終了

    purchase_link = Column(sa.UnicodeText)
    canceld = Column(Boolean, default=False)
    # sale = relationship("Sale", backref=orm.backref("performances", order_by=id))
    event = relationship("Event", backref=orm.backref("performances", order_by=start_on))
    # client = relationship("Client", backref=orm.backref("performances", order_by=id))

    @property
    def jprefecture(self):
        return PDICT.name_to_label.get(self.prefecture, u"--")

class Sale(BaseOriginalMixin, Base):
    """ 販売条件
    performance -* sale -* ticketという関連
    ??? ※ただし、簡略化のためsaleもticketもeventを持つ
    """
    __tablename__ = 'sale'
    query = DBSession.query_property()

    id = Column(Integer, primary_key=True)
    
    performance_id = Column(Integer, ForeignKey('performance.id'))
    performance = relationship("Performance", backref=orm.backref("sales", order_by=id))

    name = Column(Unicode(length=255), doc=u"saleskind. 販売条件(最速抽選, 先行抽選, 先行先着, 一般販売, 追加抽選.etc)")
    start_on = Column(DateTime)
    end_on = Column(DateTime)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Ticket(BaseOriginalMixin, Base):
    """
    券種
    """
    __tablename__ = "ticket"
    query = DBSession.query_property()

    id = Column(Integer, primary_key=True)
    orderno = Column(Integer)
    sale_id = Column(Integer, ForeignKey("sale.id"))
    event_id = Column(Integer, ForeignKey("event.id"))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    price = Column(Integer, default=0)

    sale = relationship("Sale", backref=orm.backref("tickets", order_by=orderno))
    event = relationship("Event", backref=orm.backref("tickets", order_by=orderno))

    seattype = Column(Unicode(255))


# class Seatfigure(BaseOriginalMixin, Base):
#     """
#     席図
#     """
#     __tablename__ = "seatfigure"
#     query = DBSession.query_property()

#     id = Column(Integer, primary_key=True)
#     created_at = Column(DateTime, default=datetime.now)
#     updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

#     figure_url = Column(String(255))
#     controller_url = Column(String(255))

#     client_id = Column(Integer, ForeignKey("event.id"))




class Site(BaseOriginalMixin, Base):
    __tablename__ = "site"
    query = DBSession.query_property()

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    name = Column(Unicode(255))
    description = Column(Unicode(255))
    url = Column(String(255))

    client_id = Column(Integer, ForeignKey("client.id")) #@TODO: サイトにくっつけるべき？
    client = relationship("Client", backref="site", uselist=False) ##?

    
class Category(Base):
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
    __tableargs__ = (
        sa.UniqueConstraint("site_id", "name")
        )
    query = DBSession.query_property()
    id = sa.Column(sa.Integer, primary_key=True)

    site_id = sa.Column(sa.Integer, sa.ForeignKey("site.id"))
    site = orm.relationship("Site", backref="categories", uselist=False)
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
    orderno = sa.Column(sa.Integer)
    origin = sa.Column(sa.Unicode(length=255))

    @classmethod
    def get_toplevel_categories(cls, hierarchy=u"大", site=None, request=None): ## fixme
        if site is None and request and hasattr(request,"site"):
            site = request.site
            return cls.query.filter(cls.site==site, cls.hierarchy==hierarchy, cls.parent==None)
        else:
            ## 本当はこちらは存在しないはず。
            ## request.siteはまだ未実装。
            return cls.query.filter(cls.hierarchy==hierarchy, cls.parent==None)


