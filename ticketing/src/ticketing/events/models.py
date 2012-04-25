# -*- coding: utf-8 -*-

from datetime import datetime

from ticketing.utils import StandardEnum
from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship, join, backref, column_property

import sqlahelper
session = sqlahelper.get_session()
Base = sqlahelper.get_base()

from ticketing.users.models import User, MemberShip
from ticketing.master.models import BankAccount

class AccountTypeEnum(StandardEnum):
    Promoter    = 1
    Playguide   = 2
    User        = 3

class Account(Base):
    __tablename__ = "Account"

    id = Column(BigInteger, primary_key=True)

    # @see AccountTypeEnum
    account_type = Column(Integer)

    user_id         = Column(BigInteger, ForeignKey("User.id"), nullable=True)
    user            = relationship('User')

    client_id       = Column(BigInteger, ForeignKey("Client.id"), nullable=True)
    client          = relationship('Client', uselist=False)

    updated_at      = Column(DateTime, nullable=True)
    created_at      = Column(DateTime)
    status          = Column(Integer, default=1)

    @staticmethod
    def get(account_id):
        return session.query(Account).filter(Account.id == account_id).first()

'''

 Event & Performance

'''
class Performance(Base):
    __tablename__ = 'Performance'
    id = Column(BigInteger, primary_key=True)
    event_id = Column(BigInteger, ForeignKey('Event.id'))
    name = Column(String(255))
    code = Column(String(12))
    open_on = Column(DateTime)
    start_on = Column(DateTime)
    end_on = Column(DateTime)
    no_period = Column(Boolean)
    owner_id = Column(BigInteger, ForeignKey('Account.id'))
    owner = relationship('Account')
    venue_id = Column(BigInteger, ForeignKey('Venue.id'))
    venue = relationship('Venue')
    product_item = relationship('ProductItem')

    @staticmethod
    def get(performance_id):
        return session.query(Performance).filter(Performance.id == performance_id).first()

    @staticmethod
    def add(performance):
        session.add(performance)

    @staticmethod
    def update(performance):
        performance.updated_at = datetime.now()
        session.merge(performance)
        session.flush()

class Event(Base):
    __tablename__ = 'Event'
    id = Column(BigInteger, primary_key=True)
    code = Column(String(12))
    title = Column(String(1024))
    abbreviated_title = Column(String(1024))
    start_on = Column( DateTime, nullable=True)
    end_on = Column( DateTime, nullable=True)
    performances = relationship('Performance', backref='event')

    @staticmethod
    def get(event_id):
        return session.query(Event).filter(Event.id==event_id).first()

    @staticmethod
    def get_by_code(code):
        return session.query(Event).filter(Event.code==code).first()

    @staticmethod
    def add(event):
        session.add(event)

    @staticmethod
    def update(event):
        session.merge(event)
        session.flush()

    @staticmethod
    def delete(event):
        session.delete(event)

    @staticmethod
    def all():
        return session.query(Event).all()

