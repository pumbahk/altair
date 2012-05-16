# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, DECIMAL, func
from sqlalchemy.orm import relationship, join, backref, column_property, mapper, relation

from ticketing.utils import StandardEnum
from ticketing.models import Base, BaseModel, DBSession, JSONEncodedDict, MutationDict
from ticketing.venues.models import  SeatStatusEnum, SeatStatus

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

class ProductItem(BaseModel, Base):
    __tablename__ = 'ProductItem'
    id = Column(BigInteger, primary_key=True)
    item_type = Column(Integer)
    price = Column(BigInteger)

    product_id = Column(BigInteger, ForeignKey('Product.id'))
    performance_id = Column(BigInteger, ForeignKey('Performance.id'))

    stock_id = Column(BigInteger, ForeignKey('Stock.id'))
    stock = relationship("Stock")

    stock_type_id = Column(BigInteger, ForeignKey('StockType.id'))
    stock_type = relationship('StockType', backref='product_items')

    def get_for_update(self):
        self.stock = Stock.get_for_update(self.performance_id, self.stock_type_id)
        if self.stock != None:
            self.seatStatus = SeatStatus.get_for_update(self.stock.id)
            return self.seatStatus
        else:
            return None

class StockTypeEnum(StandardEnum):
    Seat = 1
    Other = 2

class StockType(BaseModel, Base):
    __tablename__ = 'StockType'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    type = Column(Integer)  # @see StockTypeEnum

    event_id = Column(BigInteger, ForeignKey("Event.id"))

    stocks = relationship('Stock', backref='stock_type')

    style = Column(MutationDict.as_mutable(JSONEncodedDict(1024)))

    @property
    def num_seats(self):
        return DBSession.query(func.sum(Stock.quantity)).filter_by(stock_type=self).scalar()

    @property
    def is_seat(self):
        return self.type == StockTypeEnum.Seat.v

class StockAllocation(Base):
    __tablename__ = "StockAllocation"
    stock_type_id = Column(BigInteger, ForeignKey('StockType.id'), primary_key=True)
    performance_id = Column(BigInteger, ForeignKey('Performance.id'), primary_key=True)
    stock_type = relationship('StockType', uselist=False)
    performance = relationship('Performance', uselist=False)
    quantity = Column(Integer, nullable=False)

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

    stock_holder_id = Column(BigInteger, ForeignKey('StockHolder.id'))
    seats = relationship("Seat", backref='stock')

    stock_type_id = Column(BigInteger, ForeignKey('StockType.id'))

    stock_status = relationship("StockStatus", uselist=False, backref='stock')

    @staticmethod
    def get_for_update(pid, stid):
        return DBSession.query(Stock).with_lockmode("update").filter(Stock.performance_id==pid, Stock.stock_type_id==stid, Stock.quantity>0).first()

# stock based on quantity
class StockStatus(BaseModel, Base):
    __tablename__ = "StockStatus"
    stock_id = Column(BigInteger, ForeignKey('Stock.id'), primary_key=True)
    quantity = Column(Integer)

class Product(BaseModel, Base):
    __tablename__ = 'Product'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    price = Column(BigInteger)

    sales_segment_id = Column(BigInteger, ForeignKey('SalesSegment.id'), nullable=True)
    sales_segment = relationship('SalesSegment', uselist=False, backref='product')

    event_id = Column(BigInteger, ForeignKey('Event.id'))
    event = relationship('Event', backref='products')

    items = relationship('ProductItem', backref='product')

    @staticmethod
    def find(performance_id = None, event_id = None):
        query = DBSession.query(Product)
        if performance_id:
            query = query.\
                join(Product.items).\
                filter(ProductItem.performance_id==performance_id)
        elif event_id:
            # todo
            pass
        return query.all()

    def items_by_performance_id(self, id):
        return DBSession.query(ProductItem).\
            filter_by(performance_id=id).\
            filter_by(product_id=self.id).all()

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
