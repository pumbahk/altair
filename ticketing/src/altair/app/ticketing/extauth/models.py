from datetime import datetime
from urlparse import urlparse
from zope.interface import implementer
from pyramid.threadlocal import get_current_request
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.sql import functions as sqlf
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from altair.models import Identifier
from altair.models import MutableSpaceDelimitedList, SpaceDelimitedList, MutationDict, JSONEncodedDict
from altair.oauth.interfaces import IClient
from .utils import is_descendant_of

Base = declarative_base()

class WithCreatedAt(object):
    @declared_attr
    def created_at(self):
        return sa.Column(sa.DateTime(), nullable=False, default=datetime.now, server_default=sqlf.current_timestamp())


class Organization(Base):
    __tablename__ = 'Organization'
    id = sa.Column(Identifier, autoincrement=True, primary_key=True, nullable=False)
    short_name = sa.Column(sa.Unicode(32), nullable=False)
    canonical_host_name = sa.Column(sa.Unicode(128), sa.ForeignKey('Host.host_name', use_alter=True, name=u'Organization_ibfk_1'), nullable=True)
    maximum_oauth_scope = sa.Column(MutableSpaceDelimitedList.as_mutable(SpaceDelimitedList(255)), nullable=False, default=u'')
    invalidate_client_http_session_on_access_token_revocation = sa.Column(sa.Boolean(), nullable=False, default=False)
    emergency_exit_url = sa.Column(sa.Unicode(255), nullable=True, default=None)
    settings = sa.Column(MutationDict.as_mutable(JSONEncodedDict(2048)))
    default_host = orm.relationship(
        'Host',
        primaryjoin=lambda: (Organization.id == Host.organization_id) & (Organization.canonical_host_name == Host.host_name),
        foreign_keys=[canonical_host_name],
        uselist=False
        )
    fanclub_api_available = sa.Column(sa.Boolean(), nullable=False, default=False)
    fanclub_api_type = sa.Column(sa.Unicode(32), nullable=True, default=None)


class Host(Base):
    __tablename__ = 'Host'
    __table_args__ = (
        sa.PrimaryKeyConstraint('host_name', 'organization_id'),
        )
    host_name = sa.Column(sa.Unicode(128), nullable=False, primary_key=True)
    organization_id = sa.Column(Identifier, sa.ForeignKey('Organization.id'))


class MemberSet(Base):
    __tablename__ = 'MemberSet'
    __table_args__ = (
        sa.UniqueConstraint('organization_id', 'name'),
        )

    id = sa.Column(Identifier, autoincrement=True, primary_key=True, nullable=False)
    organization_id = sa.Column(Identifier, sa.ForeignKey('Organization.id'))
    name = sa.Column(sa.Unicode(32), nullable=False)
    display_name = sa.Column(sa.Unicode(255), nullable=False)
    applicable_subtype = sa.Column(sa.Unicode(32), nullable=True, index=True)
    use_password = sa.Column(sa.Boolean(), nullable=False, default=True)
    auth_identifier_field_name = sa.Column(sa.Unicode(255), nullable=True, default=u'')
    auth_secret_field_name = sa.Column(sa.Unicode(255), nullable=True, default=u'')
    organization = orm.relationship('Organization', backref='member_sets')


class Member(Base, WithCreatedAt):
    __tablename__ = 'Member'
    __table_args__ = (
        sa.UniqueConstraint('member_set_id', 'auth_identifier'),
        )

    id = sa.Column(Identifier, autoincrement=True, primary_key=True, nullable=False)
    name = sa.Column(sa.Unicode(255), nullable=False)
    member_set_id = sa.Column(Identifier, sa.ForeignKey('MemberSet.id'))
    auth_identifier = sa.Column(sa.Unicode(128), nullable=False)
    auth_secret = sa.Column(sa.Unicode(128), nullable=True)
    member_set = orm.relationship('MemberSet', backref='member_sets')
    enabled = sa.Column(sa.Boolean(), nullable=False, default=True)

    email = sa.Column(sa.Unicode(255), nullable=True)
    given_name = sa.Column(sa.Unicode(255), nullable=True)
    family_name = sa.Column(sa.Unicode(255), nullable=True)
    given_name_kana = sa.Column(sa.Unicode(255), nullable=True)
    family_name_kana = sa.Column(sa.Unicode(255), nullable=True)
    birthday = sa.Column(sa.Date(), nullable=True)
    gender = sa.Column(sa.Integer, nullable=True)
    country = sa.Column(sa.Unicode(64), nullable=True)
    zip = sa.Column(sa.Unicode(32), nullable=True)
    prefecture = sa.Column(sa.Unicode(128), nullable=True)
    city = sa.Column(sa.Unicode(255), nullable=True)
    address_1 = sa.Column(sa.Unicode(255), nullable=True)
    address_2 = sa.Column(sa.Unicode(255), nullable=True)
    tel_1 = sa.Column(sa.Unicode(32), nullable=True)
    tel_2 = sa.Column(sa.Unicode(32), nullable=True)

    def query_valid_memberships(self, now):
        return [
            membership
            for membership in self.memberships
            if (membership.valid_since is None or now >= membership.valid_since) and \
               (membership.expire_at is None or now < membership.expire_at) and \
               membership.enabled
            ]

    @property
    def valid_memberships(self):
        return self.query_valid_memberships(get_current_request().now)


class MemberKind(Base):
    __tablename__ = 'MemberKind'
    __table_args__ = (
        sa.UniqueConstraint('member_set_id', 'name'),
        )
    id = sa.Column(Identifier, autoincrement=True, primary_key=True, nullable=False)
    member_set_id = sa.Column(Identifier, sa.ForeignKey('MemberSet.id'))
    name = sa.Column(sa.Unicode(32), nullable=False)
    display_name = sa.Column(sa.Unicode(255), nullable=False)
    member_set = orm.relationship('MemberSet', backref='member_kinds')
    show_in_landing_page = sa.Column(sa.Boolean(), nullable=True, default=True)
    enable_guests = sa.Column(sa.Boolean(), nullable=True, default=False)


class Membership(Base, WithCreatedAt):
    __tablename__ = 'Membership'
    id = sa.Column(Identifier, autoincrement=True, primary_key=True, nullable=False)
    member_id = sa.Column(Identifier, sa.ForeignKey('Member.id', ondelete='CASCADE'), nullable=False)
    member_kind_id = sa.Column(Identifier, sa.ForeignKey('MemberKind.id', ondelete='CASCADE'), nullable=False)
    membership_identifier = sa.Column(sa.Unicode(64), nullable=True)
    valid_since = sa.Column(sa.DateTime(), nullable=True)
    expire_at = sa.Column(sa.DateTime(), nullable=True)
    enabled = sa.Column(sa.Boolean(), nullable=False, default=True)

    member = orm.relationship('Member', backref='memberships')
    member_kind = orm.relationship('MemberKind', backref='memberships')


@implementer(IClient)
class OAuthClient(Base, WithCreatedAt):
    __tablename__ = 'OAuthClient'
    id = sa.Column(Identifier, autoincrement=True, primary_key=True, nullable=False)
    organization_id = sa.Column(Identifier, sa.ForeignKey('Organization.id'))
    name = sa.Column(sa.Unicode(128), nullable=False, default=u'')
    client_id = sa.Column(sa.Unicode(128), unique=True, nullable=False)
    client_secret = sa.Column(sa.Unicode(128), nullable=False)
    authorized_scope = sa.Column(MutableSpaceDelimitedList.as_mutable(SpaceDelimitedList(255)), nullable=False, default=u'')
    redirect_uri = sa.Column(sa.Unicode(384), nullable=True)

    organization = orm.relationship(Organization, foreign_keys=[organization_id])

    def validate_redirect_uri(self, redirect_uri):
        try:
            parsed = urlparse(redirect_uri)
        except:
            return False
        if self.redirect_uri is None:
            if parsed.scheme not in ('http', 'https'):
                return False
            return True
        else:
            if self.redirect_uri == redirect_uri:
                return True
            try:
                parsed_ = urlparse(self.redirect_uri)
            except:
                return False
            return (parsed_.scheme == 'http' or parsed.scheme == parsed_.scheme) and \
                    parsed.netloc == parsed_.netloc and \
                    is_descendant_of(parsed.path, parsed_.path)

    def validate_secret(self, secret):
        return self.client_secret == secret


class OAuthServiceProvider(Base, WithCreatedAt):
    __tablename__ = 'OAuthServiceProvider'
    id = sa.Column(Identifier, autoincrement=True, primary_key=True, nullable=False)
    name = sa.Column(sa.Unicode(32), nullable=False)
    display_name = sa.Column(sa.Unicode(255), nullable=False)
    auth_type = sa.Column(sa.Unicode(64), nullable=False)
    endpoint_base = sa.Column(sa.Unicode(255), nullable=False)
    consumer_key = sa.Column(sa.Unicode(255), nullable=False)
    consumer_secret = sa.Column(sa.Unicode(255), nullable=False)
    scope = sa.Column(sa.Unicode(255), nullable=True, default=u'')
    organization_id = sa.Column(Identifier, sa.ForeignKey('Organization.id'))
    organization = orm.relationship('Organization', backref='oauth_service_provider')  # 1:1
