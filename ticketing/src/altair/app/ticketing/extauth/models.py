from datetime import datetime
from urlparse import urlparse
from zope.interface import implementer
from pyramid.threadlocal import get_current_request
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from altair.models import Identifier
from altair.models import MutableSpaceDelimitedList, SpaceDelimitedList
from altair.oauth.interfaces import IClient

Base = declarative_base()

class WithCreatedAt(object):
    @declared_attr
    def created_at(self):
        return sa.Column(sa.DateTime(), nullable=False, default=datetime.now, server_default=sa.text(u'CURRENT_TIMESTAMP()'))

class Organization(Base):
    __tablename__ = 'Organization'
    id = sa.Column(Identifier, autoincrement=True, primary_key=True, nullable=False)
    short_name = sa.Column(sa.Unicode(32), nullable=False)
    maximum_oauth_scope = sa.Column(MutableSpaceDelimitedList.as_mutable(SpaceDelimitedList(255)), nullable=False, default=u'')
    maximum_oauth_client_expiration_time = sa.Column(sa.Integer(), nullable=False, default=63072000)


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
    valid_since = sa.Column(sa.DateTime(), nullable=True)
    expire_at = sa.Column(sa.DateTime(), nullable=True)

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
            return self.redirect_uri == redirect_uri

    def validate_secret(self, secret):
        return self.client_secret == secret
