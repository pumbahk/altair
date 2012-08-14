# -*- coding:utf-8 -*-

from sqlalchemy import Table, Column, ForeignKey, ForeignKeyConstraint, Index, func
from sqlalchemy.types import Boolean, BigInteger, Integer, Float, String, Date, DateTime, Numeric, Unicode
from sqlalchemy.orm import join, backref
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy

from ..models import Base, BaseModel, WithTimestamp, LogicallyDeleted, Identifier, relationship, JSONEncodedDict, MutationDict
from ..orders.models import OrderedProductItem
from ..core.models import Seat, DeliveryMethod

class Ticket_TicketBundle(Base, BaseModel, LogicallyDeleted):
    __tablename__ = 'Ticket_TicketBundle'
    ticket_bundle_id = Column(Identifier, ForeignKey('TicketBundle.id'), primary_key=True)
    ticket_id = Column(Identifier, ForeignKey('Ticket.id'), primary_key=True)

class TicketFormat_DeliveryMethod(Base, BaseModel, LogicallyDeleted):
    __tablename__ = 'TicketFormat_DeliveryMethod'
    ticket_format_id = Column(Identifier, ForeignKey('TicketFormat.id'), primary_key=True)
    delivery_method_id = Column(Identifier, ForeignKey('DeliveryMethod.id'), primary_key=True)

class TicketFormat(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "TicketFormat"
    id = Column(Identifier, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    organization_id = Column(Identifier, ForeignKey('Organization.id'), nullable=True)
    organization = relationship('Organization', uselist=False, backref='ticket_formats')
    delivery_methods = relationship('DeliveryMethod', secondary=TicketFormat_DeliveryMethod.__table__, backref='ticket_formats')
    data = Column(MutationDict.as_mutable(JSONEncodedDict(65536)))

class Ticket(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """
    Ticket.event_idがNULLのものはマスターデータ。これを雛形として実際にeventとひもづけるTicketオブジェクトを作成する。
    """
    __tablename__ = "Ticket"
    id = Column(Identifier, primary_key=True)
    organization_id = Column(Identifier, ForeignKey('Organization.id'), nullable=True)
    organization = relationship('Organization', uselist=False, backref=backref('ticket_templates'))
    event_id = Column(Identifier, ForeignKey('Event.id', ondelete='CASCADE'), nullable=True)
    event = relationship('Event', uselist=False, backref='tickets')
    ticket_format_id = Column(Identifier, ForeignKey('TicketFormat.id'), nullable=False)
    ticket_format = relationship('TicketFormat', uselist=False, backref='tickets')
    name = Column(Unicode(255), nullable=False, default=u'')
    data = Column(MutationDict.as_mutable(JSONEncodedDict(65536)))

    @classmethod
    def templates_query(cls):
        return cls.filter_by(event_id=None)

    def create_event_bound(self, event):
        new_object = self.__class__.clone(self)
        new_object.event_id = event.id
        return new_object

class TicketBundleAttribute(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "TicketBundleAttribute" 
    ticket_bundle_id = Column(Identifier, ForeignKey('TicketBundle.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    name = Column(String(255), primary_key=True, nullable=False)
    value = Column(String(1023))

class TicketBundle(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "TicketBundle"
    id = Column(Identifier, primary_key=True)
    event_id = Column(Identifier, ForeignKey('Event.id', ondelete='CASCADE'))
    event = relationship('Event', uselist=False, backref='ticket_bundles')
    operator_id = Column(Identifier, ForeignKey('Operator.id'))
    operator = relationship('Operator', uselist=False)
    attributes_ = relationship("TicketBundleAttribute", backref='bundle', collection_class=attribute_mapped_collection('name'), cascade='all,delete-orphan')
    attributes = association_proxy('attributes_', 'value', creator=lambda k, v: SeatAttribute(name=k, value=v))
    tickets = relationship('Ticket', secondary=Ticket_TicketBundle.__table__, backref='bundles')
    product_items = relationship('ProductItem', backref='ticket_bundle')

class TicketPrintHistory(Base, BaseModel, WithTimestamp):
    __tablename__ = "TicketPrintHistory"
    id = Column(Identifier, primary_key=True, autoincrement=True, nullable=False)
    operator_id = Column(Identifier, ForeignKey('Operator.id'), nullable=True)
    ordered_product_item_id = Column(Identifier, ForeignKey('OrderedProductItem.id'), nullable=True)
    ordered_product_item = relationship('OrderedProductItem', backref='print_histories')
    seat_id = Column(Identifier, ForeignKey('Seat.id'), nullable=True)
    seat = relationship('Seat', backref='print_histories')
    ticket_bundle_id = Column(Identifier, ForeignKey('TicketBundle.id'), nullable=False)
