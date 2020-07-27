# -*- coding: utf-8 -*-

import hashlib

from sqlalchemy import Table, Column, BigInteger, Integer, String, DateTime, ForeignKey, Unicode, Boolean
from sqlalchemy.orm import join, column_property, mapper, joinedload
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.expression import or_
import sqlalchemy.orm as orm

from altair.app.ticketing.utils import StandardEnum
from altair.app.ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, DBSession, Identifier, relationship

import logging
logger = logging.getLogger(__name__)


class OperatorRole_Operator(Base):
    __tablename__   = 'OperatorRole_Operator'
    id = Column(Identifier, primary_key=True, nullable=False)
    operator_id = Column(Identifier, ForeignKey('Operator.id', ondelete='CASCADE'), index=True, nullable=False)
    operator_role_id = Column(Identifier, ForeignKey('OperatorRole.id', ondelete='CASCADE'), index=True, nullable=False)


class OperatorGroup_Event(Base):
    __tablename__ = 'OperatorGroup_Event'
    event_id = Column(Identifier, ForeignKey('Event.id', ondelete='CASCADE'), index=True, nullable=False)
    operator_group_id = Column(Identifier, ForeignKey('OperatorGroup.id', ondelete='CASCADE'), index=True,
                               nullable=False, primary_key=True)


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
        return DBSession.query(Permission).filter(Permission.category_name==category_name).first()

    @staticmethod
    def list_in(category_names):
        return DBSession.query(Permission)\
            .filter(Permission.category_name.in_(category_names)).all()


COMMON_DEFAULT_ROLES = ['administrator', 'superuser', 'operator', 'superoperator']

class OperatorRole(Base, BaseModel, WithTimestamp):
    __tablename__ = 'OperatorRole'
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    name_kana = Column(Unicode(255))
    operators = relationship('Operator', secondary=OperatorRole_Operator.__table__)
    permissions = relationship('Permission', cascade='all,delete-orphan')
    status = Column('status',Integer, default=1)
    organization_id = Column(Identifier, ForeignKey('Organization.id'), nullable=True)
    organization = relationship('Organization', uselist=False)

    @staticmethod
    def get(organization_id, id):
        return OperatorRole.query.filter(
            OperatorRole.id==id,
            OperatorRole.organization_id==organization_id
            ).first()

    @staticmethod
    def query_all(organization_id):
        return OperatorRole.query.filter(or_(
            OperatorRole.organization_id==None,
            OperatorRole.organization_id==organization_id
            ))

    @staticmethod
    def all(organization_id):
        return OperatorRole.query_all(organization_id).all()

    def is_editable(self):
        return self.name not in COMMON_DEFAULT_ROLES


class OperatorRouteGroup(Base, BaseModel, WithTimestamp):
    __tablename__ = 'OperatorRouteGroup'
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    routes = relationship('OperatorRoute')
    operators = relationship('Operator', backref='route_group', order_by='Operator.id')
    status = Column(Boolean, nullable=False, default=1)
    organization_id = Column(Identifier, ForeignKey('Organization.id'), nullable=False)
    organization = relationship('Organization', uselist=False)

    @staticmethod
    def get(id):
        return OperatorRouteGroup.query.filter(OperatorRouteGroup.id==id).first()

    @staticmethod
    def all(organization_id):
        return OperatorRouteGroup.query_all(organization_id).all()


class OperatorGroup(Base, BaseModel, WithTimestamp):
    __tablename__ = 'OperatorGroup'
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    operators = relationship('Operator', backref='group', order_by='Operator.id')
    organization_id = Column(Identifier, ForeignKey('Organization.id'), nullable=False)
    organization = relationship('Organization', uselist=False)

    @property
    def events(self):
        from ..core.models import Event
        return Event.query.join(OperatorGroup_Event, OperatorGroup_Event.event_id == Event.id).filter(
            OperatorGroup_Event.operator_group_id == self.id).all()


class OperatorRoute(Base, BaseModel, WithTimestamp):
    __tablename__ = 'OperatorRoute'
    id = Column(Identifier, primary_key=True)
    route_name = Column(String(255))
    operator_route_group_id = Column(Identifier, ForeignKey('OperatorRouteGroup.id'), nullable=False)
    operator_route_group = relationship("OperatorRouteGroup", backref=orm.backref("operator_routes", cascade="all"))


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
    id = Column(Identifier, primary_key=True, autoincrement=True, nullable=False)
    operator_id = Column(Identifier, ForeignKey('Operator.id'), nullable=False)
    login_id = Column(String(384), nullable=False, unique=True)
    password = Column(String(32))
    auth_code = Column(String(32), nullable=True)
    access_token = Column(String(32), nullable=True)
    secret_key = Column(String(32), nullable=True)

    @staticmethod
    def get_by_login_id(user_id):
        return  DBSession.query(OperatorAuth, include_deleted=True)\
                                        .filter(OperatorAuth.login_id==user_id).first()

def ensure_ascii(login_id):
    if isinstance(login_id, unicode):
        login_id = login_id.encode('ascii', errors='ignore')
    elif isinstance(login_id, (bytes, str)):
        login_id = login_id.decode('ascii', errors='ignore').encode('ascii')
    return login_id


class Operator(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Operator'
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    email = Column(String(255))
    organization_id = Column(Identifier, ForeignKey('Organization.id'))
    expire_at = Column(DateTime, nullable=True)
    status = Column(Integer, default=0)
    sales_search = Column(Boolean, nullable=False, default=0)
    hide = Column(Boolean, nullable=True, default=0)
    organization = relationship('Organization', uselist=False, backref='operators')
    roles = relationship('OperatorRole', secondary=OperatorRole_Operator.__table__)
    auth = relationship('OperatorAuth', uselist=False, backref='operator')
    operator_group_id = Column(Identifier, ForeignKey('OperatorGroup.id'))
    operator_route_group_id = Column(Identifier, ForeignKey('OperatorRouteGroup.id'))

    @staticmethod
    def get(organization_id, id):
        return Operator.query.filter(
            Operator.id==id,
            Operator.organization_id==organization_id
            ).first()

    @staticmethod
    def get_by_login_id(login_id):
        login_id = ensure_ascii(login_id)
        return Operator.query.join(OperatorAuth).filter(OperatorAuth.login_id==login_id)\
            .options(joinedload(Operator.auth), joinedload(Operator.roles)).first()

    @staticmethod
    def get_by_email(email):
        return Operator.filter_by(email=email).first()

    @staticmethod
    def login(login_id, password):
        login_id = ensure_ascii(login_id)
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

    def print_queue_entry_count(self):
        return DBSession.query(TicketPrintQueueEntry).filter_by(operator=self, processed_at=None).count()

    @property
    def is_superuser(self):
        return any(r.name == "superuser" for r in self.roles)

    @property
    def is_reservation(self):
        return any(r.name == "reservation" for r in self.roles)

    def is_member_of_organization(self, has_organization):
        if unicode(self.organization_id) != unicode(has_organization.organization_id):
            logger.warn("operator(id={id}). is not organization({short_name})'s operator.".format(id=self.id, short_name=has_organization.organization.short_name))
            return False
        return True

    @property
    def is_first(self):
        return self.status == 0

from ..core.models import TicketPrintQueueEntry
