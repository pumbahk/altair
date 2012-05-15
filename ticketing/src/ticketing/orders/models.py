
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
    first_name = Column(String(255))
    last_name = Column(String(255))
    first_name_kana = Column(String(255))
    last_name_kana = Column(String(255))
    zip = Column(String(255))
    prefecture = Column(String(255))
    city = Column(String(255))
    address_1 = Column(String(255))
    address_2 = Column(String(255))
    country = Column(String(255))
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
    shipping_address_id = Column(BigInteger, ForeignKey("ShippingAddress.id"))
    shipping_address = relationship('ShippingAddress', backref='order')

    items = relationship('OrderedProduct')
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class OrderedProduct(Base):
    __tablename__ = 'OrderedProduct'
    id = Column(BigInteger, primary_key=True)
    order_id = Column(BigInteger, ForeignKey("Order.id"))
    order = relationship('Order', backref='order_item')
    ordered_product_items = relationship('OrderedProductItem', backref='ordered_product')
    product_id = Column(BigInteger, ForeignKey("Product.id"))
    product = relationship('Product', uselist=False)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class OrderedProductItem(Base):
    __tablename__ = 'OrderedProductItem'
    id = Column(BigInteger, primary_key=True)
    ordered_product_id = Column(BigInteger, ForeignKey("OrderedProduct.id"))
    product_item_id = Column(BigInteger, ForeignKey("ProductItem.id"))
    product_item = relationship('ProductItem', uselist=False)
    seat = relationship('Seat', uselist=False)
    seat_id = Column(BigInteger, ForeignKey('Seat.id'))
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)
