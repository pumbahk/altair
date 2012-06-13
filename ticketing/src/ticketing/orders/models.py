# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, Numeric, Unicode
from sqlalchemy.orm import join, backref, column_property

from ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, Identifier, relationship
from ticketing.core.models import Seat, Performance, Product, ProductItem
from ticketing.users.models import User

orders_seat_table = Table("orders_seat", Base.metadata,
    Column("seat_id", Identifier, ForeignKey("Seat.id")),
    Column("OrderedProductItem_id", Identifier, ForeignKey("OrderedProductItem.id")),
)


class ShippingAddress(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'ShippingAddress'
    id = Column(Identifier, primary_key=True)
    user_id = Column(Identifier, ForeignKey("User.id"))
    user = relationship('User', backref='shipping_addresses')
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

class Order(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Order'
    id = Column(Identifier, primary_key=True)
    user_id = Column(Identifier, ForeignKey("User.id"))
    user = relationship('User')
    shipping_address_id = Column(Identifier, ForeignKey("ShippingAddress.id"))
    shipping_address = relationship('ShippingAddress', backref='order')
    organization_id = Column(Identifier, ForeignKey("Organization.id"))
    ordered_from = relationship('Organization', backref='orders')

    items = relationship('OrderedProduct')
    total_amount = Column(Numeric(precision=16, scale=2), nullable=False)

    multicheckout_approval_no = Column(Unicode(255), doc=u"マルチ決済受領番号")

    @staticmethod
    def filter_by_performance_id(id):
        performance = Performance.get(id)
        if not performance:
            return None

        return Order.filter_by(organization_id=performance.event.organization_id)\
                             .join(Order.ordered_products)\
                             .join(OrderedProduct.ordered_product_items)\
                             .join(OrderedProductItem.product_item)\
                             .filter(ProductItem.performance_id==id)\
                             .distinct()

    @classmethod
    def create_from_cart(cls, cart):
        order = cls()
        order.total_amount = cart.total_amount
        for product in cart.products:
            ordered_product = OrderedProduct(
                order=order, product=product.product, price=product.product.price, quantity=product.quantity)
            for item in product.items:
                ordered_product_item = OrderedProductItem(
                    ordered_product=ordered_product, product_item=item.product_item, price=item.product_item.price,
                    seats=item.seats,
                )

        return order


class OrderedProduct(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'OrderedProduct'
    id = Column(Identifier, primary_key=True)
    order_id = Column(Identifier, ForeignKey("Order.id"))
    order = relationship('Order', backref='ordered_products')
    product_id = Column(Identifier, ForeignKey("Product.id"))
    product = relationship('Product')
    price = Column(Numeric(precision=16, scale=2), nullable=False)
    quantity = Column(Integer)

class OrderedProductItem(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'OrderedProductItem'
    id = Column(Identifier, primary_key=True)
    ordered_product_id = Column(Identifier, ForeignKey("OrderedProduct.id"))
    ordered_product = relationship('OrderedProduct', backref='ordered_product_items')
    product_item_id = Column(Identifier, ForeignKey("ProductItem.id"))
    product_item = relationship('ProductItem')
#    seat_id = Column(Identifier, ForeignKey('Seat.id'))
#    seat = relationship('Seat')
    seats = relationship("Seat", secondary=orders_seat_table)
    price = Column(Numeric(precision=16, scale=2), nullable=False)
