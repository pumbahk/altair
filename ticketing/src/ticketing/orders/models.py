# -*- coding: utf-8 -*-

import logging
from datetime import datetime

from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, Numeric, Unicode
from sqlalchemy.orm import join, backref, column_property

from ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, Identifier, relationship, DBSession
from ticketing.core.models import Seat, Performance, Product, ProductItem
from ticketing.users.models import User

logger = logging.getLogger(__name__)

orders_seat_table = Table("orders_seat", Base.metadata,
    Column("seat_id", Identifier, ForeignKey("Seat.id")),
    Column("OrderedProductItem_id", Identifier, ForeignKey("OrderedProductItem.id")),
)


class ShippingAddress(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'ShippingAddress'
    id = Column(Identifier, primary_key=True)
    user_id = Column(Identifier, ForeignKey("User.id"))
    user = relationship('User', backref='shipping_addresses')
    email = Column(String(255))
    nick_name = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    first_name_kana = Column(String(255))
    last_name_kana = Column(String(255))
    sex = Column(Integer)
    zip = Column(String(255))
    prefecture    = Column(String(64), nullable=False, default=u'')
    city = Column(String(255))
    street = Column(String(255))
    address = Column(String(255))
    other_address = Column(String(255))
    tel_1 = Column(String(32))
    tel_2 = Column(String(32))
    fax = Column(String(32))
    email = Column(String(255))

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
    system_fee = Column(Numeric(precision=16, scale=2), nullable=False)
    transaction_fee = Column(Numeric(precision=16, scale=2), nullable=False)
    delivery_fee = Column(Numeric(precision=16, scale=2), nullable=False)

    multicheckout_approval_no = Column(Unicode(255), doc=u"マルチ決済受領番号")

    payment_delivery_method_pair_id = Column(Identifier, ForeignKey("PaymentDeliveryMethodPair.id"))
    payment_delivery_pair = relationship("PaymentDeliveryMethodPair")

    paid_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    canceled_at = Column(DateTime, nullable=True)

    order_no = Column(String(255))

    performance_id = Column(Identifier, ForeignKey('Performance.id'))
    performance = relationship('Performance', backref="orders")

    @property
    def status(self):
        if self.canceled_at:
            return 'canceled'
        elif self.delivered_at:
            return 'delivered'
        elif self.paid_at:
            return 'paid'
        else:
            return 'ordered'

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
        order.order_no = str(cart.id)
        order.total_amount = cart.total_amount
        order.shipping_address = cart.shipping_address
        order.payment_delivery_pair = cart.payment_delivery_pair
        order.system_fee = cart.system_fee
        order.transaction_fee = cart.transaction_fee
        order.delivery_fee = cart.delivery_fee
        order.performance = cart.performance

        for product in cart.products:
            ordered_product = OrderedProduct(
                order=order, product=product.product, price=product.product.price, quantity=product.quantity)
            for item in product.items:
                ordered_product_item = OrderedProductItem(
                    ordered_product=ordered_product, product_item=item.product_item, price=item.product_item.price,
                    seats=item.seats,
                )

        return order

    def cancel(self, request):
        # 決済をキャンセル
        ppid = self.payment_delivery_pair.payment_method.payment_plugin_id
        if not ppid:
            return False

        if ppid == 1:  # クレジットカード決済
            # 売り上げキャンセル
            from ticketing.multicheckout import api as multi_checkout_api

            multi_checkout_result = multi_checkout_api.checkout_sales_cancel(request, self.order_no)
            DBSession.add(multi_checkout_result)

            self.multi_checkout_approval_no = multi_checkout_result.ApprovalNo

        elif ppid == 2:  # 楽天あんしん決済
            # ToDo
            pass
        elif ppid == 3:  # コンビニ決済 (セブンイレブン)
            from ticketing.sej.models import SejOrder
            from ticketing.sej.exceptions import SejServerError
            from ticketing.sej.payment import request_cancel_order

            sej_order = SejOrder.query.filter_by(order_id='%(#)012d' % {'#':self.id}).first()
            if sej_order and not sej_order.cancel_at:
                try:
                    request_cancel_order(
                        sej_order.order_id,
                        sej_order.billing_number,
                        sej_order.exchange_number,
                    )
                except SejServerError, e:
                    logger.error(u'コンビニ決済(セブンイレブン)のキャンセルに失敗しました。 %s' % e)
                    return False
        elif ppid == 4:  # 窓口支払
            pass

        self.canceled_at = datetime.now()
        self.save()

        return True

class OrderedProduct(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'OrderedProduct'
    id = Column(Identifier, primary_key=True)
    order_id = Column(Identifier, ForeignKey("Order.id"))
    order = relationship('Order', backref='ordered_products')
    product_id = Column(Identifier, ForeignKey("Product.id"))
    product = relationship('Product')
    price = Column(Numeric(precision=16, scale=2), nullable=False)
    quantity = Column(Integer)

    attributes      = relationship("OrderedProductAttribute", backref='ordered_product', cascade='save-update, merge')

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

class OrderedProductAttribute(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__   = "OrderedProductAttribute"
    ordered_product_id  = Column(Identifier, ForeignKey('OrderedProduct.id'), primary_key=True, nullable=False)
    name = Column(String(255), primary_key=True, nullable=False)
    value = Column(String(1023))
