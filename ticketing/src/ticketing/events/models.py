# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, DECIMAL, func
from sqlalchemy.orm import relationship, join, backref, column_property

from ticketing.utils import StandardEnum
from ticketing.models import Base, BaseModel, DBSession
from ticketing.products.models import Product, StockHolder
from ticketing.venues.models import Venue, VenueArea, Seat, SeatAttribute

class AccountTypeEnum(StandardEnum):
    Promoter    = 1
    Playguide   = 2
    User        = 3

class Account(BaseModel, Base):
    __tablename__ = "Account"
    id = Column(BigInteger, primary_key=True)
    account_type = Column(Integer)  # @see AccountTypeEnum
    name = Column(String(255))

    user_id = Column(BigInteger, ForeignKey("User.id"), nullable=True)
    user = relationship('User')

    organization_id = Column(BigInteger, ForeignKey("Organization.id"), nullable=True)
    organization = relationship('Organization', uselist=False)
    stock_holders = relationship('StockHolder', backref='account')

    @staticmethod
    def get_by_organization_id(id):
        return DBSession.query(Account).filter(Account.organization_id==id).all()

class Performance(BaseModel, Base):
    __tablename__ = 'Performance'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    code = Column(String(12))
    open_on = Column(DateTime)
    start_on = Column(DateTime)
    end_on = Column(DateTime)
    no_period = Column(Boolean)

    event_id = Column(BigInteger, ForeignKey('Event.id'))
    owner_id = Column(BigInteger, ForeignKey('Account.id'))

    stock_holders = relationship('StockHolder', backref='performance')
    product_items = relationship('ProductItem', backref='performance')
    stock_types = relationship('StockType', backref='performance')
    venue = relationship('Venue', uselist=False, backref='performance')

    @property
    def accounts(self):
        data = DBSession.query(Account).join(StockHolder)\
                .filter(StockHolder.performance_id==self.id)\
                .filter(StockHolder.account_id==Account.id)\
                .all()
        return data

    def add(self):
        BaseModel.add(self)

        """
        Performanceの作成時には, Venueとそれに紐づくVenueArea, Seat, SeatAttributeをコピーする
        """
        # create Venue
        if self.venue_id:
            original_venue = Venue.get(self.venue_id)
            venue = Venue.clone(original_venue)
            venue.original_venue_id = original_venue.id
            venue.performance_id = self.id
            venue.save()

            # create VenueArea
            if len(original_venue.areas) > 0:
                for original_area in original_venue.areas:
                    area = VenueArea.clone(original_area)
                    area.venue_id = venue.id
                    area.save()

            # create Seat
            if len(original_venue.seats) > 0:
                for original_seat in original_venue.seats:
                    seat = Seat.clone(original_seat)
                    seat.venue_id = venue.id
                    seat.stock_id = None
                    seat.save()

                    # create SeatAttribute
                    if len(original_seat.attributes) > 0:
                        for original_attribute in original_seat.attributes:
                            attribute = SeatAttribute.clone(original_attribute)
                            attribute.seat_id = seat.id
                            attribute.save()

class Event(BaseModel, Base):
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
        data = DBSession.query(func.min(SalesSegment.start_at)).join(Product)\
                .filter(Product.event_id==self.id).first()
        return data[0] if data else None

    @property
    def sales_end_on(self):
        data = DBSession.query(func.min(SalesSegment.end_at)).join(Product)\
                .filter(Product.event_id==self.id).first()
        return data[0] if data else None

    @property
    def start_performance(self):
        return DBSession.query(Performance).filter(Performance.event_id==self.id)\
                .order_by('Performance.start_on asc').first()

    @property
    def final_performance(self):
        return DBSession.query(Performance).filter(Performance.event_id==self.id)\
                .order_by('Performance.start_on desc').first()

    def get_accounts(self):
        return DBSession.query(Account.name).join(StockHolder).join(Performance)\
                .filter(Account.organization_id==self.organization_id)\
                .filter(Account.id==StockHolder.account_id)\
                .filter(StockHolder.performance_id==Performance.id)\
                .filter(Performance.event_id==self.id)\
                .distinct()


class SalesSegment(BaseModel, Base):
    __tablename__ = 'SalesSegment'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    start_at = Column(DateTime)
    end_at = Column(DateTime)

    event_id = Column(BigInteger, ForeignKey('Event.id'))
    event = relationship('Event', backref='sales_segments')


class PaymentDeliveryMethodPair(BaseModel, Base):
    __tablename__ = 'PaymentDeliveryMethodPair'
    id = Column(BigInteger, primary_key=True)
    transaction_fee = Column(DECIMAL)
    delivery_fee = Column(DECIMAL)
    discount = Column(DECIMAL)
    discount_unit = Column(Integer)
    discount_type = Column(Integer)

    sales_segment_id = Column(BigInteger, ForeignKey('SalesSegment.id'))
    sales_segment = relationship('SalesSegment', backref='payment_delivery_method_pair')
    payment_method_id = Column(BigInteger, ForeignKey('PaymentMethod.id'))
    payment_method = relationship('PaymentMethod')
    delivery_method_id = Column(BigInteger, ForeignKey('DeliveryMethod.id'))
    delivery_method = relationship('DeliveryMethod')

    @staticmethod
    def find(**kwargs):
        query = DBSession.query(PaymentDeliveryMethodPair)
        if 'sales_segment_id' in kwargs:
            query = query.filter_by(sales_segment_id=kwargs['sales_segment_id'])
        if 'payment_method_id' in kwargs:
            query = query.filter_by(payment_method_id=kwargs['payment_method_id'])
        if 'delivery_method_id' in kwargs:
            query = query.filter_by(delivery_method_id=kwargs['delivery_method_id'])
        return query.first()