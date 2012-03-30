# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, BigInteger, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, join, column_property, mapper

from hashlib import md5

import sqlahelper

session = sqlahelper.get_session()
Base = sqlahelper.get_base()

from ticketing.clients.models import Client

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

class OperatorRole(Base):
    __tablename__ = 'OperatorRole'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    operators = relationship("Operator",
                    secondary=operator_role_association_table)
    permissions = relationship('Permission')
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column('status',Integer, default=1)

class OperatorActionHistory(Base):
    __tablename__ = 'OperatorActionHistory'
    id = Column(BigInteger, primary_key=True)
    function = Column(String(255))
    data = Column(String(1024))
    created_at = Column(DateTime)
    operator_id = Column(BigInteger, ForeignKey('Operator.id'))
    operator = relationship('Operator', uselist=False)

operator_table = Table(
    'Operator', Base.metadata,
    Column('id', BigInteger, primary_key=True),
    Column('name', String(255)),
    Column('email',String(255)),
    Column('client_id',BigInteger, ForeignKey('Client.id')),
    Column('expire_at',DateTime, nullable=True),
    Column('updated_at',DateTime),
    Column('created_at',DateTime),
    Column('status',Integer, default=1)
)
operator_auth_table = Table(
    'Operator_Auth', Base.metadata,
    Column('id', BigInteger, primary_key=True),
    Column('login_id', String(32), unique=True),
    Column('password', String(32)),
    Column('auth_code', String(32), nullable=True),
    Column('access_token', String(32), nullable=True),
    Column('secret_key', String(32), nullable=True),
)

class Operator(Base):
    __table__ = join(operator_table, operator_auth_table, operator_table.c.id == operator_auth_table.c.id)
    id = column_property(operator_table.c.id, operator_auth_table.c.id)
    client = relationship('Client',uselist=False)
    roles = relationship("OperatorRole",
        secondary=operator_role_association_table)

    @staticmethod
    def get_by_login_id(user_id):
        return session.query(Operator).filter(Operator.login_id == user_id).first()

    @staticmethod
    def login(login_id, password):
        operator = session.query(Operator)\
                .filter(Operator.login_id == login_id)\
                .filter(Operator.password == md5(password).hexdigest()).first()
        return operator
