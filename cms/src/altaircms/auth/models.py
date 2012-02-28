# coding: utf-8
from datetime import datetime
from sqlalchemy.orm import relationship

from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.schema import Table, Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import String, DateTime, Integer, Unicode

from altaircms.models import Base

DEFAULT_ROLE = 'administrator'

# CMS内で利用されるパーミッション一覧。view_configのpermission引数と合わせる
target_objects = ['event', 'topic', 'ticket', 'magazine', 'asset', 'page', 'tag', 'layout',]
PERMISSIONS = []
for t in target_objects:
    for act in ('create', 'read', 'update', 'delete'):
        PERMISSIONS.append('%s_%s' % (t, act))


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

    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    role_id = Column(Integer, ForeignKey("role.id"))
    client_id = Column(Integer, ForeignKey("client.id"))

    UniqueConstraint('auth_source', 'user_id')

    def __unicode__(self):
        return '%s' % self.user_id


class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)
    name = Column(String)


class RolePermission(Base):
    __tablename__ = 'role_permission'

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey('role.id'))
    permission = Column(String)

    UniqueConstraint('role', 'permission')


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
