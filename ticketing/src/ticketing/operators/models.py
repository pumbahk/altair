# -*- coding: utf-8 -*-

import hashlib

from sqlalchemy import Table, Column, BigInteger, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import join, column_property, mapper

from ticketing.utils import StandardEnum
from ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, DBSession, Identifier, relationship

class OperatorRole_Operator(Base):
    __tablename__   = 'OperatorRole_Operator'
    id = Column(Identifier, primary_key=True, nullable=False)
    operator_id = Column(Identifier, ForeignKey('Operator.id', ondelete='CASCADE'), index=True, nullable=False)
    operator_role_id = Column(Identifier, ForeignKey('OperatorRole.id', ondelete='CASCADE'), index=True, nullable=False)

class Permission(Base):
    __tablename__ = 'Permission'
    id = Column(Identifier, primary_key=True)
    operator_role_id = Column(Identifier, ForeignKey('OperatorRole.id'))
    operator_role = relationship('OperatorRole', uselist=False)
    category_name = Column(String(255), index=True)
    permit = Column(Integer)

    @staticmethod
    def all():
        return DBSession.query(Permission).all()

    @staticmethod
    def get_by_key(category_name):
        #return Permission.filter(Permission.category_name==category_name).first()
        return DBSession.query(Permission).filter(Permission.category_name == category_name).first()

    @staticmethod
    def list_in(category_names):
        #return Permission.filter(Permission.category_name.in_(category_names)).all()
        return DBSession.query(Permission)\
            .filter(Permission.category_name.in_(category_names)).all()

class OperatorRole(Base, BaseModel, WithTimestamp):
    __tablename__ = 'OperatorRole'
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    operators = relationship('Operator', secondary=OperatorRole_Operator.__table__)
    permissions = relationship('Permission')
    status = Column('status',Integer, default=1)

class OperatorActionHistoryTypeENum(StandardEnum):
    View      = 1
    Create    = 2
    Update    = 3
    Delete    = 4

class OperatorActionHistory(Base):
    __tablename__ = 'OperatorActionHistory'
    id = Column(Identifier, primary_key=True)
    operator_id = Column(Identifier, ForeignKey('Operator.id'))
    operator = relationship('Operator', uselist=False, backref='histories')
    function = Column(String(255))

class OperatorAuth(Base, BaseModel, WithTimestamp):
    __tablename__ = 'OperatorAuth'
    operator_id = Column(Identifier, ForeignKey('Operator.id'), primary_key=True, nullable=False)
    login_id = Column(String(32), unique=True)
    password = Column(String(32))
    auth_code = Column(String(32), nullable=True)
    access_token = Column(String(32), nullable=True)
    secret_key = Column(String(32), nullable=True)

class Operator(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Operator'
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    email = Column(String(255))
    organization_id = Column(Identifier, ForeignKey('Organization.id'))
    expire_at = Column(DateTime, nullable=True)
    status = Column(Integer, default=1)

    organization = relationship('Organization', uselist=False, backref='operators')
    roles = relationship('OperatorRole', secondary=OperatorRole_Operator.__table__)
    auth = relationship('OperatorAuth', uselist=False, backref='operator')

    @staticmethod
    def get_by_login_id(user_id):
        return Operator.filter().join(OperatorAuth)\
                .filter(OperatorAuth.login_id==user_id).first()

    @staticmethod
    def get_by_email(email):
        return Operator.filter_by(email=email).first()

    @staticmethod
    def login(login_id, password):
        operator = Operator.filter().join(OperatorAuth)\
                .filter(OperatorAuth.login_id==login_id)\
                .filter(OperatorAuth.password==hashlib.md5(password).hexdigest()).first()
        return operator

    def save(self):
        super(Operator, self).save()

        # create/update OperatorAuth
        operator_auth = OperatorAuth.filter_by(operator_id=self.id).first()
        if operator_auth:
            operator_auth.login_id = self.login_id
        else:
            operator_auth = OperatorAuth(
                operator_id=self.id,
                login_id=self.login_id,
                password=hashlib.md5(self.password).hexdigest()
            )
        operator_auth.save()

        # create/update OperatorRole
        if hasattr(self, 'role_ids'):
            DBSession.query(OperatorRole_Operator).filter_by(operator_id=self.id).delete('fetch')
            for role_id in self.role_ids:
                operator_role_assoc = OperatorRole_Operator(
                    operator_id=self.id,
                    operator_role_id=role_id
                )
                DBSession.add(operator_role_assoc)
