# coding: utf-8
from datetime import datetime
import sqlahelper
from sqlalchemy.orm import relationship, backref

import mako
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.schema import Table, Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import String, DateTime, Integer, BigInteger, Unicode

from altaircms.models import Base
_session = sqlahelper.get_session()

## 認証時初期ロール
DEFAULT_ROLE = 'administrator'

##
## CMS内で利用されるパーミッション一覧。view_configのpermission引数と合わせる
##
class OAuthToken(Base):
    __tablename__ = 'oauth_token'
    query = _session.query_property()
    token = Column(String(255), primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    def __init__(self, oauth_token):
        self.token = oauth_token
        self.created_at = datetime.now()
        self.updated_at = datetime.now()


class Operator(Base):
    """
    サイト管理者
    """
    __tablename__ = 'operator'
    query = _session.query_property()

    id = Column(Integer, primary_key=True)

    auth_source = Column(String(255), nullable=False)
    user_id = Column(Integer)
    screen_name = Column(Unicode(255))

    oauth_token = Column(String(255))
    oauth_token_secret = Column(String(255))

    date_joined = Column(DateTime, default=datetime.now())
    last_login = Column(DateTime, default=datetime.now())
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    role = relationship("Role", backref=backref("operators", order_by=id))
    role_id = Column(Integer, ForeignKey("role.id"))
    client_id = Column(Integer, ForeignKey("client.id"))

    UniqueConstraint('auth_source', 'user_id')

    def __unicode__(self):
        return '%s' % self.user_id


class RolePermission(Base):
    __tablename__ = 'role2permission'
    query = _session.query_property()

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey('role.id'))
    permission_id = Column(Integer, ForeignKey('permission.id'))

    role = relationship("Role", backref=backref("role2permission", order_by=id))
    permission = relationship("Permission", backref=backref("role2permission", order_by=id))

    UniqueConstraint('role_id', 'permission_id')


class Role(Base):
    __tablename__ = 'role'
    query = _session.query_property()

    id = Column(Integer, primary_key=True)
    name = Column(String(255))

    permissions = relationship("Permission", secondary=RolePermission.__table__, backref='role')


class Permission(Base):
    __tablename__ = 'permission'
    query = _session.query_property()

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)


class Client(Base):
    """
    顧客マスタ
    """
    __tablename__ = 'client'
    query = _session.query_property()

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    name = Column(Unicode(255))
    prefecture = Column(Unicode(255))
    address = Column(Unicode(255))
    email = Column(String(255))
    contract_status = Column(Integer)

    operators = relationship("Operator", backref="client")
    sites = relationship("Site", backref="site")
    events = relationship("Event", backref="event")


class APIKey(Base):
    __tablename__ = 'apikey'
    query = _session.query_property()

    def generate_apikey(self):
        from uuid import uuid4
        import hashlib

        hash = hashlib.new('sha256', str(uuid4()))
        return hash.hexdigest()

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    apikey = Column(String(255), default=generate_apikey)
    client = relationship("Client", backref=backref("apikeys", order_by=id))
    client_id = Column(Integer, ForeignKey("client.id"))

    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())
