# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship, join, backref, column_property, mapper, relation

import sqlahelper

session = sqlahelper.get_session()
Base = sqlahelper.get_base()
from ticketing.utils import StandardEnum

from ticketing.organizations.models import Organization
from ticketing.venues.models import SeatMasterL2
from ticketing.events.models import Account, Event

class BaseModel(object):
    updated_at  = Column(DateTime)
    created_at  = Column(DateTime)
    deleted_at  = Column(DateTime)
    status      = Column(Integer, default=1)

class PaymentMethodPlugin(BaseModel,Base):
    __tablename__ = 'PaymentMethodPlugin'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))

class DeliveryMethodPlugin(BaseModel,Base):
    __tablename__ = 'DeliveryMethodPlugin'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))

class PaymentMethod(BaseModel,Base):
    __tablename__ = 'PaymentMethod'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    fee = Column(DECIMAL)
    organization_id = Column(BigInteger, ForeignKey('Organization.id'))
    organization = relationship('Organization', uselist=False, backref='payment_method_list')
    payment_plugin_id = Column(BigInteger, ForeignKey('PaymentMethodPlugin.id'))
    payment_plugin = relationship('PaymentMethodPlugin', uselist=False)

class DeliveryMethod(BaseModel,Base):
    __tablename__ = 'DeliveryMethod'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    fee = Column(DECIMAL)
    organization_id = Column(BigInteger, ForeignKey('Organization.id'))
    organization = relationship('Organization', uselist=False , backref='delivery_method_list')
    delivery_plugin_id = Column(BigInteger, ForeignKey('DeliveryMethodPlugin.id'))
    delivery_plugin = relationship('DeliveryMethodPlugin', uselist=False)

class PaymentDeliveryMethodPair(BaseModel,Base):
    __tablename__ = 'PaymentDeliveryMethodPair'

    id = Column(BigInteger, primary_key=True)

    sales_segment_id = Column(BigInteger, ForeignKey('SalesSegment.id'))
    sales_segment = relationship('SalesSegment')

    payment_method_id = Column(BigInteger, ForeignKey('PaymentMethod.id'))
    payment_method = relationship('PaymentMethod')

    delivery_method_id = Column(BigInteger, ForeignKey('DeliveryMethod.id'))
    delivery_method = relationship('DeliveryMethod')

    transaction_fee = Column(DECIMAL)
    delivery_fee = Column(DECIMAL)

    discount = Column(DECIMAL)
    discount_unit = Column(Integer)
    discount_type = Column(Integer)

    start_at = Column(DateTime)
    end_at = Column(DateTime)

class SalesSegment(BaseModel,Base):
    __tablename__ = 'SalesSegment'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))

    sales_segment_set_id = Column(BigInteger, ForeignKey('SalesSegmentSet.id'), nullable=True)
    sales_segment_set = relationship('SalesSegmentSet', uselist=False)

    start_at = Column(DateTime)
    end_at = Column(DateTime)

class SalesSegmentSet(BaseModel,Base):
    __tablename__ = 'SalesSegmentSet'
    id = Column(BigInteger, primary_key=True)

    product_id = Column(BigInteger, ForeignKey('Product.id'), nullable=True)
    product = relationship('Product', uselist=False)

    event_id = Column(BigInteger, ForeignKey('Event.id'), nullable=True)
    event = relationship('Event', uselist=False)

buyer_condition_set_table =  Table('BuyerConditionSet', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('buyer_condition_id', BigInteger, ForeignKey('BuyerCondition.id')),
    Column('product_id', BigInteger, ForeignKey('Product.id'))
)

class BuyerCondition(BaseModel,Base):
    __tablename__ = 'BuyerCondition'
    id = Column(BigInteger, primary_key=True)

    member_ship_id = Column(BigInteger, ForeignKey('MemberShip.id'))
    member_ship   = relationship('MemberShip')
    '''
     Any Conditions.....
    '''

stock_reference_from_product_item_table =  Table('StockReferenceFromProductItem', Base.metadata,
    Column('product_id', BigInteger, ForeignKey('ProductItem.id')),
    Column('stock_id', BigInteger, ForeignKey('Stock.id'))
)

class ProductItem(BaseModel,Base):
    __tablename__ = 'ProductItem'
    id = Column(BigInteger, primary_key=True)
    item_type = Column(Integer)
    price = Column(BigInteger)

    product_id = Column(BigInteger, ForeignKey('Product.id'))
    performance_id = Column(BigInteger, ForeignKey('Performance.id'))

    stocks = relationship("Stock", secondary=stock_reference_from_product_item_table)

    def get_for_update(self):
        self.stock = Stock.get_for_update(self.performance_id, self.seat_type_id)
        if self.stock != None:
            self.seatStock = SeatStock.get_for_update(self.stock.id)
            return self.seatStock
        else:
            return None

class StockHolder(BaseModel,Base):
    __tablename__ = "StockHolder"
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))

    performance_id = Column(BigInteger, ForeignKey('Performance.id'))
    account_id = Column(BigInteger, ForeignKey('Account.id'))

    stocks = relationship('Stock', backref='stock_holder')

# stock based on quantity
class Stock(BaseModel,Base):
    __tablename__ = "Stock"
    id = Column(BigInteger, primary_key=True)
    quantity = Column(Integer)

    performance_id = Column(BigInteger, ForeignKey('Performance.id'))
    stock_folder_id = Column(BigInteger, ForeignKey('StockHolder.id'))

    seat_type_id = Column(BigInteger, ForeignKey('SeatType.id'))

    seat_stocks = relationship('SeatStock', backref='stock')

    @staticmethod
    def get_for_update(pid, stid):
        return session.query(Stock).with_lockmode("update").filter(Stock.performance_id==pid, Stock.seat_type_id==stid, Stock.quantity>0).first()

class SeatStatusEnum(StandardEnum):
    Vacant = 1
    InCart = 2
    Ordered = 3
    Confirmed = 4
    Shipped = 5
    Canceled = 6
    Reserved = 7

# stock based on phisical seat positions
class SeatStock(BaseModel,Base):
    __tablename__ = "SeatStock"
    id = Column(BigInteger, primary_key=True)
    sold = Column(Boolean) # sold or not

    stock_id = Column(BigInteger, ForeignKey('Stock.id'))
    seat = relationship('SeatMasterL2', uselist=False, backref="seat_stock") # 1:1

    @staticmethod
    def get_for_update(stock_id):
        return session.query(SeatStock).with_lockmode("update").filter(SeatStock.stock_id==stock_id, SeatStock.status==SeatStatusEnum.Vacant.v).first()

    # @TODO
    @staticmethod
    def get_group_seat(pid, stid, num):
        idx = 0
        con_num = 0
        grouping_ss = SeatMasterL2.get_grouping_seat_sets(pid, stid)
        for grouping_seats in grouping_ss:
            for i, gseat in enumerate(grouping_seats):
                if not gseat.sold:
                    if con_num == 0:
                        idx = i
                    con_num += 1
                    if con_num == num:
                        # @TODO return with locked status
                        return gseat[idx:idx+num]
                else:
                    con_num = 0
        return []


class Product(BaseModel,Base):
    __tablename__ = 'Product'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    price = Column(BigInteger)

    items = relationship('ProductItem', backref='product')

    @staticmethod
    def find(performance_id = None, event_id = None):
        query = session.query(Product)
        if performance_id:
            query.\
                join(Product.items).\
                filter(ProductItem.performance_id==performance_id)
        elif event_id:
            # todo
            pass
        return query.all()

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
            item.seatStock.status = SeatStatusEnum.Vacant.v
        session.flush()
        return True

    def put_in_cart(self):
        if self.get_for_update() == False:
            return False
        for item in self.items:
            item.stock.quantity -= 1
            item.seatStock.status = SeatStatusEnum.InCart.v
        session.flush()
        return True

    @staticmethod
    def get(product_id):
        return session.query(Product).filter(Product.id==product_id).first()


