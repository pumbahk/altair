import sqlalchemy as sa
from sqlalchemy import orm
from ..models import Base
from altair.models import Identifier, WithTimestamp

class Role(Base, WithTimestamp):
    __tablename__ = 'Role'
    id = sa.Column(Identifier, autoincrement=True, primary_key=True, nullable=False)
    name = sa.Column(sa.Unicode(128), unique=True, nullable=False)
    active = sa.Column(sa.Boolean)

class Permission(Base):
    __tablename__ = 'Permission'
    id = sa.Column(Identifier, autoincrement=True, primary_key=True, nullable=False)
    role_id = sa.Column(Identifier, sa.ForeignKey('Role.id'), nullable=False)
    category_name = sa.Column(sa.Unicode(128), nullable=False)
    permit = sa.Column(sa.Integer)

    role = orm.relationship('Role', backref='permissions')

class Operator(Base, WithTimestamp):
    __tablename__ = 'Operator'
    id = sa.Column(Identifier, autoincrement=True, primary_key=True, nullable=False)
    organization_id = sa.Column(Identifier, sa.ForeignKey('Organization.id'), nullable=False)
    auth_identifier = sa.Column(sa.Unicode(128), unique=True, nullable=False)
    auth_secret = sa.Column(sa.Unicode(128), nullable=True)
    role_id = sa.Column(Identifier, sa.ForeignKey('Role.id'), nullable=False)

    organization = orm.relationship('Organization', backref='operators')
    role = orm.relationship('Role', backref='operators')