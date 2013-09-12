# -*- coding: utf-8 -*-

import sys
import csv
import logging
import transaction
from datetime import datetime
from standardenum import StandardEnum

from zope.interface import implementer
from pyramid.threadlocal import get_current_request
from sqlalchemy.orm.exc import NoResultFound

from altair.app.ticketing.cart.reserving import NotEnoughAdjacencyException
from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.core import api as core_api
from altair.app.ticketing.core.models import (\
    Operator,
    Organization,
    Performance,
    ChannelEnum,
    PaymentDeliveryMethodPair,
    PaymentMethod,
    DeliveryMethod,
    SalesSegmentGroup,
    SalesSegment,
    Product,
    ProductItem,
    ShippingAddress,
    SeatStatusEnum,
    Seat,
    SeatStatus,
    Venue
)
from altair.app.ticketing.orders.api import create_inner_order
from altair.app.ticketing.orders.export import japanese_columns
from altair.app.ticketing.payments import plugins as payments_plugins
from altair.app.ticketing.payments.plugins.sej import get_ticketing_start_at
from altair.app.ticketing.payments.interfaces import (
    IPaymentCart,
    IPaymentCartedProduct,
    IPaymentCartedProductItem,
    IPaymentShippingAddress
)
from altair.app.ticketing.users.models import UserCredential, Membership
from altair.app.ticketing.utils import sensible_alnum_encode

logger = logging.getLogger(__name__)


class TemporaryModel(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def attributes(self):
        # Todo: このメソッドなくす
        attr = dict()
        for k in self.__dict__:
            v = getattr(self, k)
            logger.info('%s %s %s' % (k, type(v), v))
            if not k.startswith('_') and (isinstance(v, int) or isinstance(v, long) or isinstance(v, unicode)):
                attr[k] = v
        return attr


@implementer(IPaymentCart)
class TemporaryOrder(TemporaryModel):

    order = None
    order_no = None
    total_amount = 0
    system_fee = 0
    delivery_fee = 0
    transaction_fee = 0
    shipping_address = None

    @property
    def performance(self):
        return Performance.query.filter_by(id=self.performance_id).one()

    @property
    def sales_segment(self):
        return SalesSegment.query.filter_by(id=self.sales_segment_id).one()

    @property
    def payment_delivery_pair(self):
        return PaymentDeliveryMethodPair.query.filter_by(id=self.payment_delivery_method_pair_id).one()

    @property
    def operator(self):
        return Operator.query.filter_by(id=self.operator_id).one()

    @property
    def products(self):
        return self._ordered_product.values()

    def finish(self):
        pass


@implementer(IPaymentCartedProduct)
class TemporaryOrderedProduct(TemporaryModel):

    price = 0
    quantity = 0

    @property
    def product(self):
        return Product.query.filter_by(id=self.product_id).one()

    @property
    def items(self):
        return self._ordered_product_item.values()

    @property
    def cart(self):
        return self._parent


@implementer(IPaymentCartedProductItem)
class TemporaryOrderedProductItem(TemporaryModel):

    price = 0
    quantity = 0
    seats = []

    @property
    def product_item(self):
        return ProductItem.query.filter_by(id=self.product_item_id).one()

    @property
    def carted_product(self):
        return self._parent


@implementer(IPaymentShippingAddress)
class TemporaryShippingAddress(TemporaryModel):

    @property
    def email(self):
        return self.email_1 or self.email_2


def price_to_number(string):
    if string is not None:
        string = string.replace(',', '')
    return string

def csv_reader(file):
    # Todo: classにする
    reader = csv.DictReader(file)
    columns = dict((v, k) for k, v in japanese_columns.iteritems())
    header = []
    for field in reader.fieldnames:
        field = unicode(field.decode('cp932'))
        header.append(columns.get(field))
    reader.fieldnames = header

    for row in reader:
        for k, v in row.iteritems():
            row[k] = unicode(v.decode('cp932'))
        yield row


class ImportTypeEnum(StandardEnum):
    Create = (1, u'新規登録')
    Update = (2, u'同じ予約番号を更新')


class OrderImporter():

    def __init__(self, context, performance_id, order_csv, import_type):
        self.operator = context.user
        self.organization_id = context.organization.id
        self.performance_id = performance_id
        self.import_type = None
        self.orders = dict()
        self.error_orders = dict()

        for e in ImportTypeEnum:
            if e.v[0] == import_type:
                self.import_type = e.v
        self.parse_import_file(order_csv.file)

    def parse_import_file(self, file):
        reader = csv_reader(file)
        for row in reader:
            try:
                # Todo: 新規登録で、同じ公演で同じ予約番号の有効な予約が既に存在したらNGにする
                order_no = row.get(u'order.order_no')

                # User
                user = self.get_user(row)

                # SalesSegment, PaymentDeliveryMethodPair
                sales_segment = self.get_sales_segment(row)
                pdmp = self.get_pdmp(row, sales_segment)

                # Order: dict(order_no=order)
                order = self.orders.get(order_no)
                if order is None:
                    order = self.create_temporary_order(row, sales_segment, pdmp, user)

                # OrderedProduct: dict(product_id=ordered_product)
                product = self.get_product(row, sales_segment)
                op = order._ordered_product.get(product.id)
                if op is None:
                    op = self.create_temporary_ordered_product(row, order, product)
                    order._ordered_product[product.id] = op

                # OrderedProductItem: dict(product_item_id=ordered_product_item)
                product_item = self.get_product_item(row, product)
                opi = op._ordered_product_item.get(product_item.id)
                if opi is None:
                    opi = self.create_temporary_ordered_product_item(row, op, product_item)
                    op._ordered_product_item[product_item.id] = opi
                else:
                    opi.quantity += int(row.get(u'ordered_product_item.quantity'))

                # Seat: dict(seat_id=seat)
                seat = self.get_seat(row, product_item)
                if seat:
                    opi._seat_ids.append(seat.id)
            except NoResultFound, e:
                self.error_orders[order_no] = u'予約番号: %s  %s' % (order_no, e.message)
                continue

            self.orders[order_no] = order

    def get_sales_segment(self, row):
        ssg_name = row.get(u'ordered_product.product.sales_segment.sales_segment_group.name')
        try:
            sales_segment = SalesSegment.query.join(SalesSegmentGroup).filter(
                SalesSegment.performance_id == self.performance_id,
                SalesSegmentGroup.name == ssg_name,
            ).one()
        except NoResultFound, e:
            e.message = u'販売区分がありません  販売区分グループ名: %s' % ssg_name
            raise e
        return sales_segment

    def get_pdmp(self, row, sales_segment):
        payment_method_name = row.get(u'payment_method.name')
        delivery_method_name = row.get(u'delivery_method.name')
        try:
            pdmp = PaymentDeliveryMethodPair.query.filter(
                PaymentDeliveryMethodPair.sales_segment_group_id == sales_segment.sales_segment_group_id
            ).join(PaymentMethod).filter(
                PaymentMethod.name == payment_method_name
            ).join(DeliveryMethod).filter(
                DeliveryMethod.name == delivery_method_name
            ).one()
        except NoResultFound, e:
            e.message = u'決済引取方法がありません  決済方法: %s  引取方法: %s' % (payment_method_name, delivery_method_name)
            raise e
        return pdmp

    def get_user(self, row):
        auth_identifier = row.get(u'user_credential.auth_identifier')
        membership_name = row.get(u'membership.name')
        if not auth_identifier or not membership_name:
            return None

        try:
            credential = UserCredential.query.join(Membership).filter(
                UserCredential.auth_identifier == auth_identifier,
                Membership.name==membership_name
            ).one()
        except NoResultFound, e:
            e.message = u'ユーザーが見つかりません'
            raise e
        return credential.user

    def get_product(self, row, sales_segment):
        product_name = row.get(u'ordered_product.product.name')
        try:
            product = Product.query.filter(
                Product.sales_segment_id == sales_segment.id,
                Product.name == product_name
            ).one()
        except NoResultFound, e:
            e.message = u'商品がありません  商品: %s' % product_name
            raise e
        return product

    def get_product_item(self, row, product):
        product_item_name = row.get(u'ordered_product_item.product_item.name')
        try:
            product = ProductItem.query.filter(
                ProductItem.product_id == product.id,
                ProductItem.name == product_item_name
            ).one()
        except NoResultFound, e:
            e.message = u'商品明細がありません  商品明細: %s' % product_item_name
            raise e
        return product

    def get_seat(self, row, product_item):
        seat_name = row.get(u'seat.name')
        if not seat_name:
            return None

        try:
            venue = Venue.query.filter_by(performance_id=self.performance_id).one()
            seat = Seat.query.filter(
                Seat.venue_id == venue.id,
                Seat.stock_id == product_item.stock_id,
                Seat.name == seat_name
            ).one()
        except NoResultFound, e:
            e.message = u'座席がありません  座席: %s' % seat_name
            raise e
        return seat

    def create_temporary_order(self, row, sales_segment, pdmp, user):
        order = TemporaryOrder(
            order_no            = row.get(u'order.order_no'),
            total_amount        = price_to_number(row.get(u'order.total_amount')),
            system_fee          = price_to_number(row.get(u'order.system_fee')),
            transaction_fee     = price_to_number(row.get(u'order.transaction_fee')),
            delivery_fee        = price_to_number(row.get(u'order.delivery_fee')),
            paid_at             = row.get(u'order.paid_at'),
            delivered_at        = row.get(u'order.delivered_at'),
            canceled_at         = row.get(u'order.canceled_at'),
            created_at          = row.get(u'order.created_at'),
            note                = row.get(u'order.note'),
            card_brand          = row.get(u'order.card_brand'),
            card_ahead_com_code = row.get(u'order.card_ahead_com_code'),
            card_ahead_com_name = row.get(u'order.card_ahead_com_name'),
            payment_delivery_method_pair_id = pdmp.id,
            performance_id      = self.performance_id,
            sales_segment_id    = sales_segment.id,
            organization_id     = self.organization_id,
            channel             = ChannelEnum.IMPORT.v,
            operator_id         = self.operator.id,
            user_id             = user.id if user else None,
            branch_no           = 1,
            _shipping_address   = self.create_temporary_shipping_address(row, user),
            _ordered_product    = dict(),
        )
        logger.info(vars(order))
        return order

    def create_temporary_ordered_product(self, row, parent, product):
        ordered_product = TemporaryOrderedProduct(
            price                 = price_to_number(row.get(u'ordered_product.price')),
            quantity              = int(row.get(u'ordered_product.quantity')),
            product_id            = product.id,
            _ordered_product_item = dict(),
            _parent               = parent,
        )
        return ordered_product

    def create_temporary_ordered_product_item(self, row, parent, product_item):
        ordered_product_item = TemporaryOrderedProductItem(
            price           = price_to_number(row.get(u'ordered_product_item.price')),
            quantity        = int(row.get(u'ordered_product_item.quantity')),
            product_item_id = product_item.id,
            _parent         = parent,
            _seat_ids       = []
        )
        return ordered_product_item

    def create_temporary_shipping_address(self, row, user):
        shipping_address    = TemporaryShippingAddress(
            user_id         = user.id if user else None,
            first_name      = row.get(u'shipping_address.first_name'),
            last_name       = row.get(u'shipping_address.last_name'),
            first_name_kana = row.get(u'shipping_address.first_name_kana'),
            last_name_kana  = row.get(u'shipping_address.last_name_kana'),
            zip             = row.get(u'shipping_address.zip').replace('-', ''),
            country         = row.get(u'shipping_address.country'),
            prefecture      = row.get(u'shipping_address.prefecture'),
            city            = row.get(u'shipping_address.city'),
            address_1       = row.get(u'shipping_address.address_1'),
            address_2       = row.get(u'shipping_address.address_2'),
            tel_1           = row.get(u'shipping_address.tel_1'),
            tel_2           = row.get(u'shipping_address.tel_2'),
            fax             = row.get(u'shipping_address.fax'),
            email_1         = row.get(u'shipping_address.email_1'),
            email_2         = row.get(u'shipping_address.email_2'),
            sex             = row.get(u'user_profile.sex'),
            nick_name       = row.get(u'user_profile.nick_name')
        )
        return shipping_address

    def allocate_seats(self, reserving):
        # 予約(ダミーOrder)単位で1件ずつおまかせ配席をしていく
        # 座席ステータスはインナー予約での座席確保と同じ状態にする
        sum_quantity = dict()
        order_no_list = self.orders.keys()
        for order_no in order_no_list:
            order = self.orders.get(order_no)
            error_reason = None
            for op in order._ordered_product.values():
                for opi in op._ordered_product_item.values():
                    product_item = ProductItem.query.filter_by(id=opi.product_item_id).one()
                    stock = product_item.stock
                    if product_item.stock_type.quantity_only:
                        logger.debug('stock %d quantity only' % stock.id)
                        if stock.id not in sum_quantity:
                            sum_quantity[stock.id] = 0
                        sum_quantity[stock.id] += opi.quantity
                        if stock.stock_status.quantity < sum_quantity[stock.id]:
                            logger.info('cannot allocate quantity rest=%s (stock_id=%s, quantity=%s)' % (stock.stock_status.quantity, stock.id, opi.quantity))
                            error_reason = u'配席可能な座席がありません  商品明細: %s  個数: %s  (stock_id: %s)' % (order_no, product_item.name, opi.quantity, stock.id)
                            break
                    else:
                        try:
                            logger.info('product_item_id = %sm stock_id = %s, quantity = %s' % (product_item.id, stock.id, opi.quantity))
                            seats = reserving.reserve_seats(stock.id, int(opi.quantity), reserve_status=SeatStatusEnum.Keep)
                            opi._seat_ids = [s.id for s in seats]
                            logger.info(opi._seat_ids)
                        except NotEnoughAdjacencyException, e:
                            logger.info('cannot allocate seat (stock_id=%s, quantity=%s) %s' % (stock.id, opi.quantity, e))
                            error_reason = u'配席可能な座席がありません  商品明細: %s  個数: %s  (stock_id: %s)' % (order_no, product_item.name, opi.quantity, stock.id)
                            break
                if error_reason:
                    break
            if error_reason:
                self.error_orders[order_no] = u'予約番号: %s  %s' % (order_no, error_reason)
                self.orders.pop(order_no)

    def release_seats(self):
        for order in self.orders.values():
            for op in order._ordered_product.values():
                for opi in op._ordered_product_item.values():
                    for seat_id in opi._seat_ids:
                        seat_status = SeatStatus.query.filter_by(seat_id=seat_id).one()
                        if seat_status.status == int(SeatStatusEnum.Keep):
                            logger.info('seat(%s) status Keep to Vacant' % seat_status.seat_id)
                            seat_status.status = int(SeatStatusEnum.Vacant)

    def get_seat_count(self):
        count = 0
        for order in self.orders.values():
            for op in order._ordered_product.values():
                for opi in op._ordered_product_item.values():
                    count += opi.quantity
        return count

    def get_seat_per_product(self):
        seat_per_product = dict()
        for order in self.orders.values():
            for op in order._ordered_product.values():
                p = Product.query.filter_by(id=op.product_id).one()
                if p not in seat_per_product:
                    seat_per_product[p] = 0
                seat_per_product[p] += sum([int(opi.quantity) for opi in op._ordered_product_item.values()])
        return seat_per_product

    def get_order_per_pdmp(self):
        order_per_pdmp = dict()
        for order in self.orders.values():
            pdmp = PaymentDeliveryMethodPair.query.filter_by(id=order.payment_delivery_method_pair_id).one()
            if pdmp not in order_per_pdmp:
                order_per_pdmp[pdmp] = dict(count=0)
                if pdmp.delivery_method.delivery_plugin_id == payments_plugins.SEJ_DELIVERY_PLUGIN_ID:
                    now = datetime.now()
                    ticketing_start_at = get_ticketing_start_at(now, order)
                    order_per_pdmp[pdmp].update(dict(remark=u'発券開始日時 : %s' % ticketing_start_at.strftime('%Y-%m-%d %H:%M')))
            order_per_pdmp[pdmp]['count'] += 1
        return order_per_pdmp

    def statistics(self):
        stats = dict()

        # インポート方法
        stats['import_type'] = self.import_type
        # インポートする予約数
        stats['order_count'] = len(self.orders)
        # インポートする席数
        stats['seat_count'] = self.get_seat_count()
        # 商品別の席数
        stats['seat_per_product'] = self.get_seat_per_product()
        # 決済方法/引取方法ごとの予約数、コンビニ引取があるなら発券開始日時
        stats['order_per_pdmp'] = self.get_order_per_pdmp()
        # インポートできない予約数
        stats['error_order_count'] = len(self.error_orders)
        # インポートできない理由
        stats['error_orders'] = self.error_orders

        return stats

    def execute(self):
        request = get_current_request()
        stocker = cart_api.get_stocker(request)

        # インポート実行
        for org_order_no, temp_order in self.orders.iteritems():
            # 在庫更新
            # - SeatStatus.statusがInCartの座席は、CartがDB上に生成され座席を所有しているので
            #   在庫数(StockStatus.quantity)も減算しているが、
            #   Keepの座席は*つかんだ*だけで、座席を所有するオブジェクトは一時的なものなので、
            #   在庫数は減算していない
            # - なので、予約確定時に在庫数を減らす
            for temp_ordered_product in temp_order._ordered_product.values():
                for temp_ordered_product_item in temp_ordered_product._ordered_product_item.values():
                    stock = temp_ordered_product_item.product_item.stock

                    # 在庫数
                    quantity = temp_ordered_product_item.quantity
                    stock_requires = [(stock.id, quantity)]
                    stock_statuses = stocker.take_stock_by_stock_id(stock_requires)

                    # 座席ステータス
                    if not stock.stock_type.quantity_only:
                        seat_statuses = SeatStatus.query.filter(
                            SeatStatus.seat_id.in_(temp_ordered_product_item._seat_ids)
                        ).with_lockmode('update').all()
                        for seat_status in seat_statuses:
                            logger.info('seat(%s) status Keep to Ordered' % seat_status.seat_id)
                            if seat_status.status != int(SeatStatusEnum.Keep):
                                logger.error('seat(%s) invalid status %s' % (seat_status.seat_id, seat_status.status))
                                # Todo: エラー時に終了するか継続するか
                                raise Exception(u'invalid seat status')
                            seat_status.status = int(SeatStatusEnum.Ordered)
                            temp_ordered_product_item.seats.append(seat_status.seat)

            # create ShippingAddress
            attr = temp_order._shipping_address.attributes()
            shipping_address = ShippingAddress(**attr)
            shipping_address.save()
            temp_order.shipping_address = shipping_address

            # order_noを採番
            if self.import_type == ImportTypeEnum.Create.v:
                organization = Organization.query.filter_by(id=self.organization_id).one()
                base_id = core_api.get_next_order_no()
                order_no = organization.code + sensible_alnum_encode(base_id).zfill(10)
                temp_order.order_no = order_no

            # 備考欄に追記
            note = temp_order.note
            imported_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            note += u'\nインポート日時: %s' % imported_at
            if self.import_type == ImportTypeEnum.Create.v:
                note += u'\n元の予約番号: %s' % org_order_no

            # create Order
            order = create_inner_order(temp_order, note)

            # その他の項目をセット
            order.paid_at             = temp_order.paid_at
            order.card_brand          = temp_order.card_brand
            order.card_ahead_com_code = temp_order.card_ahead_com_code
            order.card_ahead_com_name = temp_order.card_ahead_com_name
            order.delivered_at        = temp_order.delivered_at
            order.canceled_at         = temp_order.canceled_at
            order.created_at          = temp_order.created_at
            order.save()

            transaction.commit()

        return
