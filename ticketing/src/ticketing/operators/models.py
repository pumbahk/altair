# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, BigInteger, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, join, column_property, mapper

from hashlib import md5

import sqlahelper

session = sqlahelper.get_session()
Base = sqlahelper.get_base()
from ticketing.utils import StandardEnum

from ticketing.organizations.models import Organization
from ticketing.models import WithTimestamp, LogicallyDeleted

operator_role_association_table = Table('OperatorRole_Operator', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('operator_role_id', BigInteger, ForeignKey('OperatorRole.id')),
    Column('operator_id', BigInteger, ForeignKey('Operator.id'))
)

class Permission(Base):
    __tablename__ = 'Permission'
    id = Column(BigInteger, primary_key=True)
    operator_role_id = Column(BigInteger, ForeignKey('OperatorRole.id'))
    operator_role = relationship('OperatorRole', uselist=False)
    category_name = Column(String(255), index=True)
    permit = Column(Integer)

    @staticmethod
    def all():
        return session.query(Permission).all()

    @staticmethod
    def get_by_key(category_name):
        return session.query(Permission).filter(Permission.category_name == category_name).first()

    @staticmethod
    def list_in(category_names):
        return session.query(Permission)\
            .filter(Permission.category_name.in_(category_names)).all()

class OperatorRole(Base, WithTimestamp):
    __tablename__ = 'OperatorRole'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    operators = relationship("Operator",
                    secondary=operator_role_association_table)
    permissions = relationship('Permission')
    status = Column('status',Integer, default=1)

    @staticmethod
    def all():
        return session.query(OperatorRole).all()

class OperatorActionHistoryTypeENum(StandardEnum):
    View      = 1
    Create    = 2
    Update    = 3
    Delete    = 4

class OperatorActionHistory(Base):
    __tablename__ = 'OperatorActionHistory'
    id = Column(BigInteger, primary_key=True)

    operator_id = Column(BigInteger, ForeignKey('Operator.id'))
    operator = relationship('Operator', uselist=False, backref='histories')
    function = Column(String(255))

class OperatorAuth(Base, WithTimestamp):
    __tablename__ = 'OperatorAuth'
    operator_id = Column(BigInteger, ForeignKey('Operator.id'), primary_key=True, nullable=False)
    login_id = Column(String(32), unique=True)
    password = Column(String(32))
    auth_code = Column(String(32), nullable=True)
    access_token = Column(String(32), nullable=True)
    secret_key = Column(String(32), nullable=True)

class Operator(Base, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Operator'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    email = Column(String(255))
    organization_id = Column(BigInteger, ForeignKey('Organization.id'))
    expire_at = Column(DateTime, nullable=True)
    status = Column(Integer, default=1)

    organization = relationship('Organization',uselist=False)
    roles = relationship('OperatorRole',
        secondary=operator_role_association_table)
    auth = relationship('OperatorAuth', uselist=False, backref='operator')

    @staticmethod
    def get_by_login_id(user_id):
        return session.query(Operator)\
                .join(OperatorAuth)\
                .filter(OperatorAuth.login_id == user_id).first()

    @staticmethod
    def login(login_id, password):
        operator = session.query(Operator)\
                .join(OperatorAuth)\
                .filter(OperatorAuth.login_id == login_id)\
                .filter(OperatorAuth.password == md5(password).hexdigest()).first()
        return operator

