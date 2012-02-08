# coding: utf-8
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship
from zope.sqlalchemy import ZopeTransactionExtension

import sqlahelper
import transaction

DBSession = sqlahelper.get_session()
Base = declarative_base()



def populate():
    session = DBSession()
    session.flush()
    transaction.commit()


def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
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

    @TODO: 席図、席種、券種をくっつける
    """
    __tablename__ = "event"

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

    def __repr__(self):
        return '<Event %s>' % self.title

    def __unicode__(self):
        return self.title

    def __html__(self):
        return self.title


class ClientMixin(object):
    @declared_attr
    def client_id(self):
        Column(Integer, ForeignKey("client.id")) # ForeignKeyはdeclared_attrにしないといかん

    @declared_attr
    def client(self):
        relationship("Client")


class Performance(Base):
    """
    パフォーマンス
    """
    __tablename__ = "performance"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    title = Column(Unicode)
    performance_open = Column(DateTime)
    performance_close = Column(DateTime)

    client_id = Column(Integer, ForeignKey("event.id"))


class Seatfigure(Base):
    """
    席図
    """
    __tablename__ = "seatfigure"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    figure_url = Column(String)
    controller_url = Column(String)

    client_id = Column(Integer, ForeignKey("event.id"))

class Seattype(Base):
    """
    席種
    """
    __tablename__ = "seattype"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    client_id = Column(Integer, ForeignKey("event.id"))


class Ticket(Base):
    """
    券種
    """
    __tablename__ = "ticket"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())
    price = Column(Integer, default=0)

    client_id = Column(Integer, ForeignKey("performance.id"))
    seattype_id = Column(Integer, ForeignKey("seattype.id"))


class Client(Base):
    """
    顧客マスタ
    """
    __tablename__ = 'client'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    name = Column(Unicode)
    prefecture = Column(Unicode)
    address = Column(Unicode)
    email = Column(String)
    contract_status = Column(Integer)

    operators = relationship("Operator", backref="client")
    sites = relationship("Site", backref="site")
    events = relationship("Event", backref="event")


class Operator(Base):
    """
    サイト管理者

    @TODO: OpenIDの認証情報を保持するカラムが必要かもしれない
    """
    __tablename__ = 'operator'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    client_id = Column(Integer, ForeignKey("client.id"))


class Permission(Base):
    __tablename__ = 'permission'

    id = Column(Integer, primary_key=True)
    operator_id = Column(Integer, ForeignKey('operator.id'))
    permission = Column(String)



class TopicType(Base):
    __tablename__ = 'topic_type'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())
    client_id = Column(Integer, ForeignKey('client.id'))

    type = Column(Integer)


class Topic(Base):
    __tablename__ = "topic"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    topic_type_id = Column(Integer, ForeignKey('topic_type.id'))
    title = Column(Unicode)
    text = Column(Unicode)

    is_public = Column(Integer, default=0)
    publish_at = Column(DateTime)


    site_id = Column(Integer, ForeignKey("site.id"))


class Site(Base):
    __tablename__ = "site"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    name = Column(Unicode)
    description = Column(Unicode)
    url = Column(String)

    client_id = Column(Integer, ForeignKey("client.id")) #@TODO: サイトにくっつけるべき？



