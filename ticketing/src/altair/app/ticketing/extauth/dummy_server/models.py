from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa
from sqlalchemy import orm
from pyramid.threadlocal import get_current_request
from datetime import datetime

Base = declarative_base()

class EaglesUser(Base):
    __tablename__ = 'EaglesUser'
    id = sa.Column(sa.Integer(), primary_key=True, autoincrement=True)
    name = sa.Column(sa.Unicode(255), nullable=False)
    member_no = sa.Column(sa.Unicode(255), nullable=False)
    openid_claimed_id = sa.Column(sa.Unicode(255), nullable=True, unique=True)
    related_at = sa.Column(sa.DateTime(), nullable=True)
    created_at = sa.Column(sa.DateTime(), nullable=True, default=datetime.now)
    valid_memberships = orm.relationship(
        'EaglesMembership',
        primaryjoin=lambda: \
            sa.and_(
                EaglesMembership.user_id == EaglesUser.id,
                sa.or_(EaglesMembership.valid_since == None,
                       EaglesMembership.valid_since <= get_current_request().now),
                sa.or_(EaglesMembership.expire_at == None,
                       get_current_request().now < EaglesMembership.expire_at)
                )
        )


class EaglesMemberKind(Base):
    __tablename__ = 'EaglesMemberKind'
    id = sa.Column(sa.Integer(), primary_key=True)
    name = sa.Column(sa.Unicode(255), unique=True, nullable=False)


class EaglesMembership(Base):
    __tablename__ = 'EaglesMembership'
    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True, nullable=False)
    membership_id = sa.Column(sa.Unicode(32), nullable=False)
    user_id = sa.Column(sa.Integer(), sa.ForeignKey('EaglesUser.id', ondelete='CASCADE'), nullable=False)
    kind_id = sa.Column(sa.Integer(), sa.ForeignKey('EaglesMemberKind.id', ondelete='CASCADE'), nullable=False)
    valid_since = sa.Column(sa.DateTime(), nullable=True)
    expire_at = sa.Column(sa.DateTime(), nullable=True)
    created_at = sa.Column(sa.DateTime(), nullable=True, default=datetime.now)

    user = orm.relationship('EaglesUser', backref='memberships')
    kind = orm.relationship('EaglesMemberKind', backref='memberships')

class VisselUser(Base):
    __tablename__ = 'VisselUser'
    id = sa.Column(sa.Integer(), primary_key=True, autoincrement=True)
    name = sa.Column(sa.Unicode(255), nullable=False)
    member_no = sa.Column(sa.Unicode(255), nullable=False)
    openid_claimed_id = sa.Column(sa.Unicode(255), nullable=True, unique=True)
    related_at = sa.Column(sa.DateTime(), nullable=True)
    created_at = sa.Column(sa.DateTime(), nullable=True, default=datetime.now)
    valid_memberships = orm.relationship(
        'VisselMembership',
        primaryjoin=lambda: \
            sa.and_(
                VisselMembership.user_id == VisselUser.id,
                sa.or_(VisselMembership.valid_since == None,
                       VisselMembership.valid_since <= get_current_request().now),
                sa.or_(VisselMembership.expire_at == None,
                       get_current_request().now < VisselMembership.expire_at)
                )
        )


class VisselMemberKind(Base):
    __tablename__ = 'VisselMemberKind'
    id = sa.Column(sa.Integer(), primary_key=True)
    name = sa.Column(sa.Unicode(255), unique=True, nullable=False)


class VisselMembership(Base):
    __tablename__ = 'VisselMembership'
    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True, nullable=False)
    membership_id = sa.Column(sa.Unicode(32), nullable=False)
    user_id = sa.Column(sa.Integer(), sa.ForeignKey('VisselUser.id', ondelete='CASCADE'), nullable=False)
    kind_id = sa.Column(sa.Integer(), sa.ForeignKey('VisselMemberKind.id', ondelete='CASCADE'), nullable=False)
    valid_since = sa.Column(sa.DateTime(), nullable=True)
    expire_at = sa.Column(sa.DateTime(), nullable=True)
    created_at = sa.Column(sa.DateTime(), nullable=True, default=datetime.now)

    user = orm.relationship('VisselUser', backref='memberships')
    kind = orm.relationship('VisselMemberKind', backref='memberships')
