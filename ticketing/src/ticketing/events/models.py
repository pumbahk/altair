# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, DECIMAL, func
from sqlalchemy.orm import relationship, join, backref, column_property

from ticketing.utils import StandardEnum
from ticketing.models import Base, BaseModel
from ticketing.products.models import SalesSegment, SalesSegmentSet

import sqlahelper
session = sqlahelper.get_session()

class AccountTypeEnum(StandardEnum):
    Promoter    = 1
    Playguide   = 2
    User        = 3

class Account(Base, BaseModel):
    __tablename__ = "Account"
    id = Column(BigInteger, primary_key=True)
    account_type = Column(Integer)  # @see AccountTypeEnum
    name = Column(String(255))

    user_id = Column(BigInteger, ForeignKey("User.id"), nullable=True)
    user = relationship('User')

    organization_id = Column(BigInteger, ForeignKey("Organization.id"), nullable=True)
    organization = relationship('Organization', uselist=False)
    stock_holders = relationship('StockHolder', uselist=False, backref='account')

    @staticmethod
    def get(account_id):
        return session.query(Account).filter(Account.id == account_id).first()

'''

 Event & Performance

'''
class Performance(Base, BaseModel):
    __tablename__ = 'Performance'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    code = Column(String(12))
    open_on = Column(DateTime)
    start_on = Column(DateTime)
    end_on = Column(DateTime)
    no_period = Column(Boolean)

    event_id = Column(BigInteger, ForeignKey('Event.id'))
    venue_id = Column(BigInteger, ForeignKey('Venue.id'))
    owner_id = Column(BigInteger, ForeignKey('Account.id'))

    stock_holders = relationship('StockHolder', backref='performance')
    stocks = relationship('Stock', backref='performance')
    product_items = relationship('ProductItem', backref='performance')
    seat_types = relationship('SeatType', backref='performance')

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

class Event(Base, BaseModel):
    __tablename__ = 'Event'
    id = Column(BigInteger, primary_key=True)
    code = Column(String(12))
    title = Column(String(1024))
    abbreviated_title = Column(String(1024))
    start_on = Column(DateTime)
    end_on = Column(DateTime, nullable=True)

    organization_id = Column(BigInteger, ForeignKey('Organization.id'))
    organization = relationship('Organization', backref='events')

    performances = relationship('Performance', backref='event')

    @property
    def sales_start_on(self):
        data = session.query(func.min(SalesSegment.start_at)).join(SalesSegmentSet)\
                .filter(SalesSegmentSet.event_id==self.id).first()
        return data[0] if data else None

    @property
    def sales_end_on(self):
        data = session.query(func.min(SalesSegment.end_at)).join(SalesSegmentSet)\
                .filter(SalesSegmentSet.event_id==self.id).first()
        return data[0] if data else None

    @property
    def start_performance(self):
        return session.query(Performance).filter(Performance.event_id==self.id)\
                .order_by('Performance.start_on asc').first()

    @property
    def final_performance(self):
        return session.query(Performance).filter(Performance.event_id==self.id)\
                .order_by('Performance.start_on desc').first()
