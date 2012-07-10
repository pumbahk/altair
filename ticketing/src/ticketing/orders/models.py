# -*- coding: utf-8 -*-

import logging
from datetime import datetime

from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, Numeric, Unicode, or_, and_
from sqlalchemy.orm import join, backref, column_property
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.exc import NoResultFound

from ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, Identifier, relationship, DBSession, record_to_multidict
from ticketing.core.models import Seat, Performance, Product, ProductItem, PaymentMethod, DeliveryMethod
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
    country = Column(String(255))
    prefecture = Column(String(255), nullable=False, default=u'')
    city = Column(String(255), nullable=False, default=u'')
    address_1 = Column(String(255), nullable=False, default=u'')
    address_2 = Column(String(255))
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

    paid_at = Column(DateTime, nullable=True, default=None)
    delivered_at = Column(DateTime, nullable=True, default=None)
    canceled_at = Column(DateTime, nullable=True, default=None)

    order_no = Column(String(255))

    performance_id = Column(Identifier, ForeignKey('Performance.id'))
    performance = relationship('Performance', backref="orders")

    @property
    def status(self):
        if self.canceled_at:
            return 'refunded' if self.paid_at else 'canceled'
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
        # キャンセル済み、売上キャンセル済み、配送済みはキャンセルできない
        if self.status == 'canceled' or self.status == 'refunded' or self.status == 'delivered':
            return False

        # 入金済みなら決済をキャンセル
        elif self.status == 'paid':
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

        # 未入金ならキャンセル日付をセットするのみ
        elif self.status == 'ordered':
            pass

        self.canceled_at = datetime.now()
        self.save()

        return True

    def delivered(self):
        # 入金済みのみ配送済みにステータス変更できる
        if self.status == 'paid':
            self.delivered_at = datetime.now()
            self.save()
            return True
        else:
            return False

    @staticmethod
    def set_search_condition(query, form):
        condition = form.order_no.data
        if condition:
            query = query.filter(Order.order_no==condition)
        condition = form.ordered_from.data
        if condition:
            query = query.filter(Order.created_at>=condition)
        condition = form.ordered_to.data
        if condition:
            query = query.filter(Order.created_at<=condition)
        condition = form.payment_method.data
        if condition:
            query = query.join(Order.payment_delivery_pair)
            query = query.join(PaymentMethod)
            query = query.filter(PaymentMethod.payment_plugin_id.in_(condition))
        condition = form.delivery_method.data
        if condition:
            query = query.join(Order.payment_delivery_pair)
            query = query.join(DeliveryMethod)
            query = query.filter(DeliveryMethod.delivery_plugin_id.in_(condition))
        condition = form.status.data
        if condition:
            status_cond = []
            if 'refunded' in condition:
                status_cond.append(and_(Order.canceled_at!=None, Order.paid_at!=None))
            if 'canceled' in condition:
                status_cond.append(and_(Order.canceled_at!=None, Order.paid_at==None))
            if 'delivered' in condition:
                status_cond.append(and_(Order.canceled_at==None, Order.delivered_at!=None))
            if 'paid' in condition:
                status_cond.append(and_(Order.canceled_at==None, Order.paid_at!=None, Order.delivered_at==None))
            if 'ordered' in condition:
                status_cond.append(and_(Order.canceled_at==None, Order.paid_at==None, Order.delivered_at==None))
            if status_cond:
                query = query.filter(or_(*status_cond))
        return query

class OrderCSV(object):

    # csv header
    order_header = [
        'order_no',
        'status',
        'created_at',
        'paid_at',
        'delivered_at',
        'canceled_at',
        'total_amount',
        'transaction_fee',
        'delivery_fee',
        'system_fee',
        ]
    user_profile_header = [
        'last_name',
        'first_name',
        'last_name_kana',
        'first_name_kana',
        'nick_name',
        ]
    shipping_address_header = [
        'last_name',
        'first_name',
        'last_name_kana',
        'first_name_kana',
        'zip',
        'country',
        'prefecture',
        'city',
        'address_1',
        'address_2',
        'tel_1',
        'fax',
        ]
    other_header = [
        'payment',
        'delivery',
        'event',
        'venue',
        'start_on',
        ]
    product_header = [
        'name',
        'price',
        'quantity',
        ]

    def __init__(self, orders):
        # shipping_addressのヘッダーにはuser_profileのカラムと区別する為にprefix(shipping_)をつける
        self.header = self.order_header \
                    + self.user_profile_header \
                    + ['shipping_' + sa for sa in self.shipping_address_header] \
                    + self.other_header
        self.rows = [self._convert_to_csv(order) for order in orders]

    def _convert_to_csv(self, order):
        order_dict = record_to_multidict(order)
        order_dict.add('created_at', str(order.created_at))
        order_dict.add('status', order.status)
        order_list = [(column, order_dict.get(column)) for column in self.order_header]

        user_profile_dict = record_to_multidict(order.user.user_profile)
        user_profile_list = [(column, user_profile_dict.get(column)) for column in self.user_profile_header]

        shipping_address_dict = record_to_multidict(order.shipping_address)
        shipping_address_list = [('shipping_' + column, shipping_address_dict.get(column)) for column in self.shipping_address_header]

        other_list = [
            ('payment', order.payment_delivery_pair.payment_method.name),
            ('delivery', order.payment_delivery_pair.delivery_method.name),
            ('event', order.ordered_products[0].product.event.title),
            ('venue', order.ordered_products[0].ordered_product_items[0].product_item.performance.venue.name),
            ('start_on', order.ordered_products[0].ordered_product_items[0].product_item.performance.start_on),
        ]

        product_list = []
        for i, ordered_product in enumerate(order.ordered_products):
            for column in self.product_header:
                column_name = 'product_%s_%s' % (column, i)
                if not column_name in self.header:
                    self.header.append(column_name)
                if column == 'name':
                    product_list.append((column_name, ordered_product.product.name))
                if column == 'price':
                    product_list.append((column_name, ordered_product.price))
                if column == 'quantity':
                    product_list.append((column_name, ordered_product.quantity))

        # encoding
        row = dict(order_list + user_profile_list + shipping_address_list + other_list + product_list)
        for key, value in row.items():
            if value:
                if not isinstance(value, unicode):
                    value = unicode(value)
                value = value.encode('utf-8')
            else:
                value = ''
            row[key] = value

        return row

class OrderedProductAttribute(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__   = "OrderedProductAttribute"
    ordered_product_item_id  = Column(Identifier, ForeignKey('OrderedProductItem.id'), primary_key=True, nullable=False)
    ordered_product_item  = relationship("OrderedProductItem", backref='_attributes')
    name = Column(String(255), primary_key=True, nullable=False)
    value = Column(String(1023))

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

    def _get(self, name):
        for item in self.items():
            if item.name == name:
                return item

    def put(self, name, value):
        attr = self._get(name)
        if attr:
            attr.value = value
        else:
            attr = OrderedProductAttribute()
            attr.ordered_product = self
            attr.name = name
            attr.value = value
            DBSession.add(attr)

    def get(self,name):
        return self.get(name).value

    def items(self):
        return [(attr.name, attr.items) for attr in self._attributes]

