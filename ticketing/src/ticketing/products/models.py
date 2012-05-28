# -*- coding: utf-8 -*-

from math import floor

from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import relationship, join, backref, column_property, mapper, relation

from ticketing.utils import StandardEnum
from ticketing.models import Base, BaseModel, DBSession, JSONEncodedDict, MutationDict, WithTimestamp, LogicallyDeleted
from ticketing.venues.models import SeatStatusEnum, SeatStatus

class PaymentMethodPlugin(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'PaymentMethodPlugin'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))

class DeliveryMethodPlugin(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'DeliveryMethodPlugin'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))

class PaymentMethod(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'PaymentMethod'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    fee = Column(Numeric(precision=16, scale=2), nullable=False)

    organization_id = Column(BigInteger, ForeignKey('Organization.id'))
    organization = relationship('Organization', uselist=False, backref='payment_method_list')
    payment_plugin_id = Column(BigInteger, ForeignKey('PaymentMethodPlugin.id'))
    payment_plugin = relationship('PaymentMethodPlugin', uselist=False)

    @staticmethod
    def get_by_organization_id(id):
        return PaymentMethod.filter(PaymentMethod.organization_id==id).all()

class DeliveryMethod(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'DeliveryMethod'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    fee = Column(Numeric(precision=16, scale=2), nullable=False)

    organization_id = Column(BigInteger, ForeignKey('Organization.id'))
    organization = relationship('Organization', uselist=False , backref='delivery_method_list')
    delivery_plugin_id = Column(BigInteger, ForeignKey('DeliveryMethodPlugin.id'))
    delivery_plugin = relationship('DeliveryMethodPlugin', uselist=False)

    @staticmethod
    def get_by_organization_id(id):
        return DeliveryMethod.filter(DeliveryMethod.organization_id==id).all()

buyer_condition_set_table =  Table('BuyerConditionSet', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('buyer_condition_id', BigInteger, ForeignKey('BuyerCondition.id')),
    Column('product_id', BigInteger, ForeignKey('Product.id'))
)

class BuyerCondition(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'BuyerCondition'
    id = Column(BigInteger, primary_key=True)

    member_ship_id = Column(BigInteger, ForeignKey('MemberShip.id'))
    member_ship   = relationship('MemberShip')
    '''
     Any Conditions.....
    '''

class ProductItem(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'ProductItem'
    id = Column(BigInteger, primary_key=True)
    item_type = Column(Integer)
    price = Column(Numeric(precision=16, scale=2), nullable=False)

    product_id = Column(BigInteger, ForeignKey('Product.id'))
    performance_id = Column(BigInteger, ForeignKey('Performance.id'))

    stock_id = Column(BigInteger, ForeignKey('Stock.id'))
    stock = relationship("Stock", backref="product_items")

    stock_type_id = Column(BigInteger, ForeignKey('StockType.id'))
    stock_type = relationship('StockType', backref='product_items')

    quantity = Column(Integer, nullable=False, default=1, server_default='1')

    def get_for_update(self):
        self.stock = Stock.get_for_update(self.performance_id, self.stock_type_id)
        if self.stock != None:
            self.seatStatus = SeatStatus.get_for_update(self.stock.id)
            return self.seatStatus
        else:
            return None

class StockTypeEnum(StandardEnum):
    Seat = 0
    Other = 1

class StockType(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'StockType'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    type = Column(Integer)  # @see StockTypeEnum

    event_id = Column(BigInteger, ForeignKey("Event.id"))

    stocks = relationship('Stock', backref='stock_type')

    style = Column(MutationDict.as_mutable(JSONEncodedDict(1024)))

    @property
    def is_seat(self):
        return self.type == StockTypeEnum.Seat.v

    def num_seats(self, performance_id=None):
        query = DBSession.query(func.sum(StockAllocation.quantity)).filter_by(stock_type=self)
        if performance_id:
            query = query.filter_by(performance_id=performance_id)
        return query.scalar()

    def set_style(self, data):
        if self.is_seat:
            self.style = {
                'stroke':{
                    'color':data.get('stroke_color'),
                    'width':data.get('stroke_width'),
                    'pattern':data.get('stroke_patten'),
                },
                'fill':{
                    'color':data.get('fill_color'),
                    'type':data.get('fill_type'),
                    'image':data.get('fill_image'),
                },
            }
        else:
            self.style = {}

class StockAllocation(Base):
    __tablename__ = "StockAllocation"
    stock_type_id = Column(BigInteger, ForeignKey('StockType.id'), primary_key=True)
    performance_id = Column(BigInteger, ForeignKey('Performance.id'), primary_key=True)
    stock_type = relationship('StockType', uselist=False, backref='stock_allocations')
    performance = relationship('Performance', uselist=False)
    quantity = Column(Integer, nullable=False)

    def save(self):
        stock_allocation = DBSession.query(StockAllocation)\
            .filter_by(performance_id=self.performance_id)\
            .filter_by(stock_type_id=self.stock_type_id)\
            .first()

        if stock_allocation:
            DBSession.merge(self)
        else:
            DBSession.add(self)
        DBSession.flush()

class StockHolder(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "StockHolder"
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))

    performance_id = Column(BigInteger, ForeignKey('Performance.id'))
    account_id = Column(BigInteger, ForeignKey('Account.id'))

    style = Column(MutationDict.as_mutable(JSONEncodedDict(1024)))

    stocks = relationship('Stock', backref='stock_holder')

# stock based on quantity
class Stock(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "Stock"
    id = Column(BigInteger, primary_key=True)
    quantity = Column(Integer)

    stock_holder_id = Column(BigInteger, ForeignKey('StockHolder.id'))
    seats = relationship("Seat", backref='stock')

    stock_type_id = Column(BigInteger, ForeignKey('StockType.id'))

    stock_status = relationship("StockStatus", uselist=False, backref='stock')

    @staticmethod
    def get_for_update(pid, stid):
        return Stock.filter(Stock.performance_id==pid, Stock.stock_type_id==stid, Stock.quantity>0).with_lockmode("update").first()

# stock based on quantity
class StockStatus(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "StockStatus"
    stock_id = Column(BigInteger, ForeignKey('Stock.id'), primary_key=True)
    quantity = Column(Integer)

class Product(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Product'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    price = Column(Numeric(precision=16, scale=2), nullable=False)

    sales_segment_id = Column(BigInteger, ForeignKey('SalesSegment.id'), nullable=True)
    sales_segment = relationship('SalesSegment', uselist=False, backref='product')

    event_id = Column(BigInteger, ForeignKey('Event.id'))
    event = relationship('Event', backref='products')

    items = relationship('ProductItem', backref='product')

    @staticmethod
    def find(performance_id=None, event_id=None, sales_segment_id=None):
        query = Product.filter()
        if performance_id:
            query = query.join(Product.items).filter(ProductItem.performance_id==performance_id)
        if event_id:
            query = query.filter(Product.event_id==event_id)
        if sales_segment_id:
            query = query.filter(Product.sales_segment_id==sales_segment_id)
        return query.all()

    def items_by_performance_id(self, id):
        return ProductItem.filter_by(performance_id=id)\
                          .filter_by(product_id=self.id).all()

    def get_for_update(self):
        for item in self.items:
            if item.get_for_update() == None:
                return False
        return True

    def get_out_cart(self):
        if self.get_for_update() == False:
            return False
        for item in self.items:
            item.stock.quantity += 1
            item.seatStatus.status = SeatStatusEnum.Vacant.v
        DBSession.flush()
        return True

    def put_in_cart(self):
        if self.get_for_update() == False:
            return False
        for item in self.items:
            item.stock.quantity -= 1
            item.seatStatus.status = SeatStatusEnum.InCart.v
        DBSession.flush()
        return True

    def get_sync_data(self, performance_id):
        data = {
            'name':self.name,
            'seat_type':self.seat_type(performance_id),
            'price':floor(self.price),
        }
        return data

    def seat_type(self, performance_id):
        item = ProductItem.filter_by(performance_id=performance_id)\
                          .filter_by(product_id=self.id)\
                          .join(ProductItem.stock_type)\
                          .filter(StockType.type==StockTypeEnum.Seat.v).first()
        return item.stock_type.name if item else ''
