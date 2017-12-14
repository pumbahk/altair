import sqlalchemy as sa

from altair.models import Identifier, WithTimestamp

from ..models import Base

class Role(Base, WithTimestamp):
    __tablename__ = 'Role'
    id = sa.Column(Identifier, autoincrement=True, primary_key=True, nullable=False)
    name = sa.Column(sa.Unicode(32), unique=True, nullable=False)
    verbose_name = sa.Column(sa.Unicode(128), nullable=False)
    active = sa.Column(sa.Boolean)

class Permission(Base):
    __tablename__ = 'Permission'
    id = sa.Column(Identifier, autoincrement=True, primary_key=True, nullable=False)
    role_id = sa.Column(Identifier, sa.ForeignKey('Role.id'), nullable=False)
    category_name = sa.Column(sa.Unicode(128), nullable=False)
    permit = sa.Column(sa.Integer)

    role = sa.orm.relationship('Role', backref='permissions')

class Operator(Base, WithTimestamp):
    __tablename__ = 'Operator'
    id = sa.Column(Identifier, autoincrement=True, primary_key=True, nullable=False)
    organization_id = sa.Column(Identifier, sa.ForeignKey('Organization.id'), nullable=False)
    auth_identifier = sa.Column(sa.Unicode(128), unique=True, nullable=False)
    auth_secret = sa.Column(sa.Unicode(128), nullable=True)
    role_id = sa.Column(Identifier, sa.ForeignKey('Role.id'), nullable=False)
    status = sa.Column(sa.Integer, default=0)

    organization = sa.orm.relationship('Organization', backref='operators')
    role = sa.orm.relationship('Role', backref='operators')

    @property
    def is_administrator(self):
        return self.role_id == 1

    @property
    def is_superoperator(self):
        return self.role_id == 2

    @property
    def is_first(self):
        return self.status == 0