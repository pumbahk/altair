# -*= coding:utf-8 -*-

import uuid
from uuid import uuid4
import hashlib
from datetime import datetime
import sqlahelper
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table, Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import String, DateTime, Integer, Unicode, Enum
from sqlalchemy.ext.associationproxy import association_proxy
from zope.deprecation import deprecation
from altaircms.models import WithOrganizationMixin, BaseOriginalMixin, DBSession


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

    def get_permission(self, perm):
        return RolePermission.query.filter(
            RolePermission.id==perm.id,
            RolePermission.role_id==Role.id,
            Role.id==operator_role.c.role_id,
            operator_role.c.operator_id==self.id,
            ).first()

    def get_permission_by_name(self, name):
        return RolePermission.query.filter(
            RolePermission.name==name,
            RolePermission.role_id==Role.id,
            Role.id==operator_role.c.role_id,
            operator_role.c.operator_id==self.id,
            ).first()

    def has_permission(self, perm):
        return bool(self.get_permission(perm))

    def has_permission_by_name(self, name):
        return bool(self.get_permission_by_name(name))

    UniqueConstraint('auth_source', 'user_id')

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


class Organization(BaseOriginalMixin, Base):
    """
    所属組織
    """
    __tablename__ = 'organization'
    query = _session.query_property()

    id = Column(Integer, primary_key=True)
    backend_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    auth_source = Column(String(255)) ##nullable=False?
    short_name = Column(String(32),index=True, nullable=False)
    code = Column(String(3))  # 2桁英字大文字のみ

    use_full_usersite = Column(sa.Boolean, default=False, nullable=False,
                               doc=u"これがtrueのときsmartphone, mobile用のviewや検索フォームなどの機能が有効になる"
    ) ## todo:細分化
    use_only_one_static_page_type = Column(sa.Boolean, default=True, nullable=False,
                                      doc=u"これがtrueのとき、smartphoneアクセスでもpcの静的ページを見に行く"
    ) ## todo:修正
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

class WithOrganizationMixin(object):
    organization_id = sa.Column(sa.Integer, index=True) ## need FK?(organization.id)

    @property
    def organization(self):
        if self.organization_id is None:
            return None
        return Organization.query.filter_by(id=self.organization_id)


class APIKey(Base):
    __tablename__ = 'apikey'
    query = _session.query_property()

    def generate_apikey(self):
        hash = hashlib.new('sha256', str(uuid4()))
        return hash.hexdigest()

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    apikey = Column(String(255), default=generate_apikey)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Host(BaseOriginalMixin, WithOrganizationMixin, Base):
    __tablename__ = 'host'

    query = DBSession.query_property()

    id = sa.Column(sa.Integer, primary_key=True)
    host_name = sa.Column(sa.Unicode(255), unique=True, index=True)
    cart_domain = sa.Column(sa.Unicode(255), unique=False, index=False)

class PageAccesskey(Base, WithOrganizationMixin):
    query = DBSession.query_property()
    __tablename__ = "page_accesskeys"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Unicode(255))
    page_id = sa.Column(sa.Integer, sa.ForeignKey("page.id"))
    page = orm.relationship("Page", backref=orm.backref("access_keys", cascade="all"))
    event_id = sa.Column(sa.Integer, sa.ForeignKey("event.id"))
    event = orm.relationship("Event", backref=orm.backref("access_keys", cascade="all"))
    operator_id = sa.Column(sa.Integer, sa.ForeignKey("operator.id"))
    operator = orm.relationship("Operator", backref=orm.backref("access_keys", cascade="all"))

    SCOPE_CANDIDATES = ("onepage", "onepage+cart", "usersite", "cart", "both")
    scope = sa.Column(sa.String(length=16), nullable=False, default="onepage")

    hashkey = sa.Column(sa.String(length=32), nullable=False)
    expiredate = sa.Column(sa.DateTime)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return "%r:%s %s" % (self.__class__, self.hashkey, self.expiredate)

    def default_gen_key(self):
        return uuid.uuid4().hex

    def sethashkey(self, genkey=None, key=None):
        if key:
            self.hashkey = key
        else:
            self.hashkey = (genkey or self.default_gen_key)()

    @property
    def keytype(self):
        if self.page_id:
            return "page"
        elif self.event_id:
            return "event"
        return "unknown"
