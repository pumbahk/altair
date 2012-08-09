# -*- coding: utf-8 -*-

import logging
from datetime import datetime

from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, Numeric, Unicode, or_, and_
from sqlalchemy.orm import join, backref, column_property
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.exc import NoResultFound
from pyramid.threadlocal import get_current_registry

from ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, Identifier, relationship, DBSession, record_to_multidict
from ticketing.utils import sensible_alnum_decode
from ticketing.core.models import Seat, Performance, Product, ProductItem, PaymentMethod, DeliveryMethod, StockStatus, SeatStatus, SeatStatusEnum
from ticketing.users.models import User
from ticketing.sej.models import SejOrder
from ticketing.sej.exceptions import SejServerError
from ticketing.sej.payment import request_cancel_order
from ticketing.cart.helpers import format_number as _format_number

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

    def cancel(self, request):
        # キャンセル済み、売上キャンセル済み、配送済みはキャンセルできない
        if self.status == 'canceled' or self.status == 'refunded' or self.status == 'delivered':
            return False

        '''
        決済方法ごとに払戻し処理
        '''
        ppid = self.payment_delivery_pair.payment_method.payment_plugin_id
        if not ppid:
            return False

        # クレジットカード決済
        if ppid == 1:
            # 入金済みなら決済をキャンセル
            if self.status == 'paid':
                # 売り上げキャンセル
                from ticketing.multicheckout import api as multi_checkout_api

                order_no = self.order_no
                if request.registry.settings.get('multicheckout.testing', False):
                    order_no = '%010d%02d' % (sensible_alnum_decode(order_no[2:12]), 0)
                multi_checkout_result = multi_checkout_api.checkout_sales_cancel(request, order_no)
                DBSession.add(multi_checkout_result)

                error_code = ''
                if multi_checkout_result.CmnErrorCd and multi_checkout_result.CmnErrorCd != '000000':
                    error_code = multi_checkout_result.CmnErrorCd
                elif multi_checkout_result.CardErrorCd and multi_checkout_result.CardErrorCd != '000000':
                    error_code = multi_checkout_result.CardErrorCd

                if error_code:
                    logger.error(u'クレジットカード決済のキャンセルに失敗しました。 %s' % error_code)
                    return False

                self.multi_checkout_approval_no = multi_checkout_result.ApprovalNo

        # 楽天あんしん決済
        elif ppid == 2:
            # ToDo
            pass

        # コンビニ決済 (セブンイレブン)
        elif ppid == 3:
            # 入金済みならキャンセル不可
            if self.status == 'paid':
                return False

            # 未入金ならコンビニ決済のキャンセル通知
            elif self.status == 'ordered':
                sej_order = SejOrder.query.filter_by(order_id=self.order_no).first()
                if sej_order and not sej_order.cancel_at:
                    settings = get_current_registry().settings
                    shop_id = settings.get('sej.shop_id', 0)
                    if sej_order.shop_id != shop_id:
                        logger.error(u'コンビニ決済(セブンイレブン)のキャンセルに失敗しました Invalid shop_id : %s' % shop_id)
                        return False

                    try:
                        request_cancel_order(
                            order_id=sej_order.order_id,
                            billing_number=sej_order.billing_number,
                            exchange_number=sej_order.exchange_number,
                            shop_id=shop_id,
                            secret_key=settings.get('sej.api_key'),
                            hostname=settings.get('sej.inticket_api_url')
                        )
                    except SejServerError, e:
                        logger.error(u'コンビニ決済(セブンイレブン)のキャンセルに失敗しました %s' % e)
                        return False

        # 窓口支払
        elif ppid == 4:
            pass

        # 在庫を戻す
        self.release()
        self.canceled_at = datetime.now()
        self.save()

        return True

    def release(self):
        # 在庫を解放する
        for product in self.ordered_products:
            product.release()

    def delivered(self):
        # 入金済みのみ配送済みにステータス変更できる
        if self.status == 'paid':
            self.delivered_at = datetime.now()
            self.save()
            return True
        else:
            return False

    @classmethod
    def create_from_cart(cls, cart):
        order = cls()
        order.order_no = cart.order_no
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

    @staticmethod
    def set_search_condition(query, form):
        sort = form.sort.data or 'id'
        direction = form.direction.data or 'desc'
        query = query.order_by('Order.' + sort + ' ' + direction)

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


def no_filter(value):
    return value

def format_number(value):
    return _format_number(float(value))

class OrderCSV(object):
    order_value_filters = dict((k, format_number) for k in ['transaction_fee', 'delivery_fee', 'system_fee', 'total_amount'])

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
        'sex',
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
        'tel_2',
        'fax',
        'email',
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
        'other',
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
        order_list = [(column, self.order_value_filters.get(column, no_filter)(order_dict.get(column))) for column in self.order_header]

        if order.user:
            user_profile_dict = record_to_multidict(order.user.user_profile)
            user_profile_list = [(column, user_profile_dict.get(column)) for column in self.user_profile_header]
        else:
            user_profile_list = []

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
                if column != 'other':
                    column_name = 'product_%s_%s' % (column, i)
                    if not column_name in self.header:
                        self.header.append(column_name)
                    if column == 'name':
                        product_list.append((column_name, ordered_product.product.name))
                    if column == 'price':
                        product_list.append((column_name, format_number(ordered_product.price)))
                    if column == 'quantity':
                        product_list.append((column_name, ordered_product.quantity))
                else:
                    for ordered_product_item in ordered_product.ordered_product_items:
                        for key, value in ordered_product_item.attributes.items():
                            if value and key in ['t_shirts_size', 'publicity', 'mail_permission', 'cont', 'old_id_number']:
                                column_name = '%s_%s' % (key, i)
                                if not column_name in self.header:
                                    self.header.append(column_name)

                                # for bj89ers
                                if key == 'mail_permission':
                                    value = '' if value is None else value
                                elif key == 'cont':
                                    value = u'新規' if value == 'no' else u'継続'

                                product_list.append((column_name, value))

        # encoding
        row = dict(order_list + user_profile_list + shipping_address_list + other_list + product_list)
        for key, value in row.items():
            if value:
                if not isinstance(value, unicode):
                    value = unicode(value)
                value = value.encode('cp932')
            else:
                value = ''
            row[key] = value

        return row

class OrderedProductAttribute(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__   = "OrderedProductAttribute"
    ordered_product_item_id  = Column(Identifier, ForeignKey('OrderedProductItem.id'), primary_key=True, nullable=False)
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

    def release(self):
        # 在庫を解放する
        for item in self.ordered_product_items:
            item.release()

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

    _attributes = relationship("OrderedProductAttribute", backref='ordered_product_item', collection_class=attribute_mapped_collection('name'), cascade='all,delete-orphan')
    attributes = association_proxy('_attributes', 'value', creator=lambda k, v: OrderedProductAttribute(name=k, value=v))

    @property
    def seat_statuses(self):
        """ 確保済の座席ステータス
        """
        return DBSession.query(SeatStatus).filter(SeatStatus.seat_id.in_([s.id for s in self.seats])).all()

    def release(self):
        # 座席開放
        for seat_status in self.seat_statuses:
            logger.debug('release seat id=%d' % (seat_status.seat_id))
            seat_status.status = int(SeatStatusEnum.Vacant)
        # 在庫数を戻す
        logger.debug('release stock id=%s quantity=%d' % (self.product_item.stock_id, self.product_item.quantity))
        query = StockStatus.__table__.update().values(
            {'quantity': StockStatus.quantity + self.product_item.quantity}
        ).where(StockStatus.stock_id==self.product_item.stock_id)
        DBSession.bind.execute(query)
