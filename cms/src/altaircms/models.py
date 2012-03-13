# coding: utf-8
from datetime import datetime
import sqlalchemy.orm as orm
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import  declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from zope.sqlalchemy import ZopeTransactionExtension
import transaction

class BaseOriginalMixin(object):
    def to_dict(self):
        from sqlalchemy.sql.operators import ColumnOperators
        return {k: getattr(self, k) for k, v in self.__class__.__dict__.items() \
                    if isinstance(v, ColumnOperators)}

    def column_items(self):
        from sqlalchemy.sql.operators import ColumnOperators
        return [(k, v) for k, v in self.__class__.__dict__.items()\
                    if isinstance(v, ColumnOperators)]

    @classmethod
    def column_iters(cls, D):
        from sqlalchemy.sql.operators import ColumnOperators
        for k, v in cls.__dict__.items():
            if isinstance(v, ColumnOperators):
                yield k, D.get(k)

    @classmethod
    def from_dict(cls, D):
        instance = cls()
        items_fn = D.iteritems if hasattr(D, "iteritems") else D.items
        for k, v in items_fn():
            setattr(instance, k, v)
        return instance
    
Base = declarative_base(cls=BaseOriginalMixin)
DBSession = orm.scoped_session(orm.sessionmaker(extension=[ZopeTransactionExtension()]))


def populate():
    session = DBSession()
    session.flush()
    transaction.commit()


def initialize_sql(engine, dropall=False):
    Base.metadata.bind = engine
    DBSession.bind = engine
    if dropall:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    try:
        populate()
    except IntegrityError:
        transaction.abort()


###
### ここからCMS用モデル
###

class BaseMixin(object):
    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())


class Event(Base):
    """
    イベント

    @TODO: 席図をくっつける
    """
    __tablename__ = "event"
    query = DBSession.query_property()

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    title = Column(Unicode)
    subtitle = Column(Unicode)
    description = Column(Unicode)
    place = Column(Unicode)
    inquiry_for = Column(Unicode)
    event_open = Column(DateTime)
    event_close = Column(DateTime)
    deal_open = Column(DateTime)
    deal_close = Column(DateTime)

    is_searchable = Column(Integer, default=0)

    client_id = Column(Integer, ForeignKey("client.id"))

    def __unicode__(self):
        return self.title

    def __html__(self):
        return self.title


"""
このあたりevent/models.pyに移動した方が良い。
"""
class Performance(Base):
    """
    パフォーマンス
    """
    __tablename__ = "performance"
    query = DBSession.query_property()

    id = Column(Integer, primary_key=True)
    backend_performance_id = Column(Integer, nullable=False)
    event_id = Column(Integer, ForeignKey('event.id'))
    client_id = Column(Integer, ForeignKey("client.id"))

    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    title = Column(Unicode)
    venue = Column(Unicode) #開催地
    open_on = Column(DateTime)  # 開場
    start_on = Column(DateTime)  # 開始
    close_on = Column(DateTime)  # 終了

    # sale = relationship("Sale", backref=orm.backref("performances", order_by=id))
    event = relationship("Event", backref=orm.backref("performances", order_by=start_on))
    # client = relationship("Client", backref=orm.backref("performances", order_by=id))


class Sale(Base):
    __tablename__ = 'sale'
    query = DBSession.query_property()

    id = Column(Integer, primary_key=True)
    performance_id = Column(Integer, ForeignKey('performance.id'))
    performance = relationship("Performance", backref=orm.backref("sales", order_by=id))

    name = Column(String)
    start_on = Column(DateTime)
    close_on = Column(DateTime)


    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())


class Ticket(Base):
    """
    券種
    """
    __tablename__ = "ticket"
    query = DBSession.query_property()

    id = Column(Integer, primary_key=True)
    orderno = Column(Integer)
    sale_id = Column(Integer, ForeignKey("sale.id"))
    event_id = Column(Integer, ForeignKey("event.id"))
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())
    price = Column(Integer, default=0)

    sale = relationship("Sale", backref=orm.backref("tickets", order_by=orderno))
    event = relationship("Event", backref=orm.backref("tickets", order_by=orderno))

    client_id = Column(Integer, ForeignKey("performance.id"))
    seattype = Column(Unicode(255))


class Seatfigure(Base):
    """
    席図
    """
    __tablename__ = "seatfigure"
    query = DBSession.query_property()

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    figure_url = Column(String)
    controller_url = Column(String)

    client_id = Column(Integer, ForeignKey("event.id"))


class Topic(Base):
    """
    トピック
    """
    __tablename__ = "topic"
    query = DBSession.query_property()

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    client_id = Column(Integer, ForeignKey("client.id")) #?
    site_id = Column(Integer, ForeignKey("site.id"))    

    type = Column(String(255))
    title = Column(Unicode)
    text = Column(Unicode)
    is_public = Column(Integer, default=0) #?
    publish_at = Column(DateTime)





class Site(Base):
    __tablename__ = "site"
    query = DBSession.query_property()

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    name = Column(Unicode)
    description = Column(Unicode)
    url = Column(String)

    client_id = Column(Integer, ForeignKey("client.id")) #@TODO: サイトにくっつけるべき？
