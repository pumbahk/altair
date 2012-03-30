
from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship, join, backref, column_property, mapper, relation

import sqlahelper
session = sqlahelper.get_session()
Base = sqlahelper.get_base()

from ticketing.venues.models import SeatMasterL2
from ticketing.events.models import Account, Event

class Price(Base):
    __tablename__ = 'Price'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    event_id = Column(BigInteger, ForeignKey('Event.id'))
    event = relationship('Event', uselist=False)
    price = Column(BigInteger)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class PaymentMethod(Base):
    __tablename__ = 'PaymentMethod'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    fee = Column(DECIMAL)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class DeliveryMethod(Base):
    __tablename__ = 'DeliveryMethod'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    fee = Column(DECIMAL)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class PaymentDeliveryMethodPair(Base):
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

    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class SalesSegment(Base):
    __tablename__ = 'SalesSegment'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))

    sales_segment_set_id = Column(BigInteger, ForeignKey('SalesSegmentSet.id'), nullable=True)
    sales_segment_set = relationship('SalesSegmentSet', uselist=False)

    start_at = Column(DateTime)
    end_at = Column(DateTime)

    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class SalesSegmentSet(Base):
    __tablename__ = 'SalesSegmentSet'
    id = Column(BigInteger, primary_key=True)

    product_id = Column(BigInteger, ForeignKey('Product.id'), nullable=True)
    product = relationship('Product', uselist=False)

    event_id = Column(BigInteger, ForeignKey('Event.id'), nullable=True)
    event = relationship('Event', uselist=False)

    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

buyer_condition_set_table =  Table('BuyerConditionSet', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('buyer_condition_id', BigInteger, ForeignKey('BuyerCondition.id')),
    Column('product_id', BigInteger, ForeignKey('Product.id'))
)

class BuyerCondition(Base):
    __tablename__ = 'BuyerCondition'
    id = Column(BigInteger, primary_key=True)

    member_ship_id = Column(BigInteger, ForeignKey('MemberShip.id'))
    member_ship   = relationship('MemberShip')
    '''
     Any Conditions.....
    '''
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class ProductItem(Base):
    __tablename__ = 'ProductItem'
    id = Column(BigInteger, primary_key=True)

    product_id = Column(BigInteger, ForeignKey('Product.id'))
    product = relationship('Product', uselist=False)

    price = Column(BigInteger)
    item_type = Column(Integer)

    performance_id = Column(BigInteger, ForeignKey('Performance.id'))
    performance = relationship('Performance', uselist=False)
    price_id = Column(BigInteger, ForeignKey('Price.id'))
    price = relationship('Price', uselist=False)
    seat_type_id = Column(BigInteger, ForeignKey('SeatType.id'))
    seat_type = relationship('SeatType', uselist=False)

    product_id = Column(BigInteger, ForeignKey('Product.id'))
    product = relationship('Product', uselist=False)

    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class StockHolder(Base):
    __tablename__ = "StockHolder"
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))

    performance_id = Column(BigInteger, ForeignKey('Performance.id'))
    performance = relationship('Performance', uselist=False)

    account_id = Column(BigInteger, ForeignKey('Account.id'))
    account = relationship('Account', uselist=False)

    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)


# stock based on quantity
class Stock(Base):
    __tablename__ = "Stock"
    id = Column(BigInteger, primary_key=True)

    performance_id = Column(BigInteger, ForeignKey('Performance.id'))
    performance = relationship('Performance', uselist=False)
    stock_folder_id = Column(BigInteger, ForeignKey('StockHolder.id'))
    stock_folder = relationship('StockHolder', uselist=False)

    seat_type_id = Column(BigInteger, ForeignKey('SeatType.id'))
    seat_type = relationship('SeatType', uselist=False)

    quantity = Column(Integer)

    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

    @staticmethod
    def get_for_update(pid, stid):
        return session.query(Stock).with_lockmode("update").filter(Stock.performance_id==pid, Stock.seat_type_id==stid).first()

# stock based on phisical seat positions
class SeatStock(Base):
    __tablename__ = "SeatStock"
    id = Column(BigInteger, primary_key=True)

    stock = Column(BigInteger, ForeignKey('Stock.id'))
    stock_id = relationship('Stock', uselist=False, backref="seatStocks")

    seat_id = Column(BigInteger, ForeignKey("SeatMasterL2.seat_id"))
    seat = relationship('SeatMasterL2', uselist=False, backref="seat_stock_id") # 1:1
    sold = Column(Boolean) # sold or not

    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

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


class Product(Base):
    __tablename__ = 'Product'
    id = Column(BigInteger, primary_key=True)

    name = Column(String(255))
    price = Column(BigInteger)



    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

    items = relationship('ProductItem')
