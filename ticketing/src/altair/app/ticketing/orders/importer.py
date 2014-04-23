# -*- coding: utf-8 -*-

import sys
import csv
import logging
import transaction
import json
from dateutil.parser import parse as parsedate
from datetime import datetime
from standardenum import StandardEnum
from collections import OrderedDict
from StringIO import StringIO

from zope.interface import implementer
from pyramid.threadlocal import get_current_request
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from altair.app.ticketing.cart.reserving import NotEnoughAdjacencyException
from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.core import api as core_api
from altair.app.ticketing.core.models import (
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
    Venue,
    OrderImportTask,
    ImportStatusEnum,
    CartMixin,
)
from altair.app.ticketing.orders.api import create_inner_order
from altair.app.ticketing.orders.export import japanese_columns
from altair.app.ticketing.payments import plugins as payments_plugins
from altair.app.ticketing.payments.plugins.sej import get_ticketing_start_at
from altair.app.ticketing.payments.interfaces import IPaymentCart
from altair.app.ticketing.core.interfaces import (
    IOrderedProductLike,
    IOrderedProductItemLike,
    IShippingAddress,
)
from altair.app.ticketing.users.models import UserCredential, Membership
from altair.app.ticketing.utils import sensible_alnum_encode

logger = logging.getLogger(__name__)


class TemporaryModel(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)


@implementer(IPaymentCart)
class TemporaryCart(TemporaryModel, CartMixin):
    def __init__(self, **kwargs):
        self.order = None
        self.order_no = None
        self.total_amount = 0
        self.system_fee = 0
        self.special_fee = 0
        self.special_fee_name = u''
        self.delivery_fee = 0
        self.transaction_fee = 0
        self.shipping_address = None
        self.channel = None
        self.name = None
        self.has_different_amount = False
        self.different_amount = 0
        super(type(self), self).__init__(**kwargs)

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
    def items(self):
        return self._carted_product.values()

    @property
    def calculated_total_amount(self):
        return (self.transaction_fee + self.delivery_fee + self.system_fee + self.special_fee
                + sum([p.price * p.quantity for p in self.items]))

    def finish(self):
        pass


@implementer(IOrderedProductLike)
class TemporaryCartedProduct(TemporaryModel):
    def __init__(self, **kwargs):
        self.price = 0
        self.quantity = 0
        super(type(self), self).__init__(**kwargs)

    @property
    def product(self):
        return Product.query.filter_by(id=self.product_id).one()

    @property
    def elements(self):
        return self._carted_product_item.values()

    @property
    def cart(self):
        return self._parent


@implementer(IOrderedProductItemLike)
class TemporaryCartedProductItem(TemporaryModel):
    def __init__(self, **kwargs):
        self.price = 0
        self.quantity = 0
        self.seats = []
        self.original_seats = []
        super(type(self), self).__init__(**kwargs)

    @property
    def product_item(self):
        return ProductItem.query.filter_by(id=self.product_item_id).one()

    @property
    def carted_product(self):
        return self._parent


@implementer(IShippingAddress)
class TemporaryShippingAddress(TemporaryModel):

    def __init__(self, **kwargs):
        self.user_id         = None
        self.tel_1           = None
        self.tel_2           = None
        self.first_name      = None
        self.last_name       = None
        self.first_name_kana = None
        self.last_name_kana  = None
        self.zip             = None
        self.email_1         = None
        self.email_2         = None
        super(type(self), self).__init__(**kwargs)

    @property
    def email(self):
        return self.email_1 or self.email_2


def price_to_number(string):
    if string is not None:
        string = string.replace(',', '')
    return int(string)


class ImportCSVReader(object):

    def __init__(self, file, encoding='cp932'):
        self.reader = csv.DictReader(file)
        self.encoding = encoding
        columns = dict((v, k) for k, v in japanese_columns.iteritems())
        header = []
        try:
            for field in self.reader.fieldnames:
                field = unicode(field.decode(self.encoding))
                header.append(columns.get(field))
        except Exception, e:
            logger.info('invalid file: %s' % e.message)
        self.reader.fieldnames = header

    def __iter__(self):
        for row in self.reader:
            for k, v in row.iteritems():
                row[k] = v.decode(self.encoding) if v is not None else u''
            yield row

    @property
    def fieldnames(self):
        return self.reader.fieldnames


class ImportTypeEnum(StandardEnum):
    Create = 1
    Update = 2

class AllocationModeEnum(StandardEnum):
    AlwaysAllocateNew = 1
    NoAutoAllocation = 2

import_type_labels = {
    1: u'新規登録',
    2: u'同じ予約番号を更新',
    }

allocation_mode_labels = {
    1: u'座席番号を無視し常に自動配席する',
    2: u'座席番号に該当する座席を配席する',
    }

def get_import_type_label(import_type):
    return import_type_labels.get(int(import_type), None)

def get_allocation_mode_label(allocation_mode):
    return allocation_mode_labels.get(int(allocation_mode), None)

class OrderImporter(object):
    def __init__(self, operator, organization, performance_id, order_csv, import_type, allocation_mode=AllocationModeEnum.AlwaysAllocateNew, **kwargs):
        self.operator_id = operator.id
        self.organization_id = organization.id
        self.performance_id = performance_id
        self.import_type = int(import_type)
        self.allocation_mode = int(allocation_mode)
        self.status = ImportStatusEnum.Waiting.v[0]
        file_data = order_csv.read()
        self.file_data = unicode(file_data.decode('cp932'))

        # csvファイルから読み込んだ予約 {order_no:cart}
        self.carts = OrderedDict()
        # csvファイルから読み込めなかった予約 / インポートできなかった予約 {order_no:cart}
        self.errors = OrderedDict()

        self.task_id = None
        self.created_at = None
        self.updated_at = None
        if 'task_id' in kwargs:
            self.task_id = kwargs.get('task_id')
        if 'created_at' in kwargs:
            self.created_at = kwargs.get('created_at')
        if 'updated_at' in kwargs:
            self.updated_at = kwargs.get('updated_at')
        if 'status' in kwargs:
            self.status = kwargs.get('status')
        if 'errors' in kwargs:
            errors = kwargs.get('errors')
            if errors:
                self.errors = OrderedDict(errors)

        file = StringIO()
        file.write(file_data)
        file.seek(0)
        self.parse_import_file(file)

    @property
    def task(self):
        if self.task_id:
            return OrderImportTask.query.filter_by(id=self.task_id).one()
        return None

    @property
    def operator(self):
        return Operator.query.filter_by(id=self.operator_id).one()

    @property
    def imported(self):
        return self.status == ImportStatusEnum.Imported.v[0]

    @property
    def valid_carts(self):
        errors = self.errors.keys()
        return OrderedDict([(order_no, cart) for order_no, cart in self.carts.items() if order_no not in errors])

    @property
    def import_type_label(self):
        return get_import_type_label(self.import_type) or u''

    def parse_import_file(self, file):
        reader = ImportCSVReader(file)
        for row in reader:
            try:
                order_no = row.get(u'order.order_no')
                if order_no in self.errors.keys():
                    continue

                # create TemporaryCart
                cart = self.carts.get(order_no)
                if cart is None:
                    # User
                    user = self.get_user(row)

                    # SalesSegment, PaymentDeliveryMethodPair
                    sales_segment = self.get_sales_segment(row)
                    pdmp = self.get_pdmp(row, sales_segment)

                    # TemporaryCart: dict(order_no=temp_cart)
                    cart = self.create_temporary_cart(row, sales_segment, pdmp, user)

                # create TemporaryCartedProduct: dict(product_id=temp_carted_product)
                product = self.get_product(row, cart.sales_segment)
                cp = cart._carted_product.get(product.id)
                if cp is None:
                    cp = self.create_temporary_carted_product(row, cart, product)
                    cart._carted_product[product.id] = cp

                # create TemporaryOrderedProductItem: dict(product_item_id=temp_carted_product_item)
                product_item = self.get_product_item(row, product)
                cpi = cp._carted_product_item.get(product_item.id)
                if cpi is None:
                    cpi = self.create_temporary_carted_product_item(row, cp, product_item)
                    cp._carted_product_item[product_item.id] = cpi
                else:
                    cpi.quantity += int(row.get(u'ordered_product_item.quantity'))

                # Seat: dict(seat_id=seat)
                seat = self.get_seat(row, product_item)
                cpi.original_seats.append(seat)
            except (NoResultFound, MultipleResultsFound), e:
                self.errors[order_no] = u'予約番号: %s  %s' % (order_no, e.message)
                continue

            self.carts[order_no] = cart
        return

    def validate(self):
        from altair.app.ticketing.models import DBSession
        session = DBSession
        sum_quantity = dict()
        order_no_list = self.carts.keys()
        for order_no in order_no_list:
            cart = self.carts.get(order_no)

            # 合計金額
            if cart.total_amount != cart.calculated_total_amount:
                self.errors[order_no] = u'予約番号: %s  %s' % (order_no, u'合計金額が正しくありません')
            for cp in cart.items:
                if (cp.price * cp.quantity) != sum([cpi.price * cpi.quantity for cpi in cp.elements]):
                    self.errors[order_no] = u'予約番号: %s  %s' % (order_no, u'商品単価または商品個数が正しくありません')

            # 在庫数
            # - ここでは在庫総数のチェックのみ
            # - 実際に配席しないと連席判定も含めた在庫の過不足は分からない為
            try:
                for cp in cart.items:
                    for cpi in cp.elements:
                        product_item = cpi.product_item
                        stock = product_item.stock
                        if stock.id not in sum_quantity:
                            sum_quantity[stock.id] = 0

                        sum_quantity[stock.id] += cpi.quantity
                        if stock.stock_status.quantity < sum_quantity[stock.id]:
                            logger.info('cannot allocate quantity rest=%s (stock_id=%s, quantity=%s)' %
                                        (stock.stock_status.quantity, stock.id, cpi.quantity))
                            error_reason = u'配席可能な座席がありません  商品明細: %s  個数: %s  (stock_id: %s)' %\
                                           (product_item.name, cpi.quantity, stock.id)
                            raise Exception(error_reason)
                        if self.allocation_mode == AllocationModeEnum.NoAutoAllocation.v:
                            if not stock.stock_type.quantity_only:
                                # セッションからdetachしているかもしれないので
                                for seat in cpi.original_seats:
                                    session.add(seat)
                                if not all(cpi.original_seats):
                                    raise Exception(u'座席番号が一致しないもしくは指定されていないデータがありますが、自動配席が無効になっています')
                                if len(cpi.original_seats) != cpi.quantity:
                                    raise Exception(u'商品明細数と座席数が一致しません')
                                for seat in cpi.original_seats:
                                    if seat.status != SeatStatusEnum.Vacant.v:
                                        raise Exception(u'座席「%s」(id=%ld, l0_id=%s) は配席済みです' % (seat.name, seat.id, seat.l0_id))
            except Exception as e:
                self.errors[order_no] = u'予約番号: %s  %s' % (order_no, e.message)
        return

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
        except MultipleResultsFound, e:
            e.message = u'候補の販売区分が複数あります  販売区分グループ名: %s' % ssg_name
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
        except MultipleResultsFound, e:
            e.message = u'候補の決済引取方法が複数あります  決済方法: %s  引取方法: %s' % (payment_method_name, delivery_method_name)
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
        except MultipleResultsFound, e:
            e.message = u'候補の商品が複数あります  商品: %s' % product_name
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
        except MultipleResultsFound, e:
            e.message = u'候補の商品明細が複数あります  商品明細: %s' % product_item_name
            raise e
        return product

    def get_seat(self, row, product_item):
        seat_name = row.get(u'seat.name')
        if not seat_name:
            return None

        try:
            venue = Venue.query.filter_by(performance_id=self.performance_id).one()
            seat = Seat.query.options(joinedload(Seat.status_)).filter(
                Seat.venue_id == venue.id,
                Seat.stock_id == product_item.stock_id,
                Seat.name == seat_name
            ).one()
        except NoResultFound, e:
            e.message = u'座席がありません  座席: %s' % seat_name
            raise e
        except MultipleResultsFound, e:
            e.message = u'候補の座席が複数あります  座席: %s' % seat_name
            raise e
        return seat

    def create_temporary_cart(self, row, sales_segment, pdmp, user):
        cart = TemporaryCart(
            order_no            = row.get(u'order.order_no'),
            total_amount        = price_to_number(row.get(u'order.total_amount')),
            system_fee          = price_to_number(row.get(u'order.system_fee')),
            special_fee         = price_to_number(row.get(u'order.special_fee')),
            special_fee_name    = row.get(u'order.special_fee_name'),
            transaction_fee     = price_to_number(row.get(u'order.transaction_fee')),
            delivery_fee        = price_to_number(row.get(u'order.delivery_fee')),
            note                = row.get(u'order.note'),
            performance_id      = self.performance_id,
            organization_id     = self.organization_id,
            operator_id         = self.operator_id,
            sales_segment_id    = sales_segment.id,
            payment_delivery_method_pair_id = pdmp.id,
            user_id             = user.id if user else None,
            branch_no           = 1,
            channel             = ChannelEnum.IMPORT.v,
            _shipping_address   = self.create_temporary_shipping_address(row, user),
            _carted_product     = dict(),
            paid_at             = parsedate(row.get(u'order.paid_at')),
            created_at          = parsedate(row.get(u'order.created_at')),
        )
        return cart

    def create_temporary_carted_product(self, row, parent, product):
        carted_product = TemporaryCartedProduct(
            price                 = price_to_number(row.get(u'ordered_product.price')),
            quantity              = int(row.get(u'ordered_product.quantity')),
            product_id            = product.id,
            _carted_product_item  = dict(),
            _parent               = parent,
        )
        return carted_product

    def create_temporary_carted_product_item(self, row, parent, product_item):
        carted_product_item = TemporaryCartedProductItem(
            price           = price_to_number(row.get(u'ordered_product_item.price')),
            quantity        = int(row.get(u'ordered_product_item.quantity')),
            product_item_id = product_item.id,
            _parent         = parent,
        )
        return carted_product_item

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
        )
        return shipping_address

    def get_seat_count(self, carts):
        count = 0
        for cart in carts.values():
            for cp in cart.items:
                count += sum([cpi.quantity for cpi in cp.elements])
        return count

    def get_seat_per_product(self, carts):
        seat_per_product = OrderedDict()
        for cart in carts.values():
            for cp in cart.items:
                p = cp.product
                if p not in seat_per_product:
                    seat_per_product[p] = 0
                seat_per_product[p] += sum([int(cpi.quantity) for cpi in cp.elements])
        return seat_per_product

    def get_order_per_pdmp(self, carts):
        order_per_pdmp = OrderedDict()
        for cart in carts.values():
            pdmp = cart.payment_delivery_pair
            if pdmp not in order_per_pdmp:
                order_per_pdmp[pdmp] = dict(count=0)
                if pdmp.delivery_method.delivery_plugin_id == payments_plugins.SEJ_DELIVERY_PLUGIN_ID:
                    now = datetime.now()
                    ticketing_start_at = get_ticketing_start_at(now, cart)
                    order_per_pdmp[pdmp].update(dict(remark=u'発券開始日時 : %s' % ticketing_start_at.strftime('%Y-%m-%d %H:%M')))
            order_per_pdmp[pdmp]['count'] += 1
        return order_per_pdmp

    def stats(self):
        stats = dict()
        carts = self.valid_carts
        errors = self.errors

        # インポート方法
        stats['import_type'] = get_import_type_label(self.import_type)
        # 配席モード
        stats['allocation_mode'] = get_allocation_mode_label(self.allocation_mode)
        # インポートする予約数
        stats['order_count'] = len(carts)
        # インポートする席数
        stats['seat_count'] = self.get_seat_count(carts)
        # 商品別の席数
        stats['seat_per_product'] = self.get_seat_per_product(carts)
        # 決済方法/引取方法ごとの予約数、コンビニ引取があるなら発券開始日時
        stats['order_per_pdmp'] = self.get_order_per_pdmp(carts)
        # インポートできない予約数
        stats['error_order_count'] = len(errors)
        # インポートできない理由
        stats['error_orders'] = errors

        # OrderImportTaskからの情報
        stats['task_id'] = self.task_id
        stats['created_at'] = self.created_at
        stats['updated_at'] = self.updated_at

        stats['operator_name'] = self.operator.name
        stats['status'] = OrderImportTask.status_label(self.status)

        return stats

    def allocate_seats(self, reserving, product_item, quantity):
        stock = product_item.stock
        logger.info('product_item_id = %sm stock_id = %s, quantity = %s' % (product_item.id, stock.id, quantity))

        seats = []
        if not product_item.stock_type.quantity_only:
            try:
                seats = reserving.reserve_seats(stock.id, int(quantity), reserve_status=SeatStatusEnum.Ordered)
            except NotEnoughAdjacencyException, e:
                logger.info('cannot allocate seat (stock_id=%s, quantity=%s) %s' % (stock.id, quantity, e))
                e.message = u'配席可能な座席がありません  商品明細: %s  個数: %s  (stock_id: %s)' % (product_item.name, quantity, stock.id)
                raise e
        return seats

    def execute(self):
        request = get_current_request()
        stocker = cart_api.get_stocker(request)
        reserving = cart_api.get_reserving(request)

        # ステータス更新
        self.status = ImportStatusEnum.Importing.v[0]
        self.update_task()
        transaction.commit()

        self.validate()
        from altair.app.ticketing.models import DBSession
        session = DBSession

        # インポート実行
        order_no_list = self.carts.keys()
        for org_order_no in order_no_list:
            logger.info('order_no (%s) importing..' % org_order_no)
            temp_cart = self.carts.get(org_order_no)

            # 配席/在庫更新
            try:
                for temp_cp in temp_cart.items:
                    for temp_cpi in temp_cp.elements:
                        product_item = temp_cpi.product_item
                        stock = temp_cpi.product_item.stock

                        # 在庫数
                        quantity = temp_cpi.quantity
                        stock_requires = [(stock.id, quantity)]
                        stockstatuses = stocker.take_stock_by_stock_id(stock_requires)

                        # 配席
                        if not stock.stock_type.quantity_only:
                            if self.allocation_mode == AllocationModeEnum.NoAutoAllocation.v:
                                assert len(temp_cpi.original_seats) == temp_cpi.quantity, 'len(cpi.original_seats) (%d) != cpi.quantity (%d)' % (len(temp_cpi.original_seats), temp_cpi.quantity)
                                for seat in temp_cpi.original_seats:
                                    session.add(seat)
                                reserving.reserve_selected_seats(stockstatuses, performance_id=temp_cart.performance_id, selected_seat_l0_ids=[seat.l0_id for seat in temp_cpi.original_seats], reserve_status=SeatStatusEnum.Ordered)
                                temp_cpi.seats += temp_cpi.original_seats
                            elif self.allocation_mode == AllocationModeEnum.AlwaysAllocateNew.v:
                                seats = self.allocate_seats(reserving, product_item, temp_cpi.quantity)
                                temp_cpi.seats += seats
                            else:
                                raise AssertionError('never get here')
            except Exception as e:
                logger.error('take stock error (%s): %r' % (org_order_no, e))
                transaction.abort()
                self.errors[org_order_no] = u'予約番号: %s  %s' % (org_order_no, u'座席を確保できませんでした')
                continue

            # create ShippingAddress
            attr = temp_cart._shipping_address.__dict__
            shipping_address = ShippingAddress(**attr)
            shipping_address.save()
            temp_cart.shipping_address = shipping_address

            # order_noを採番
            if self.import_type == ImportTypeEnum.Create.v:
                organization = Organization.query.filter_by(id=self.organization_id).one()
                base_id = core_api.get_next_order_no()
                order_no = organization.code + sensible_alnum_encode(base_id).zfill(10)
                temp_cart.order_no = order_no

            # 備考欄に追記
            note = u''
            if self.import_type == ImportTypeEnum.Create.v:
                note = u'元の予約番号: %s  ' % org_order_no
            imported_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            note += u'インポート日時: %s' % imported_at
            if temp_cart.note:
                note += u'\n' + temp_cart.note

            # create Order
            try:
                order = create_inner_order(temp_cart, note)
            except Exception, e:
                logger.error('create inner order error (%s): %s' % (org_order_no, e.message), exc_info=sys.exc_info())
                transaction.abort()
                self.errors[org_order_no] = u'予約番号: %s  %s' % (org_order_no, e.message)
                continue

            if temp_cart.created_at:
                # 予約日時があれば維持
                order.created_at = temp_cart.created_at
            if temp_cart.paid_at:
                # 決済日時はコンビニ決済でないなら維持
                payment_plugin_id = order.payment_delivery_pair.payment_method.payment_plugin_id
                if payment_plugin_id != payments_plugins.SEJ_PAYMENT_PLUGIN_ID:
                    order.paid_at = temp_cart.paid_at

            order.save()
            transaction.commit()
            logger.info('order_no (%s) import success' % org_order_no)

        # ステータス更新
        self.status = ImportStatusEnum.Imported.v[0]
        self.update_task()
        transaction.commit()

        return

    def add_task(self):
        task = OrderImportTask(
            organization_id=self.organization_id,
            performance_id=self.performance_id,
            operator_id=self.operator_id,
            import_type=self.import_type,
            allocation_mode=self.allocation_mode,
            count=len(self.valid_carts),
            status=self.status,
            data=self.file_data,
            errors=json.dumps(self.errors)
        )
        task.save()

    def update_task(self):
        task = self.task
        task.status = self.status
        task.errors = json.dumps(self.errors)
        task.save()

    @staticmethod
    def load_task(task):
        file = StringIO()
        file.write(task.data.encode('cp932'))
        file.seek(0)
        return OrderImporter(
            task.operator,
            task.organization,
            task.performance_id,
            file,
            task.import_type,
            task.allocation_mode,
            task_id=task.id,
            created_at=task.created_at,
            updated_at=task.updated_at,
            status=task.status,
            errors=task.errors
        )
