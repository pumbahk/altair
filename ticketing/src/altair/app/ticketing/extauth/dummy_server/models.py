from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa
from sqlalchemy import orm
from pyramid.threadlocal import get_current_request

Base = declarative_base()

class EaglesUser(Base):
    __tablename__ = 'EaglesUser'
    id = sa.Column(sa.Integer(), primary_key=True, autoincrement=True)
    last_name = sa.Column(sa.Unicode(255), nullable=False)
    first_name = sa.Column(sa.Unicode(255), nullable=False)
    openid_claimed_id = sa.Column(sa.Unicode(255), nullable=True, unique=True)
    valid_memberships = orm.relationship(
        'EaglesMembership',
        primaryjoin=lambda: \
            sa.and_(
                EaglesMembership.user_id == EaglesUser.id,
                EaglesMembership.valid_since <= get_current_request().now,
                get_current_request().now < EaglesMembership.expire_at
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

    user = orm.relationship('EaglesUser', backref='memberships')
    kind = orm.relationship('EaglesMemberKind', backref='memberships')
