# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship, join, backref, column_property

from ticketing.models import Base, BaseModel
from ticketing.users.models import User
from ticketing.products.models import Product, ProductItem
from ticketing.venues.models import Seat

class ShippingAddress(BaseModel, Base):
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

class Order(BaseModel, Base):
    __tablename__ = 'Order'
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("User.id"))
    user = relationship('User')
    shipping_address_id = Column(BigInteger, ForeignKey("ShippingAddress.id"))
    shipping_address = relationship('ShippingAddress', backref='order')
    organization_id = Column(BigInteger, ForeignKey("Organization.id"))
    ordered_from = relationship('Organization', backref='orders')

    items = relationship('OrderedProduct')
    total_amount = Column(Numeric(precision=16, scale=2), nullable=False)

class OrderedProduct(BaseModel, Base):
    __tablename__ = 'OrderedProduct'
    id = Column(BigInteger, primary_key=True)
    order_id = Column(BigInteger, ForeignKey("Order.id"))
    order = relationship('Order', backref='ordered_products')
    product_id = Column(BigInteger, ForeignKey("Product.id"))
    product = relationship('Product')
    price = Column(Numeric(precision=16, scale=2), nullable=False)

class OrderedProductItem(BaseModel, Base):
    __tablename__ = 'OrderedProductItem'
    id = Column(BigInteger, primary_key=True)
    ordered_product_id = Column(BigInteger, ForeignKey("OrderedProduct.id"))
    ordered_product = relationship('OrderedProduct', backref='ordered_product_items')
    product_item_id = Column(BigInteger, ForeignKey("ProductItem.id"))
    product_item = relationship('ProductItem')
    seat_id = Column(BigInteger, ForeignKey('Seat.id'))
    seat = relationship('Seat')
    price = Column(Numeric(precision=16, scale=2), nullable=False)
