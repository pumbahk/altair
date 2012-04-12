# coding: utf-8
from datetime import datetime
import sqlahelper
import sqlalchemy.orm as orm
from sqlalchemy import (Column, Integer, Unicode, String, ForeignKey, DateTime)
from sqlalchemy.orm import relationship


class BaseOriginalMixin(object):
    def to_dict(self):
        from sqlalchemy.sql.operators import ColumnOperators
        return {k: getattr(self, k) for k, v in self.__class__.__dict__.iteritems() \
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
from altaircms.event.models import Event
class Performance(BaseOriginalMixin, Base):
    """
    パフォーマンス
    """
    __tablename__ = "performance"
    query = DBSession.query_property()

    id = Column(Integer, primary_key=True)
    backend_performance_id = Column(Integer, nullable=False)
    event_id = Column(Integer, ForeignKey('event.id'))
    client_id = Column(Integer, ForeignKey("client.id"))

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    title = Column(Unicode)
    venue = Column(Unicode) #開催地
    open_on = Column(DateTime)  # 開場
    start_on = Column(DateTime)  # 開始
    close_on = Column(DateTime)  # 終了

    # sale = relationship("Sale", backref=orm.backref("performances", order_by=id))
    event = relationship("Event", backref=orm.backref("performances", order_by=start_on))
    # client = relationship("Client", backref=orm.backref("performances", order_by=id))


class Sale(BaseOriginalMixin, Base):
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
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())
    price = Column(Integer, default=0)

    sale = relationship("Sale", backref=orm.backref("tickets", order_by=orderno))
    event = relationship("Event", backref=orm.backref("tickets", order_by=orderno))

    client_id = Column(Integer, ForeignKey("performance.id"))
    seattype = Column(Unicode(255))


class Seatfigure(BaseOriginalMixin, Base):
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




class Site(BaseOriginalMixin, Base):
    __tablename__ = "site"
    query = DBSession.query_property()

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    name = Column(Unicode)
    description = Column(Unicode)
    url = Column(String)

    client_id = Column(Integer, ForeignKey("client.id")) #@TODO: サイトにくっつけるべき？
