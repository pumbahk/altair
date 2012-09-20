# coding: utf-8

#raise Exception, __name__

from datetime import datetime
import sqlahelper
from sqlalchemy.orm import relationship, backref

from sqlalchemy.schema import Table, Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import String, DateTime, Integer, Unicode, Enum
from sqlalchemy.ext.associationproxy import association_proxy
from zope.deprecation import deprecation
from altaircms.models import WithOrganizationMixin
import hashlib

Base = sqlahelper.get_base()
_session = sqlahelper.get_session()

PERMISSIONS = [
    # event
    "event_create",
    "event_read",
    "event_update",
    "event_delete",
    # topic
    "topic_create",
    "topic_read",
    "topic_update",
    "topic_delete",
    # topcontent
    "topcontent_create",
    "topcontent_read",
    "topcontent_update",
    "topcontent_delete",
    # ticket
    "ticket_create",
    "ticket_read",
    "ticket_update",
    "ticket_delete",
    # magazine
    "magazine_create",
    "magazine_read",
    "magazine_update",
    "magazine_delete",
    # asset
    "asset_create",
    "asset_read",
    "asset_update",
    "asset_delete",
    # page
    "page_create",
    "page_read",
    "page_update",
    "page_delete",
    # tag
    "tag_create",
    "tag_read",
    "tag_update",
    "tag_delete",
    # tag
    "category_create",
    "category_read",
    "category_update",
    "category_delete",
    # tag
    "promotion_create",
    "promotion_read",
    "promotion_update",
    "promotion_delete",
    # tag
    "promotion_unit_create",
    "promotion_unit_read",
    "promotion_unit_update",
    "promotion_unit_delete",
    # performance
    "sale_create",
    "sale_read",
    "sale_update",
    "sale_delete",

    # performance
    "performance_create",
    "performance_read",
    "performance_update",
    "performance_delete",
    # layout
    "layout_create",
    "layout_read",
    "layout_update",
    "layout_delete",
    # operator
    "operator_create",
    "operator_read",
    "operator_update",
    "operator_delete",
    # hotword
    "hotword_create",
    "hotword_read",
    "hotword_update",
    "hotword_delete",
    # pagedefaultinfo
    "pagedefaultinfo_create",
    "pagedefaultinfo_read",
    "pagedefaultinfo_update",
    "pagedefaultinfo_delete",
]


## 認証時初期ロール
DEFAULT_ROLE = 'administrator'

##
## CMS内で利用されるパーミッション一覧。view_configのpermission引数と合わせる
##
class OAuthToken(Base):
    __tablename__ = 'oauth_token'
    query = _session.query_property()
    token = Column(String(255), primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)



operator_role = Table(
    "operator_role", Base.metadata,
    Column("operator_id", Integer, ForeignKey("operator.id")),
    Column("role_id", Integer, ForeignKey("role.id")),
)


class OperatorSelfAuth(Base):
    __tablename__ = "operator_selfauth"
    query = _session.query_property()    

    operator_id = Column(Integer, ForeignKey("operator.id"), primary_key=True)
    operator = relationship("Operator", uselist=False)
    password = Column(String(64))

    @classmethod
    def get_login_user(self, organization_id, name, password):
        password = hashlib.sha256(password).hexdigest()
        return Operator.query.filter(Operator.organization_id==organization_id, Operator.screen_name==name)\
            .filter(OperatorSelfAuth.password==password).first()

    @classmethod
    def bound_selfauth(cls, operator, password):
        password = hashlib.sha256(password).hexdigest()
        return cls(operator=operator, password=password)


class Operator(WithOrganizationMixin, Base):
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

    date_joined = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    roles = relationship("Role", backref=("operators"), secondary=operator_role, cascade='all')
    organization_id = Column(Integer, ForeignKey("organization.id"))

    # quick fix!
    @property
    def role(self):
        if self.roles:
            return self.roles[0]
    role = deprecation.deprecated(role, "role is no more, use `Operator.roles`")

    def has_permission(self, perm):
        for role in self.roles:
            if any(p == perm for p in role.permissions):
                return True
        return False

    UniqueConstraint('auth_source', 'user_id')

    def __unicode__(self):
        return '%s' % self.user_id


class Role(Base):
    __tablename__ = 'role'
    query = _session.query_property()

    id = Column(Integer, primary_key=True)
    name = Column(String(255))

    perms = relationship("RolePermission", backref="role")
    permissions = association_proxy("perms", "name",
        creator=lambda name: RolePermission(name=name))

class RolePermission(Base):
    __tablename__ = 'role_permissions'
    query = _session.query_property()
    
    id = Column(Integer, primary_key=True)
    name = Column(Enum(*PERMISSIONS))
    role_id = Column(Integer, ForeignKey('role.id'))


class Organization(Base):
    """
    所属組織
    """
    __tablename__ = 'organization'
    query = _session.query_property()

    id = Column(Integer, primary_key=True)
    backend_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    auth_source = Column(String(255)) ##nullable=False?
    name = Column(Unicode(255))
    prefecture = Column(Unicode(255))
    address = Column(Unicode(255))
    email = Column(String(255))
    contract_status = Column(Integer)

    operators = relationship("Operator", backref="organization")

    UniqueConstraint('auth_source', 'backend_id')

    def inthere(self, key="organization_id"):
        def transform(qs):
            return qs.filter_by(**{key: self.id})
        return transform

    @classmethod
    def get_or_create(cls, backend_id, source):
        obj = cls.query.filter_by(backend_id=backend_id, auth_source=source).first()
        if obj:
            return obj
        return cls(backend_id=backend_id, auth_source=source)
        

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

    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())
