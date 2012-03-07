# coding: utf-8
from datetime import datetime
from sqlalchemy.orm import relationship, backref

from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.schema import Table, Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import String, DateTime, Integer, BigInteger, Unicode

from altaircms.models import Base

## 認証時初期ロール
DEFAULT_ROLE = 'administrator'

##
## CMS内で利用されるパーミッション一覧。view_configのpermission引数と合わせる
##
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
    """
    __tablename__ = 'operator'

    id = Column(Integer, primary_key=True)

    auth_source = Column(String, nullable=False)
    user_id = Column(Integer)
    screen_name = Column(Unicode)

    oauth_token = Column(String)
    oauth_token_secret = Column(String)

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

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey('role.id'))
    permission_id = Column(Integer, ForeignKey('permission.id'))

    role = relationship("Role", backref=backref("role2permission", order_by=id))
    permission = relationship("Permission", backref=backref("role2permission", order_by=id))

    UniqueConstraint('role_id', 'permission_id')


class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    permissions = relationship("Permission", secondary=RolePermission.__table__, backref='role')


class Permission(Base):
    __tablename__ = 'permission'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)


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


class APIKey(Base):
    __tablename__ = 'apikey'

    def generate_apikey(self):
        from uuid import uuid4
        import hashlib

        hash = hashlib.new('sha256', str(uuid4()))
        return hash.hexdigest()

    id = Column(Integer, primary_key=True)
    name = Column(String)
    apikey = Column(String, default=generate_apikey)
    client = relationship("Client", backref=backref("apikeys", order_by=id))
    client_id = Column(Integer, ForeignKey("client.id"))

    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())
