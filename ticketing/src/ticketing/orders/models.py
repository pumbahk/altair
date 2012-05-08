
from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship, join, backref, column_property

import sqlahelper
session = sqlahelper.get_session()
Base = sqlahelper.get_base()

from ticketing.users.models import User
from ticketing.products.models import Product, ProductItem
from ticketing.venues.models import Seat

class ShippingAddress(Base):
    __tablename__ = 'ShippingAddress'
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("User.id"))
    user = relationship('User', backref='user_point')
    order_id = Column(BigInteger, ForeignKey("Order.id"))
    order = relationship('Order', backref='shipping_id')
    nick_name = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    first_name_kana = Column(String(255))
    last_name_kana = Column(String(255))
    birth_day = Column(DateTime)
    sex = Column(Integer)
    zip = Column(String(255))
    prefecture = Column(String(255))
    city = Column(String(255))
    street = Column(String(255))
    address = Column(String(255))
    other_address = Column(String(255))
    tel_1 = Column(String(32))
    tel_2 = Column(String(32))
    fax = Column(String(32))
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class Order(Base):
    __tablename__ = 'Order'
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("User.id"))
    user = relationship('User', uselist=False)

    items = relationship('OrderItem')
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class OrderItem(Base):
    __tablename__ = 'OrderItem'
    id = Column(BigInteger, primary_key=True)
    order_id = Column(BigInteger, ForeignKey("Order.id"))
    order = relationship('Order', backref='order_item')
    product_id = Column(BigInteger, ForeignKey("Product.id"))
    product = relationship('Product', uselist=False)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class AssignedProductItem(Base):
    __tablename__ = 'AssignedProductItem'
    id = Column(BigInteger, primary_key=True)
    order_id = Column(BigInteger, ForeignKey("Order.id"))
    order = relationship('Order')
    product_item_id = Column(BigInteger, ForeignKey("ProductItem.id"))
    product_item = relationship('ProductItem', uselist=False)
    seat = relationship('Seat', uselist=False)
    seat_id = Column(BigInteger, ForeignKey('Seat.id'))
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)
