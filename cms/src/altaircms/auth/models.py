# coding: utf-8
from datetime import datetime
from sqlalchemy.orm import relationship

from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.schema import Table, Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import String, DateTime, Integer, Unicode

from altaircms.models import Base


class OAuthToken(Base):
    __tablename__ = 'oauth_token'

    token = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    def __init__(self, oauth_token):
        self.token = oauth_token
        self.created_at = datetime.now()
        self.updated_at = datetime.now()


class Operator(Base):
    """
    サイト管理者

    @TODO: OpenIDの認証情報を保持するカラムが必要かもしれない
    """
    __tablename__ = 'operator'

    id = Column(Integer, primary_key=True)

    auth_source = Column(String, nullable=False)
    user_id = Column(Integer)

    oauth_token = Column(String)
    oauth_token_secret = Column(String)

    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    client_id = Column(Integer, ForeignKey("client.id"))

    UniqueConstraint('auth_source', 'user_id')


class Permission(Base):
    __tablename__ = 'permission'

    id = Column(Integer, primary_key=True)
    operator_id = Column(Integer, ForeignKey('operator.id'))
    permission = Column(String)


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
