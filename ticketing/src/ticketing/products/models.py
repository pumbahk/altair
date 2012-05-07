# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship, join, backref, column_property, mapper, relation

from ticketing.models import Base, BaseModel, DBSession, JSONEncodedDict, MutationDict
from ticketing.utils import StandardEnum
from ticketing.venues.models import Seat

class PaymentMethodPlugin(BaseModel, Base):
    __tablename__ = 'PaymentMethodPlugin'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))

class DeliveryMethodPlugin(BaseModel, Base):
    __tablename__ = 'DeliveryMethodPlugin'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))

class PaymentMethod(BaseModel, Base):
    __tablename__ = 'PaymentMethod'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    fee = Column(DECIMAL)

    organization_id = Column(BigInteger, ForeignKey('Organization.id'))
    organization = relationship('Organization', uselist=False, backref='payment_method_list')
    payment_plugin_id = Column(BigInteger, ForeignKey('PaymentMethodPlugin.id'))
    payment_plugin = relationship('PaymentMethodPlugin', uselist=False)

    @staticmethod
    def get_by_organization_id(id):
        return DBSession.query(PaymentMethod).filter(PaymentMethod.organization_id==id).all()

class DeliveryMethod(BaseModel, Base):
    __tablename__ = 'DeliveryMethod'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    fee = Column(DECIMAL)

    organization_id = Column(BigInteger, ForeignKey('Organization.id'))
    organization = relationship('Organization', uselist=False , backref='delivery_method_list')
    delivery_plugin_id = Column(BigInteger, ForeignKey('DeliveryMethodPlugin.id'))
    delivery_plugin = relationship('DeliveryMethodPlugin', uselist=False)

    @staticmethod
    def get_by_organization_id(id):
        return DBSession.query(DeliveryMethod).filter(DeliveryMethod.organization_id==id).all()

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
    def find(payment_method_id=None, delivery_method_id=None):
        return DBSession.query(PaymentDeliveryMethodPair)\
            .filter(PaymentDeliveryMethodPair.payment_method_id==payment_method_id)\
            .filter(PaymentDeliveryMethodPair.delivery_method_id==delivery_method_id)\
            .all()

class SalesSegment(BaseModel, Base):
    __tablename__ = 'SalesSegment'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    start_at = Column(DateTime)
    end_at = Column(DateTime)

    organization_id = Column(BigInteger, ForeignKey('Organization.id'))
    organization = relationship('Organization')

    @staticmethod
    def get_by_organization_id(id):
        return DBSession.query(SalesSegment).filter(SalesSegment.organization_id==id).all()

buyer_condition_set_table =  Table('BuyerConditionSet', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('buyer_condition_id', BigInteger, ForeignKey('BuyerCondition.id')),
    Column('product_id', BigInteger, ForeignKey('Product.id'))
)

class BuyerCondition(BaseModel, Base):
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

class ProductItem(BaseModel, Base):
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

class StockHolder(BaseModel, Base):
    __tablename__ = "StockHolder"
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))

    performance_id = Column(BigInteger, ForeignKey('Performance.id'))
    account_id = Column(BigInteger, ForeignKey('Account.id'))

    style = Column(MutationDict.as_mutable(JSONEncodedDict(1024)))

    stocks = relationship('Stock', backref='stock_holder')

# stock based on quantity
class Stock(BaseModel, Base):
    __tablename__ = "Stock"
    id = Column(BigInteger, primary_key=True)
    quantity = Column(Integer)

    performance_id = Column(BigInteger, ForeignKey('Performance.id'))
    stock_holder_id = Column(BigInteger, ForeignKey('StockHolder.id'))

    seat_type_id = Column(BigInteger, ForeignKey('SeatType.id'))

    seat_stocks = relationship('SeatStock', backref='stock')

    @staticmethod
    def get_for_update(pid, stid):
        return DBSession.query(Stock).with_lockmode("update").filter(Stock.performance_id==pid, Stock.seat_type_id==stid, Stock.quantity>0).first()

class SeatStatusEnum(StandardEnum):
    Vacant = 1
    InCart = 2
    Ordered = 3
    Confirmed = 4
    Shipped = 5
    Canceled = 6
    Reserved = 7

# stock based on phisical seat positions
class SeatStock(BaseModel, Base):
    __tablename__ = "SeatStock"
    id = Column(BigInteger, primary_key=True)
    sold = Column(Boolean) # sold or not

    stock_id = Column(BigInteger, ForeignKey('Stock.id'))
    seat = relationship('Seat', uselist=False, backref="seat_stock") # 1:1

    @staticmethod
    def get_for_update(stock_id):
        return DBSession.query(SeatStock).with_lockmode("update").filter(SeatStock.stock_id==stock_id, SeatStock.status==SeatStatusEnum.Vacant.v).first()

    # @TODO
    @staticmethod
    def get_group_seat(pid, stid, num):
        idx = 0
        con_num = 0
        grouping_ss = Seat.get_grouping_seat_sets(pid, stid)
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


class Product(BaseModel, Base):
    __tablename__ = 'Product'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    price = Column(BigInteger)

    sales_segment_id = Column(BigInteger, ForeignKey('SalesSegment.id'), nullable=True)
    sales_segment = relationship('SalesSegment', uselist=False, backref='product')

    event_id = Column(BigInteger, ForeignKey('Event.id'))
    event = relationship('Event', uselist=False, backref='product')

    items = relationship('ProductItem', backref='product')

    @staticmethod
    def find(performance_id = None, event_id = None):
        query = DBSession.query(Product)
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
        DBSession.flush()
        return True

    def put_in_cart(self):
        if self.get_for_update() == False:
            return False
        for item in self.items:
            item.stock.quantity -= 1
            item.seatStock.status = SeatStatusEnum.InCart.v
        DBSession.flush()
        return True
