# -*- coding: utf-8 -*-

import isodate

from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import join, backref, column_property

from ticketing.utils import StandardEnum
from ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, Identifier, relationship
from ticketing.products.models import Product, ProductItem, StockHolder, Stock, StockAllocation
from ticketing.venues.models import Venue, VenueArea, VenueArea_group_l0_id, Seat, SeatAttribute

class AccountTypeEnum(StandardEnum):
    Promoter    = 1
    Playguide   = 2
    User        = 3

class Account(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "Account"
    id = Column(Identifier, primary_key=True)
    account_type = Column(Integer)  # @see AccountTypeEnum
    name = Column(String(255))

    user_id = Column(Identifier, ForeignKey("User.id"), nullable=True)
    user = relationship('User')

    organization_id = Column(Identifier, ForeignKey("Organization.id"), nullable=True)
    organization = relationship('Organization', uselist=False)
    stock_holders = relationship('StockHolder', backref='account')

    @staticmethod
    def get_by_organization_id(id):
        return Account.filter(Account.organization_id==id).all()

class Performance(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Performance'

    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    code = Column(String(12))
    open_on = Column(DateTime)
    start_on = Column(DateTime)
    end_on = Column(DateTime)
    no_period = Column(Boolean)

    event_id = Column(Identifier, ForeignKey('Event.id'))
    owner_id = Column(Identifier, ForeignKey('Account.id'))

    stock_holders = relationship('StockHolder', backref='performance')
    product_items = relationship('ProductItem', backref='performance')
    venue = relationship('Venue', uselist=False, backref='performance')

    @property
    def accounts(self):
        data = Account.filter().join(StockHolder)\
                .filter(StockHolder.performance_id==self.id)\
                .filter(StockHolder.account_id==Account.id)\
                .all()
        return data

    def add(self):
        BaseModel.add(self)

        if hasattr(self, 'original_id') and self.original_id:
            """
            Performanceのコピー時は以下のモデルをcloneする
              - StockHolder
                - Stock
                  - ProductItem
              - StockAllocation
            """
            template_performance = Performance.get(self.original_id)

            # create StockHolder - Stock - ProductItem
            for template_stock_holder in template_performance.stock_holders:
                StockHolder.create_from_template(template=template_stock_holder, performance_id=self.id)

            # create StockAllocation
            for template_stock_allocation in template_performance.stock_allocations:
                StockAllocation.create_from_template(template=template_stock_allocation, performance_id=self.id)
        else:
            """
            Performanceの作成時は以下のモデルを自動生成する
              - StockHolder (デフォルト枠)
            """
            account = Account.filter_by(organization_id=self.event.organization.id)\
                             .filter_by(user_id=self.event.organization.user_id).first()
            stock_holder = StockHolder(
                name=u'自社',
                performance_id=self.id,
                account_id=account.id,
                style=None,
            )
            stock_holder.save()

    def save(self):
        BaseModel.save(self)

        """
        Performanceの作成時は以下のモデルを自動生成する
        また更新時にVenueの変更があったら以下のモデルをdeleteする
          - Venue
            - VenueArea
            - Seat
              - SeatAttribute
        """
        # create Venue - VenueArea, Seat - SeatAttribute
        if hasattr(self, 'create_venue_id') and self.venue_id:
            template_venue = Venue.get(self.venue_id)
            Venue.create_from_template(template=template_venue, performance_id=self.id)

        # delete Venue - VenueArea, Seat - SeatAttribute
        if hasattr(self, 'delete_venue_id') and self.delete_venue_id:
            venue = Venue.get(self.delete_venue_id)
            venue.delete_cascade()

    def get_sync_data(self):
        start_on = isodate.datetime_isoformat(self.start_on) if self.start_on else ''
        end_on = isodate.datetime_isoformat(self.end_on) if self.end_on else ''
        data = {
            'id':self.id,
            'name':self.name,
            'venue':self.venue.name,
            'open_on':isodate.datetime_isoformat(self.open_on),
            'start_on':start_on,
            'end_on':end_on,
            'sales':[s.get_sync_data(self.id) for s in self.event.sales_segments],
            'deleted':'true' if self.deleted_at else 'false',
        }
        return data

class Event(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Event'

    id = Column(Identifier, primary_key=True)
    code = Column(String(12))
    title = Column(String(1024))
    abbreviated_title = Column(String(1024))
    start_on = Column(DateTime)
    end_on = Column(DateTime, nullable=True)

    account_id = Column(Identifier, ForeignKey('Account.id'))
    account = relationship('Account', backref='events')

    organization_id = Column(Identifier, ForeignKey('Organization.id'))
    organization = relationship('Organization', backref='events')

    performances = relationship('Performance', backref='event')
    stock_types = relationship('StockType', backref='event')

    @property
    def sales_start_on(self):
        return SalesSegment.filter().with_entities(func.min(SalesSegment.start_at)).join(Product)\
                .filter(Product.event_id==self.id).scalar()

    @property
    def sales_end_on(self):
        return SalesSegment.filter().with_entities(func.min(SalesSegment.end_at)).join(Product)\
                .filter(Product.event_id==self.id).scalar()

    @property
    def start_performance(self):
        return Performance.filter(Performance.event_id==self.id)\
                .order_by('Performance.start_on asc').first()

    @property
    def final_performance(self):
        return Performance.filter(Performance.event_id==self.id)\
                .order_by('Performance.start_on desc').first()

    @staticmethod
    def get_distributing(organization_id):
        return Event.filter().join(Event.account).filter(Account.organization_id==organization_id).all()

    @staticmethod
    def get_distributed(user_id):
        return Event.filter().join(Event.account).filter(Account.user_id==user_id).all()

    def get_accounts(self):
        return Account.filter().with_entities(Account.name).join(StockHolder).join(Performance)\
                .filter(Account.organization_id==self.organization_id)\
                .filter(Account.id==StockHolder.account_id)\
                .filter(StockHolder.performance_id==Performance.id)\
                .filter(Performance.event_id==self.id)\
                .distinct()

    def get_sync_data(self):
        start_on = isodate.datetime_isoformat(self.start_on) if self.start_on else ''
        end_on = isodate.datetime_isoformat(self.end_on) if self.end_on else ''
        performances = Performance.query.filter_by(event_id=self.id).all()
        data = {
            'id':self.id,
            'title':self.title,
            'subtitle':self.abbreviated_title,
            'start_on':start_on,
            'end_on':end_on,
            'performances':[p.get_sync_data() for p in performances],
            'deleted':'true' if self.deleted_at else 'false',
        }
        return data

    def add(self):
        super(Event, self).add()

        """
        Eventの作成時は以下のモデルがなければ自動生成する
          - Account (自社枠)
        """
        account = Account.filter_by(organization_id=self.organization.id)\
                         .filter_by(user_id=self.organization.user_id).first()
        if not account:
            account = Account(
                account_type=AccountTypeEnum.Playguide.v,
                name=u'自社',
                user_id=self.organization.user_id,
                organization_id=self.organization.id,
            )
            account.save()

class SalesSegment(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'SalesSegment'
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    start_at = Column(DateTime)
    end_at = Column(DateTime)
    upper_limit = Column(Integer)
    seat_choice = Column(Boolean, default=True)

    event_id = Column(Identifier, ForeignKey('Event.id'))
    event = relationship('Event', backref='sales_segments')

    def get_sync_data(self, performance_id):
        products = Product.find(performance_id=performance_id, sales_segment_id=self.id)
        if products:
            start_at = isodate.datetime_isoformat(self.start_at) if self.start_at else ''
            end_at = isodate.datetime_isoformat(self.end_at) if self.end_at else ''
            data = {
                'name':self.name,
                'start_on':start_at,
                'end_on':end_at,
                'tickets':[p.get_sync_data(performance_id) for p in products],
            }
            return data
        return {}

class PaymentDeliveryMethodPair(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'PaymentDeliveryMethodPair'
    id = Column(Identifier, primary_key=True)
    transaction_fee = Column(Numeric(precision=16, scale=2), nullable=False)
    delivery_fee = Column(Numeric(precision=16, scale=2), nullable=False)
    discount = Column(Numeric(precision=16, scale=2), nullable=False)
    discount_unit = Column(Integer)

    sales_segment_id = Column(Identifier, ForeignKey('SalesSegment.id'))
    sales_segment = relationship('SalesSegment', backref='payment_delivery_method_pairs')
    payment_method_id = Column(Identifier, ForeignKey('PaymentMethod.id'))
    payment_method = relationship('PaymentMethod')
    delivery_method_id = Column(Identifier, ForeignKey('DeliveryMethod.id'))
    delivery_method = relationship('DeliveryMethod')
