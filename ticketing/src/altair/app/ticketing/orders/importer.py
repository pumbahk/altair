# -*- coding: utf-8 -*-

import sys
import re
import csv
import logging
import transaction
import json
import six
from decimal import Decimal
from datetime import datetime, date, time
from standardenum import StandardEnum
from collections import OrderedDict
from StringIO import StringIO

from pyramid.decorator import reify
from zope.interface import implementer
from sqlalchemy.sql import expression as sql_expr
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from altair.timeparse import parse_date_or_time
from altair.viewhelpers.datetime_ import create_date_time_formatter
from altair.app.ticketing.utils import todatetime, todate
from altair.app.ticketing.payments.api import lookup_plugin
from altair.app.ticketing.cart.reserving import NotEnoughAdjacencyException
from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.core import api as core_api
from altair.app.ticketing.core.models import (
    Operator,
    Organization,
    Event,
    Performance,
    ChannelEnum,
    PaymentDeliveryMethodPair,
    SalesSegment_PaymentDeliveryMethodPair,
    PaymentMethod,
    DeliveryMethod,
    SalesSegmentGroup,
    SalesSegment,
    Product,
    ProductItem,
    ShippingAddress,
    SeatStatusEnum,
    StockTypeEnum,
    Seat,
    SeatStatus,
    Venue,
    CartMixin,
    )
from altair.app.ticketing.lots.models import (
    Lot,
    LotEntry,
    )
from altair.app.ticketing.orders.models import (
    Order,
    OrderedProduct,
    OrderedProductItem,
    OrderedProductItemToken,
    )
from altair.app.ticketing.payments import plugins as payments_plugins
from altair.app.ticketing.payments.exceptions import OrderLikeValidationFailure
from altair.app.ticketing.payments.plugins.sej import get_ticketing_start_at
from altair.app.ticketing.payments.interfaces import IPaymentCart
from altair.app.ticketing.core.interfaces import (
    IOrderedProductLike,
    IOrderedProductItemLike,
    IShippingAddress,
    )
from altair.app.ticketing.users.models import UserCredential, Membership, MemberGroup, Member, MemberGroup_SalesSegment
from altair.app.ticketing.utils import sensible_alnum_encode
from .models import OrderImportTask, ImportStatusEnum, ImportTypeEnum, AllocationModeEnum, ProtoOrder
from .api import create_or_update_orders_from_proto_orders, get_order_by_order_no, get_relevant_object, label_for_object
from .export import japanese_columns
from .exceptions import MassOrderCreationError

logger = logging.getLogger(__name__)


class ImportCSVReader(object):
    def __init__(self, file, encoding='cp932'):
        self.reader = csv.DictReader(file)
        self.encoding = encoding
        columns = dict((v, k) for k, v in japanese_columns.iteritems())
        header = []
        for field in self.reader.fieldnames:
            field = unicode(field.decode(self.encoding))
            column_id = columns.get(field)
            if column_id is None:
                # 該当するカラムがない場合には、ヘッダに出現した内容をそのままキーとする
                column_id = field
            header.append(column_id)
        self.reader.fieldnames = header

    def __iter__(self):
        for row in self.reader:
            for k, v in row.iteritems():
                row[k] = v.decode(self.encoding) if v is not None else u''
            yield row

    @property
    def line_num(self):
        return self.reader.line_num

    @property
    def fieldnames(self):
        return self.reader.fieldnames

IMPORT_ERROR = 100
IMPORT_WARNING = 50

class ImporterErrorBase(Exception):
    def __init__(self, ref, message, *args):
        super(ImporterErrorBase, self).__init__(ref, message, *args)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u'%s: %s' % (self.ref, self.message)

    @property
    def ref(self):
        return self.args[0]

    @property
    def message(self):
        return self.args[1]

    @property
    def level(self):
        return self.args[2]


class ImportCSVParserError(ImporterErrorBase):
    def __init__(self, ref, message, level, line_num):
        super(ImportCSVParserError, self).__init__(ref, message, level, line_num)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        if self.line_num:
            return u'%s (行 %d)' % (super(ImportCSVParserError, self).__unicode__(), self.line_num)
        else:
            return super(ImportCSVParserError, self).__unicode__()

    @property
    def line_num(self):
        return self.args[3]


class ImporterValidationError(ImporterErrorBase):
    pass


class DummyCart(CartMixin):
    def __init__(self, proto_order):
        self.proto_order = proto_order
        self.product_quantity_pair = [(p.product, p.quantity) for p in self.proto_order.items]

    @property
    def created_at(self):
        return self.proto_order.new_order_created_at

    @reify
    def total_amount(self):
        return core_api.calculate_total_amount(self.proto_order)

    @reify
    def payment_delivery_pair(self):
        return self.proto_order.payment_delivery_pair

    @reify
    def sales_segment(self):
        return self.proto_order.sales_segment

    @reify
    def system_fee(self):
        return self.sales_segment.get_system_fee(self.payment_delivery_pair, self.product_quantity_pair)

    @reify
    def special_fee(self):
        return self.sales_segment.get_special_fee(self.payment_delivery_pair, self.product_quantity_pair)

    @reify
    def transaction_fee(self):
        return self.sales_segment.get_transaction_fee(self.payment_delivery_pair, self.product_quantity_pair)

    @reify
    def delivery_fee(self):
        return self.sales_segment.get_delivery_fee(self.payment_delivery_pair, self.product_quantity_pair)

    @property
    def performance(self):
        return self.proto_order.performance


def date_time_compare(a, b):
    if isinstance(a, datetime):
        return a == todatetime(b)
    elif isinstance(a, date):
        return a == todate(b)
    else:
        return a == b

class ImportCSVParserContext(object):
    attribute_re = re.compile(ur'attribute\[([^]]*)\]')

    shipping_address_record_key_map = {
        'first_name': {
            'key': u'shipping_address.first_name',
            'required': True,
            },
        'last_name': {
            'key': u'shipping_address.last_name',
            'required': True,
            },
        'first_name_kana': {
            'key': u'shipping_address.first_name_kana',
            'required': True,
            },
        'last_name_kana': {
            'key': u'shipping_address.last_name_kana',
            'required': True,
            },
        'zip': {
            'key': u'shipping_address.zip',
            'required': True,
            },
        'country': {
            'key': u'shipping_address.country',
            'required': True,
            },
        'prefecture': {
            'key': u'shipping_address.prefecture',
            'required': True,
            },
        'city': {
            'key': u'shipping_address.city',
            'required': True,
            },
        'address_1': {
            'key': u'shipping_address.address_1',
            'required': True,
            },
        'address_2': {
            'key': u'shipping_address.address_2',
            'required': False,
            },
        'tel_1': {
            'key': u'shipping_address.tel_1',
            'required': True,
            },
        'tel_2': {
            'key': u'shipping_address.tel_2',
            'required': False,
            },
        'fax': {
            'key': u'shipping_address.fax',
            'required': False,
            },
        'email_1': {
            'key': u'shipping_address.email_1',
            'required': True,
            },
        'email_2': {
            'key': u'shipping_address.email_2',
            'required': False,
            },
        'sex': {
            'key': u'user_profile.sex',
            'required': False,
            },
        }

    def __init__(self, request, session, exc_factory, order_import_task, organization, performance, event, default_payment_method, default_delivery_method):
        self.request = request
        self.session = session
        self.exc_factory = exc_factory
        self.order_import_task = order_import_task
        self.organization = organization
        self.event = event
        self.performance = performance
        self.event = event or (performance and performance.event)
        self.default_payment_method = default_payment_method
        self.default_delivery_method = default_delivery_method

        self.orders_will_be_created = bool(order_import_task.import_type & ImportTypeEnum.Create.v)
        self.orders_will_be_updated = bool(order_import_task.import_type & ImportTypeEnum.Update.v)
        self.always_issue_order_no = bool(order_import_task.import_type & ImportTypeEnum.AlwaysIssueOrderNo.v)
        self.merge_order_attributes = order_import_task.merge_order_attributes
        self.operator = order_import_task.operator

        # csvファイルから読み込んだ予約 {order_no:cart}
        self.carts = OrderedDict()
        # csvファイルから読み込めなかった予約 / インポートできなかった予約 {order_no:[error, error...]}
        self.ordered_product_for_order_and_product = {}
        self.ordered_product_item_for_ordered_product_and_product_item = {}
        self.serial_for_element = {}
        self.performances = {}
        self.events = {}
        self.venues = {}
        self.payment_methods = {}
        self.delivery_methods = {}
        self.date_time_formatter = create_date_time_formatter(request)

    def parse_int(self, string, message):
        if string is not None:
            string = string.strip()
        if string:
            string = string.replace(',', '')
            try:
                return int(string)
            except Exception as e:
                logger.debug(u'invalid integer string: %r' % e)
                raise self.exc_factory(u'%s: %s' % (message, string))
        return None

    def parse_decimal(self, string, message):
        if string is not None:
            string = string.strip()
        if string:
            string = string.replace(',', '')
            try:
                return Decimal(string)
            except Exception as e:
                logger.debug(u'invalid decimal string: %r' % e)
                raise self.exc_factory(u'%s: %s' % (message, string))
        return None

    def parse_date(self, string, message, as_datetime=True):
        if string is not None:
            string = string.strip()
        if string:
            try:
                lazy_dt = parse_date_or_time(string)
                return lazy_dt.as_date_datetime_or_time(to_datetime=as_datetime)
            except Exception as e:
                logger.debug(u'invalid date/time string: %r' % e)
                raise self.exc_factory(u'%s: %s' % (message, string))
        return None

    def get_proto_order(self, row, order_no_or_key, performance, sales_segment, pdmp, cart_setting, attributes=None):
        # create TemporaryCart
        cart = self.carts.get(order_no_or_key)
        if cart is None:
            membership, membergroup, user = self.get_user(row)
            note = re.split(ur'\r\n|\r|\n', row.get(u'order.note', u'').strip())
            # SalesSegment, PaymentDeliveryMethodPair
            original_order = None
            obj = None
            if order_no_or_key:
                obj = get_relevant_object(self.request, order_no_or_key, self.session, include_deleted=True)
                logger.info('relevant_object=%s' % obj)
            if self.always_issue_order_no and self.orders_will_be_created:
                order_no = None
                if isinstance(obj, Order):
                    if self.orders_will_be_updated:
                        if obj.is_canceled() or obj.deleted_at is not None:
                            raise self.exc_factory(u'元の注文 %s はキャンセル済みです' % obj.order_no)
                        order_no = order_no_or_key
                        original_order = obj
                elif obj is not None:
                    order_no = core_api.get_next_order_no(self.request, self.organization)
                    logger.info('always_issue_order_no is specified; new_order_no=%s' % order_no)
                    if isinstance(obj, LotEntry):
                        note.append(u'元の抽選の予約番号: %s' % order_no_or_key)
                    else: 
                        logger.info(u'%s is used by %s' % (order_no_or_key, label_for_object(obj)))

                # 予約番号の特定ができない場合は新規に発番する
                if order_no is None:
                    order_no = core_api.get_next_order_no(self.request, self.organization)
                    logger.info('always_issue_order_no is specified; new_order_no=%s' % order_no)
            else:
                if obj is not None:
                    order_no = order_no_or_key
                    if isinstance(obj, LotEntry):
                        if obj.is_canceled or obj.deleted_at is not None:
                            raise self.exc_factory(u'抽選 %s はキャンセル済みです' % obj.entry_no)
                        note.append(u'抽選より同じ予約番号で生成')
                    else:
                        if self.orders_will_be_updated:
                            if isinstance(obj, Order):
                                if obj.is_canceled() or obj.deleted_at is not None:
                                    raise self.exc_factory(u'元の注文 %s はキャンセル済みです' % obj.order_no)
                                original_order = obj
                            else:
                                raise self.exc_factory(u'更新対象が注文ではありません (%sです)' % label_for_object(obj))
                        else:
                            if obj.deleted_at is not None:
                                raise self.exc_factory(u'この予約番号は予約されています')
                            else:
                                raise self.exc_factory(u'すでに同じ予約番号の予約またはカートが存在します')
                else:
                    if self.orders_will_be_created:
                        order_no = core_api.get_next_order_no(self.request, self.organization)
                    elif self.orders_will_be_updated:
                        raise self.exc_factory(u'更新対象の注文が存在しません')
            if original_order is not None:
                if original_order.issued_at is not None or \
                   original_order.printed_at is not None:
                    raise self.exc_factory(u'更新対象の注文はすでに発券済みです')
                if original_order.payment_delivery_pair.payment_method.payment_plugin_id != pdmp.payment_method.payment_plugin_id:
                    raise self.exc_factory(u'更新対象の注文の決済方法と新しい注文の決済方法が異なっています')
                if original_order.payment_delivery_pair.delivery_method.delivery_plugin_id != pdmp.delivery_method.delivery_plugin_id:
                    raise self.exc_factory(u'更新対象の注文の引取方法と新しい注文の引取方法が異なっています')

            new_order_created_at = None
            new_order_paid_at = None
            issuing_start_at = None
            issuing_end_at = None
            payment_start_at = None
            payment_due_at = None

            new_order_created_at_str = row.get(u'order.created_at')
            new_order_created_at = self.parse_date(new_order_created_at_str, u'注文生成日時が不正です')

            new_order_paid_at_str = row.get(u'order.paid_at')
            new_order_paid_at = self.parse_date(new_order_paid_at_str, u'支払日時が不正です')

            issuing_start_at_str = row.get(u'order.issuing_start_at')
            issuing_start_at = self.parse_date(issuing_start_at_str, u'発券開始日時が不正です')

            issuing_end_at_str = row.get(u'order.issuing_end_at')
            issuing_end_at = self.parse_date(issuing_end_at_str, u'発券終了日時が不正です')

            payment_start_at_str = row.get(u'order.paymenet_start_at')
            payment_start_at = self.parse_date(payment_start_at_str, u'支払開始日時が不正です')

            payment_due_at_str = row.get(u'order.payment_due_at')
            payment_due_at = self.parse_date(payment_due_at_str, u'支払期限が不正です')

            shipping_address = self.create_shipping_address(row, user)

            if original_order is not None:
                if new_order_created_at is None:
                    logger.info(u'[%s] new_order_created_at is not specified; using that of the original order' % original_order.order_no)
                    new_order_created_at = original_order.created_at
                if new_order_paid_at is None: 
                    logger.info(u'[%s] new_order_paid_at is not specified; using that of the original order' % original_order.order_no)
                    new_order_paid_at = original_order.paid_at
                if issuing_start_at is None:
                    logger.info(u'[%s] issuing_start_at is not specified; using that of the original order' % original_order.order_no)
                    issuing_start_at = original_order.issuing_start_at
                if issuing_end_at is None:
                    logger.info(u'[%s] issuing_end_at is not specified; using that of the original order' % original_order.order_no)
                    issuing_end_at = original_order.issuing_end_at
                if payment_start_at is None:
                    logger.info(u'[%s] payment_start_at is not specified; using that of the original order' % original_order.order_no)
                    payment_start_at = original_order.payment_start_at
                if payment_due_at is None:
                    logger.info(u'[%s] payment_due_at is not specified; using that of the original order' % original_order.order_no)
                    payment_due_at = original_order.payment_due_at
                if shipping_address is None:
                    logger.info(u'[%s] shipping_address is not specified; using that of the original order' % original_order.order_no)
                    shipping_address = original_order.shipping_address
                if membership is None:
                    logger.info(u'[%s] user information is not specified; using that of the original order' % original_order.order_no)
                    membership = original_order.membership
                    user = original_order.user
                    if user is not None and sales_segment is not None and membership is not None:
                        membergroup = None
                        try:
                            membergroup = self.session.query(MemberGroup) \
                                .join(Member) \
                                .join(MemberGroup_SalesSegment) \
                                .filter(MemberGroup.membership_id == membership.id) \
                                .filter(Member.user_id == user.id) \
                                .filter(MemberGroup_SalesSegment.c.sales_segment_id == sales_segment.id) \
                                .one()
                        except NoResultFound:
                            logger.info(
                                u'[%s] no corresponding Member found for Membership(id=%ld), User(id=%ld), SalesSegment(id=%ld)' % (
                                    original_order.order_no,
                                    membership.id, user.id, sales_segment.id
                                    )
                                )
                        except MultipleResultsFound:
                            logger.info(
                                u'[%s] multiple Member found for Membership(id=%ld), User(id=%ld), SalesSegment(id=%ld)' % (
                                    original_order.order_no,
                                    membership.id, user.id, sales_segment.id
                                    )
                                )
                if attributes is None:
                    attributes = dict(original_order.attributes)
                else:
                    if self.merge_order_attributes:
                        _attributes = dict(original_order.attributes)
                        _attributes.update(attributes)
                        attributes = _attributes

            if shipping_address is None:
                # インナー予約なので、指定されていないときは
                # 空の配送先を作るので良い (作らない方が良い?)
                shipping_address = ShippingAddress(user=user)

            # TemporaryCart: dict(order_no=temp_cart)
            cart = self.carts[order_no_or_key] = ProtoOrder(
                ref                   = order_no_or_key,
                order_no              = order_no,
                total_amount          = self.parse_decimal(row.get(u'order.total_amount'), u'合計金額が不正です'),
                system_fee            = self.parse_decimal(row.get(u'order.system_fee'), u'システム利用料が不正です'),
                special_fee           = self.parse_decimal(row.get(u'order.special_fee'), u'特別手数料が不正です'),
                special_fee_name      = row.get(u'order.special_fee_name'),
                transaction_fee       = self.parse_decimal(row.get(u'order.transaction_fee'), u'決済手数料が不正です'),
                delivery_fee          = self.parse_decimal(row.get(u'order.delivery_fee'), u'配送手数料が不正です'),
                note                  = u'\n'.join(note),
                performance           = performance,
                organization          = self.organization,
                operator              = self.operator,
                sales_segment         = sales_segment,
                payment_delivery_pair = pdmp,
                membership            = membership,
                membergroup           = membergroup,
                user                  = user,
                shipping_address      = shipping_address,
                new_order_paid_at     = new_order_paid_at,
                new_order_created_at  = new_order_created_at,
                original_order        = original_order,
                issuing_start_at      = issuing_start_at,
                issuing_end_at        = issuing_end_at,
                payment_start_at      = payment_start_at,
                payment_due_at        = payment_due_at,
                cart_setting_id       = cart_setting.id,
                attributes            = attributes
                )
        else:
            if attributes is not None and cart.attributes != attributes:
                raise self.exc_factory(u'同じキーを持つエントリの間で属性値に相違があります')

        return cart

    def get_ordered_product(self, row, order_no_or_key, proto_order, product):
        ordered_product_for_product = self.ordered_product_for_order_and_product.get(order_no_or_key)
        if ordered_product_for_product is None:
            ordered_product_for_product = self.ordered_product_for_order_and_product[order_no_or_key] = {}
        ordered_product = ordered_product_for_product.get(product.id)
        price = self.parse_decimal(row.get(u'ordered_product.price'), u'商品単価が不正です')
        if price is None:
            price = product.price
        quantity = self.parse_int(row.get(u'ordered_product.quantity'), u'商品個数が不正です')
        if quantity is None:
            raise self.exc_factory(u'商品個数が指定されていません')
        if ordered_product is None:
            ordered_product = ordered_product_for_product[product.id] = OrderedProduct(
                proto_order           = proto_order,
                price                 = price,
                quantity              = quantity,
                product               = product
                )
        else:
            if price != ordered_product.price:
                raise self.exc_factory(u'同じ商品で価格が一致していない行があります (%s != %s)' % (price, ordered_product.price))
            if quantity != ordered_product.quantity:
                raise self.exc_factory(u'同じ商品で個数が一致していない行があります (%s != %s)' % (quantity, ordered_product.quantity))
        return ordered_product

    def get_ordered_product_item(self, row, ordered_product, product_item):
        ordered_product_item_for_product_item = self.ordered_product_item_for_ordered_product_and_product_item.get(ordered_product)
        if ordered_product_item_for_product_item is None:
            ordered_product_item_for_product_item = self.ordered_product_item_for_ordered_product_and_product_item[ordered_product] = {}
        ordered_product_item = ordered_product_item_for_product_item.get(product_item.id) 
        price = self.parse_decimal(row.get(u'ordered_product_item.price'), u'商品明細単価が不正です')
        element_quantity_for_row = self.parse_int(row.get(u'ordered_product_item.quantity'), u'商品明細個数が不正です')
        if element_quantity_for_row is None:
            raise self.exc_factory(u'商品明細個数が指定されていません')
        if ordered_product_item is None:
            if price is None:
                price = product_item.price
            ordered_product_item = ordered_product_item_for_product_item[product_item.id] = OrderedProductItem(
                ordered_product = ordered_product,
                price           = price,
                quantity        = element_quantity_for_row,
                product_item    = product_item
                )
        else:
            if price != ordered_product_item.price:
                raise self.exc_factory(u'同じ商品明細で価格が一致していない行があります (%s != %s)' % (price, ordered_product_item.price))
            ordered_product_item.quantity += element_quantity_for_row
        return ordered_product_item, element_quantity_for_row

    def get_serial(self, element):
        next_serial = self.serial_for_element[element] = self.serial_for_element.get(element, -1) + 1
        return next_serial

    def create_shipping_address(self, row, user):
        # すべてのレコードがないときは省略されたとみなす
        unspecified = True
        record = {}
        for k1, desc in six.iteritems(self.shipping_address_record_key_map):
            k2 = desc['key']
            v = row.get(k2)
            if v is not None:
                v = v.strip()
            else:
                v = u''
            if v:
                unspecified = False
            record[k1] = v
        if unspecified:
            return None

        # バリデーション (もうちょっと頑張った方が良い)
        for k1, desc in six.iteritems(self.shipping_address_record_key_map):
            if desc['required'] and not record[k1]:
                raise self.exc_factory(u'「%s」が指定されていません' % japanese_columns[desc['key']])

        record['zip'] = record['zip'].replace('-', '')
        try:
            record['sex'] = int(record['sex'])
        except (TypeError, ValueError):
            record['sex'] = None

        shipping_address    = ShippingAddress(
            user_id         = user.id if user else None,
            first_name      = record['first_name'],
            last_name       = record['last_name'],
            first_name_kana = record['first_name_kana'],
            last_name_kana  = record['last_name_kana'],
            zip             = record['zip'],
            country         = record['country'],
            prefecture      = record['prefecture'],
            city            = record['city'],
            address_1       = record['address_1'],
            address_2       = record['address_2'],
            tel_1           = record['tel_1'],
            tel_2           = record['tel_2'],
            fax             = record['fax'],
            email_1         = record['email_1'],
            email_2         = record['email_2'],
            sex             = record['sex'],
            )
        return shipping_address

    def get_event(self, row):
        event_title = row.get(u'event_title')
        if event_title is not None:
            event_title = event_title.strip()
        if not event_title:
            return self.event
        retval = self.events.get(event_title)
        if retval is not None:
            return retval
        q = self.session.query(Event) \
            .filter(Event.organization == self.organization) \
            .filter(Event.title == event_title)
        try:
            self.events[event_title] = retval = q.one()
        except NoResultFound:
            raise self.exc_factory(u'イベントがありません  イベント名: %s' % (event_title,))
        except MultipleResultsFound:
            raise self.exc_factory(u'複数の候補があります  イベント名: %s' % (event_title,))
        return retval

    def get_performance(self, row, event):
        performance_name = row.get(u'performance.name')
        if performance_name is not None:
            performance_name = performance_name.strip()
        performance_code = row.get(u'performance.code')
        if performance_code is not None:
            performance_code = performance_code.strip()
        if not performance_name and not performance_code:
            return self.performance
        performance_date = row.get(u'performance.start_on')
        _performance_date = self.parse_date(performance_date, u'公演日が不正です', as_datetime=False)
        key = u'%s:%s:%s' % (performance_name, performance_code, repr(_performance_date))
        retval = self.performances.get(key)
        if retval is not None:
            return retval
        q = self.session.query(Performance) \
            .join(Performance.event) \
            .filter(Event.organization == self.organization)
        if event is not None:
            q = q.filter(Performance.event == event)
        if performance_code:
            q = q.filter(Performance.code == performance_code)
        else:
            if performance_name:
                q = q.filter(Performance.name == performance_name)
            if _performance_date:
                if isinstance(_performance_date, datetime):
                    q = q.filter(Performance.start_on == _performance_date)
                elif isinstance(_performance_date, date):
                    q = q.filter(sql_expr.func.DATE(Performance.start_on) == _performance_date)
                elif isinstance(_performance_date, time):
                    q = q.filter(sql_expr.func.TIME(Performance.start_on) == _performance_date)
        try:
            retval = q.one()
        except NoResultFound:
            raise self.exc_factory(u'公演がありません  公演名: %s, 公演コード: %s, 公演日: %s' % (performance_name, performance_code, performance_date))
        except MultipleResultsFound:
            raise self.exc_factory(u'複数の候補があります  公演名: %s, 公演コード: %s, 公演日: %s' % (performance_name, performance_code, performance_date))
        if performance_name is not None and retval.name != performance_name:
            raise self.exc_factory(u'公演名が違います  公演名: %s != %s, 公演コード: %s, 公演日: %s' % (performance_name, retval.name, performance_code, performance_date))
        if _performance_date and not date_time_compare(_performance_date, retval.start_on):
            raise self.exc_factory(u'公演日が違います  公演名: %s, 公演コード: %s, 公演日: %s != %s' % (performance_name, performance_code, performance_date, self.date_time_formatter.format_datetime(retval.start_on) if retval.start_on else u'-'))
        self.performances[key] = retval
        return retval

    def get_sales_segment(self, row, performance):
        ssg_name = row.get(u'ordered_product.product.sales_segment.sales_segment_group.name')
        lot_name = row.get(u'order.created_from_lot_entry.lot.name', u'').strip()

        q = self.session.query(SalesSegment).join(SalesSegmentGroup).join(Event) \
            .filter(SalesSegmentGroup.name == ssg_name) \
            .filter(Event.organization == self.organization)
        if lot_name:
            q = q.join(
                Lot,
                sql_expr.and_(
                    Lot.sales_segment_id == SalesSegment.id,
                    Lot.deleted_at == None
                    )
                ) \
                .filter(Lot.name == lot_name)
        else:
            if performance is not None:
                q = q.filter(SalesSegment.performance == performance)

        if self.event is not None:
            q = q.filter(SalesSegmentGroup.event == self.event)
        try:
            sales_segment = q.one()
        except NoResultFound:
            raise self.exc_factory(u'販売区分がありません  販売区分グループ名: %s' % ssg_name)
        except MultipleResultsFound:
            raise self.exc_factory(u'候補の販売区分が複数あります  販売区分グループ名: %s' % ssg_name)
        return sales_segment

    def get_payment_method(self, row):
        name = row.get(u'payment_method.name', u'').strip()
        if name:
            payment_method = self.payment_methods.get(name)
            if payment_method is None:
                try:
                    payment_method = self.payment_methods[name] =self.session.query(PaymentMethod) \
                        .filter(PaymentMethod.organization_id == self.organization.id) \
                        .filter(PaymentMethod.name == name) \
                        .one()
                except MultipleResultsFound:
                    raise self.exc_factory(u'「%s」という決済方法が複数あります' % name)
                except NoResultFound:
                    raise self.exc_factory(u'決済方法「%s」は存在しません' % name)
            return payment_method
        else:
            if self.default_payment_method is None:
                raise self.exc_factory(u'決済方法が指定されていません')
            return self.default_payment_method

    def get_delivery_method(self, row):
        name = row.get(u'delivery_method.name', u'').strip()
        if name:
            delivery_method = self.delivery_methods.get(name)
            if delivery_method is None:
                try:
                    delivery_method = self.delivery_methods[name] =self.session.query(DeliveryMethod) \
                        .filter(DeliveryMethod.organization_id == self.organization.id) \
                        .filter(DeliveryMethod.name == name) \
                        .one()
                except MultipleResultsFound:
                    raise self.exc_factory(u'「%s」という引取方法が複数あります' % name)
                except NoResultFound:
                    raise self.exc_factory(u'引取方法「%s」は存在しません' % name)
            return delivery_method
        else:
            if self.default_delivery_method is None:
                raise self.exc_factory(u'引取方法が指定されていません')
            return self.default_delivery_method

    def get_pdmp(self, row, sales_segment):
        payment_method = self.get_payment_method(row)
        delivery_method = self.get_delivery_method(row)
        try:
            pdmp = self.session.query(PaymentDeliveryMethodPair) \
                .join(SalesSegment_PaymentDeliveryMethodPair) \
                .filter(SalesSegment_PaymentDeliveryMethodPair.c.sales_segment_id == sales_segment.id) \
                .filter(PaymentDeliveryMethodPair.payment_method == payment_method) \
                .filter(PaymentDeliveryMethodPair.delivery_method == delivery_method) \
                .one()
        except NoResultFound:
            raise self.exc_factory(u'販売区分「%s」(id=%ld) に決済引取方法がありません  決済方法: %s  引取方法: %s' % (sales_segment.sales_segment_group.name, sales_segment.id, payment_method.name, delivery_method.name))
        except MultipleResultsFound:
            raise self.exc_factory(u'候補の決済引取方法が複数あります  決済方法: %s  引取方法: %s' % (payment_method.name, delivery_method.name))
        return pdmp

    def get_user(self, row):
        auth_identifier = row.get(u'user_credential.auth_identifier')
        membership_name = row.get(u'membership.name')
        membergroup_name = row.get(u'membergroup.name', '')
        if not membership_name:
            return None, None, None

        membership = None
        membergroup = None
        credential = None

        try:
            q = self.session.query(Membership) \
                .filter(Membership.name == membership_name) \
                .filter(Membership.organization_id == self.organization.id)
            membership = q.one()
        except NoResultFound:
            raise self.exc_factory(u'会員種別が見つかりません (membership_name=%s)' % membership_name)

        if membergroup_name:
            try:
                q = self.session.query(MemberGroup) \
                    .filter(MemberGroup.name == membergroup_name) \
                    .filter(MemberGroup.membership_id == membership.id)
                membergroup = q.one()
            except NoResultFound:
                raise self.exc_factory(u'会員グループが見つかりません (membergroup_name=%s)' % membergroup_name)

        if auth_identifier: # 空欄は未指定であるので、is not None ではない
            try:
                q = self.session.query(UserCredential) \
                    .filter(
                        UserCredential.auth_identifier == auth_identifier,
                        UserCredential.membership_id == membership.id
                        )
                if membergroup is not None: 
                    q = q.join(Member, (Member.user_id == UserCredential.user_id) & (Member.membergroup_id == membergroup.id))
                credential = q.one()
            except NoResultFound:
                raise self.exc_factory(u'ユーザが見つかりません (membership_name=%s, auth_identifier=%s)' % (membership_name, auth_identifier))
        return membership, membergroup, (credential.user if credential else None)

    def get_product(self, row, sales_segment, performance):
        product_name = row.get(u'ordered_product.product.name')
        try:
            q = self.session.query(Product) \
                .filter(
                    Product.sales_segment_id == sales_segment.id,
                    Product.name == product_name
                    )
            if performance is not None:
                q = q.join(Product.sales_segment).filter(SalesSegment.performance_id == performance.id)
            product = q.one()
        except NoResultFound:
            raise self.exc_factory(u'商品がありません  商品: %s 販売区分: %s' % (product_name, sales_segment.sales_segment_group.name))
        except MultipleResultsFound:
            logger.info(u'multiple product for the name %s found (sales_segment_id=%d)' % (product_name, sales_segment.id))
            raise self.exc_factory(u'候補の商品が複数あります  商品: %s 販売区分: %s' % (product_name, sales_segment.sales_segment_group.name))
        return product

    def get_product_item(self, row, product):
        product_item_name = row.get(u'ordered_product_item.product_item.name')
        try:
            product = self.session.query(ProductItem) \
                .filter(
                    ProductItem.product_id == product.id,
                    ProductItem.name == product_item_name
                    ) \
                .one()
        except NoResultFound:
            raise self.exc_factory(u'商品明細がありません  商品明細: %s' % product_item_name)
        except MultipleResultsFound, e:
            raise self.exc_factory(u'候補の商品明細が複数あります  商品明細: %s' % product_item_name)
        return product

    def get_venue(self, performance_id):
        venue = self.venues.get(performance_id)
        if venue is None:
            venue = self.venues[performance_id] = self.session.query(Venue).filter_by(performance_id=performance_id).one()
        return venue

    def get_seat(self, seat_name, product_item):
        venue = self.get_venue(product_item.stock.performance_id)
        seats = self.session.query(Seat) \
            .options(joinedload(Seat.status_)) \
            .filter(
                Seat.venue_id == venue.id,
                Seat.name == seat_name
                ) \
            .all()
        if len(seats) == 0:
            raise self.exc_factory(u'座席がありません  座席: %s' % seat_name)
        elif len(seats) == 1:
            if seats[0].stock_id != product_item.stock_id:
                if seats[0].stock.stock_type is None:
                    raise self.exc_factory(u'座席「%s」は未配席です。「%s」として配席してください' % (seat_name, product_item.stock.stock_type.name))
                else:
                    raise self.exc_factory(u'座席「%s」の席種「%s」は商品明細に紐づいている席種「%s」であるべきです' % (seat_name, seats[0].stock.stock_type.name, product_item.stock.stock_type.name))
            return seats[0]
        elif len(seats) > 1:
            seats = [seat for seat in seats if seat.stock_id == product_item.stock_id]
            if len(seats) > 1:
                raise self.exc_factory(u'候補の座席が複数あります  座席: %s' % seat_name)
            else:
                return seats[0]
        assert False # never get here

    def get_cart_setting(self, row, event):
        name = row.get(u'order.cart_setting_id', u'').strip()
        cart_setting = None
        if name:
            try:
                cart_setting = cart_api.get_cart_setting_by_name(None, name, organization_id=self.organization.id, session=self.session)
            except NoResultFound:
                pass
            except MultipleResultsFound:
                raise self.exc_factory(u'同名のカート設定が複数あります: %s' % name)
        else:
            if event is not None and event.setting is not None and event.setting.cart_setting_id is not None:
                cart_setting_id = event.setting.cart_setting_id
            else:
                cart_setting_id = self.organization.setting.cart_setting_id
            cart_setting = cart_api.get_cart_setting(None, cart_setting_id, session=self.session)
        if cart_setting is None:
            raise self.exc_factory(u'カート設定が見つかりません: %s' % name)
        return cart_setting

    def get_attributes(self, row):
        retval = {}
        for k, v in row.items():
            m = re.match(self.attribute_re, k)
            if m is not None:
                retval[m.group(1)] = v
        return retval

class ImportCSVParser(object):
    def __init__(self, request, session, order_import_task, organization, performance=None, event=None, default_payment_method=None, default_delivery_method=None):
        self.request = request
        self.session = session
        self.order_import_task = order_import_task
        self.organization = organization
        self.event = event
        self.performance = performance
        self.event = event or (performance and performance.event)
        self.default_payment_method = default_payment_method
        self.default_delivery_method = default_delivery_method

    def create_context(self, exc_factory):
        return ImportCSVParserContext(
            self.request, self.session, exc_factory,
            order_import_task=self.order_import_task,
            organization=self.organization,
            performance=self.performance,
            event=self.event,
            default_payment_method=self.default_payment_method,
            default_delivery_method=self.default_delivery_method
            )

    def __call__(self, reader):
        order_no_or_key = None
        def exc(message):
            return ImportCSVParserError(order_no_or_key, message, IMPORT_ERROR, getattr(reader, 'line_num', None))
        context = self.create_context(exc)
        errors = OrderedDict()
        for row in reader:
            order_no_or_key = row.get(u'order.order_no')
            if order_no_or_key is None:
                raise ImportCSVParserError('-', u'「予約番号」の列が存在しません', IMPORT_ERROR, getattr(reader, 'line_num', None))
            order_no_or_key = order_no_or_key.strip()
            if order_no_or_key in errors:
                continue
            try:
                event = context.get_event(row)
                performance = context.get_performance(row, event)
                if self.performance is not None and performance != self.performance:
                    raise exc(u'インポート対象の公演「%s」とCSVで指定された公演「%s」が異なっています' % (self.performance.name, performance.name))
                sales_segment = context.get_sales_segment(row, performance)
                pdmp = context.get_pdmp(row, sales_segment)
                cart_setting = context.get_cart_setting(row, event)
                attributes = context.get_attributes(row)
                if not attributes:
                    # 目下、購入情報属性の指定が1つもない場合は、属性を空にするのではなく元のOrderから属性を引き継ぐようにする
                    attributes = None
                cart = context.get_proto_order(row, order_no_or_key, performance, sales_segment, pdmp, cart_setting, attributes)
                product = context.get_product(row, cart.sales_segment, performance)
                item = context.get_ordered_product(row, order_no_or_key, cart, product)
                product_item = context.get_product_item(row, product)
                element, element_quantity_for_row = context.get_ordered_product_item(row, item, product_item)
                seat_name = row.get(u'seat.name')
                if seat_name is not None:
                    seat_name = seat_name.strip()
                seat = None
                if not product_item.stock.stock_type.quantity_only:
                    if self.order_import_task.allocation_mode == AllocationModeEnum.NoAutoAllocation.v:
                        if not seat_name:
                            raise exc(u'席種「%s」は数受けではありませんが、座席番号が指定されていません' % product_item.stock.stock_type.name)
                        seat = context.get_seat(seat_name, product_item)
                        if seat in element.seats:
                            raise exc(u'すでに同じ座席番号の座席が追加されています (%s)' % seat)
                        element.seats.append(seat)
                else:
                    if seat_name:
                        raise exc(u'席種「%s」は数受けですが、座席番号が指定されています' % product_item.stock.stock_type.name)
                for i in range(element_quantity_for_row):
                    serial = context.get_serial(element)
                    if len(element.tokens) >= product_item.quantity * item.quantity:
                        raise exc(u'商品「%s」の商品明細「%s」の数量 %d × 商品個数 %d を超える数のデータが存在します' % (product.name, product_item.name, product_item.quantity, item.quantity))
                    element.tokens.append(
                        OrderedProductItemToken(
                            serial=serial,
                            valid=True,
                            seat=seat
                            )
                        )
            except ImportCSVParserError as e:
                logger.info(u'%s' % e)
                context.carts.pop(order_no_or_key, None)
                errors[order_no_or_key] = e
                continue
        return context.carts, errors


class OrderImporter(object):
    def __init__(self, request, import_type, allocation_mode=AllocationModeEnum.AlwaysAllocateNew.v, entrust_separate_seats=False, merge_order_attributes=False, session=None, now=None):
        self.request = request
        self.import_type = int(import_type)
        self.allocation_mode = int(allocation_mode)
        self.entrust_separate_seats = entrust_separate_seats
        self.merge_order_attributes = merge_order_attributes
        self.session = session
        if now is None:
            now = datetime.now()
        self.now = now

    def pass2(self, carts, order_import_task):
        """ImportCSVParserによってできたProtoOrder-OrderedProduct-OrderedProductItemのツリーを検証したりする"""
        sum_quantity = dict()
        ref = None
        cart = None
        carts_to_be_imported = []
        errors = OrderedDict()
        refs_excluded = set()
        no_update = order_import_task.import_type & (ImportTypeEnum.Create.v | ImportTypeEnum.Update.v) == ImportTypeEnum.Create.v

        def add_error(message, level=IMPORT_ERROR):
            logger.info('%s: %s' % (ref, message))
            errors_for_order = errors.get(ref)
            if errors_for_order is None:
                errors_for_order = errors[ref] = []
            errors_for_order.append(ImporterValidationError(ref, message, level))
            if level > IMPORT_WARNING:
                refs_excluded.add(ref)

        original_order_nos = set(cart.original_order.order_no for cart in carts.values() if cart.original_order is not None)

        for ref, cart in carts.items():
            if cart.new_order_created_at is None:
                cart.new_order_created_at = self.now
            dummy_cart = DummyCart(cart)
            # 合計金額
            if cart.total_amount is None:
                # 合計金額が指定されていない場合は新たに計算してその値をセットする
                cart.total_amount = dummy_cart.total_amount
            else:
                if cart.total_amount != dummy_cart.total_amount:
                    add_error(u'合計金額が正しくありません (%s であるべきですが %s となっています)' % (dummy_cart.total_amount, cart.total_amount))

            # 手数料
            # 合計が指定されていない場合は新たに計算してその値をセットする
            # システム手数料
            if cart.system_fee is None:
                cart.system_fee = dummy_cart.system_fee
            else:
                if cart.system_fee != dummy_cart.system_fee:
                    add_error(u'システム手数料が正しくありません (%s であるべきですが %s となっています)' % (dummy_cart.system_fee, cart.system_fee))

            # 特別手数料
            if cart.special_fee is None:
                cart.special_fee = dummy_cart.special_fee
            else:
                if cart.special_fee != dummy_cart.special_fee:
                    add_error(u'特別手数料が正しくありません (%s であるべきですが %s となっています)' % (dummy_cart.special_fee, cart.special_fee))

            # 決済手数料
            if cart.transaction_fee is None:
                cart.transaction_fee = dummy_cart.transaction_fee
            else:
                if cart.transaction_fee != dummy_cart.transaction_fee:
                    add_error(u'決済手数料が正しくありません (%s であるべきですが %s となっています)' % (dummy_cart.transaction_fee, cart.transaction_fee))

            # 配送手数料
            if cart.delivery_fee is None:
                cart.delivery_fee = dummy_cart.delivery_fee
            else:
                if cart.delivery_fee != dummy_cart.delivery_fee:
                    add_error(u'配送手数料が正しくありません (%s であるべきですが %s となっています)' % (dummy_cart.delivery_fee, cart.delivery_fee))

            # 発券開始日時 / 発券終了日時 / 支払開始日時 / 支払終了日時
            if cart.issuing_start_at is None:
                cart.issuing_start_at = dummy_cart.issuing_start_at
                logger.info(u'issuing_start_at=%s' % (cart.issuing_start_at.strftime("%Y-%m-%d %H:%M:%S") if cart.issuing_start_at else u'-'))
            if cart.issuing_end_at is None:
                cart.issuing_end_at = dummy_cart.issuing_end_at
                logger.info(u'issuing_end_at=%s' % (cart.issuing_end_at.strftime("%Y-%m-%d %H:%M:%S") if cart.issuing_end_at else u'-'))
            if cart.payment_start_at is None:
                cart.payment_start_at = dummy_cart.payment_start_at
                logger.info(u'payment_start_at=%s' % (cart.payment_start_at.strftime("%Y-%m-%d %H:%M:%S") if cart.payment_start_at else u'-'))
            if cart.payment_due_at is None:
                cart.payment_due_at = dummy_cart.payment_due_at
                logger.info(u'payment_due_at=%s' % (cart.payment_due_at.strftime("%Y-%m-%d %H:%M:%S") if cart.payment_due_at else u'-'))

            # 商品明細の価格や個数の検証
            for cp in cart.items:
                if (cp.price * cp.quantity) != sum([cpi.price * cpi.quantity for cpi in cp.elements]):
                    add_error(u'商品「%s」の商品単価または商品個数が正しくありません' % cp.product.name)

            for cp in cart.items:
                product_item_to_element_map = {}
                for cpi in cp.elements:
                    product_item = cpi.product_item
                    stock = product_item.stock
                    prev_element = product_item_to_element_map.get(product_item.id)
                    if prev_element is not None:
                        add_error(
                            u'商品「%s」の同じ商品明細「%s」(id=%s) に紐づく要素が複数存在しています' % (
                                product_item.product.name,
                                product_item.name,
                                product_item.id
                                )
                            )
                    product_item_to_element_map[product_item.id] = cpi
                    if no_update:
                        # 在庫数
                        # - ここでは在庫総数のチェックのみ
                        # - 実際に配席しないと連席判定も含めた在庫の過不足は分からない為
                        # - 予約の更新の場合は在庫引当の検証を行わない
                        quantity_for_stock = sum_quantity.setdefault(stock.id, 0)
                        quantity_for_stock += cpi.quantity
                        if stock.stock_status.quantity < quantity_for_stock:
                            logger.info('cannot allocate quantity rest=%s (stock_id=%s, quantity=%s)' %
                                        (stock.stock_status.quantity, stock.id, cpi.quantity))
                            add_error(u'配席可能な座席がありません  商品明細: %s  個数: %s  (stock_id: %s)' %\
                                           (product_item.name, cpi.quantity, stock.id))
                        else:
                            sum_quantity[stock.id] = quantity_for_stock

                    # 座席状態のチェック
                    if not stock.stock_type.quantity_only:
                        if len(cpi.seats) > cpi.quantity:
                            add_error(u'商品明細数よりも座席数が多くなっています (座席数=%d 商品明細数=%d)' % (len(cpi.seats), cpi.quantity))
                        elif len(cpi.seats) < cpi.quantity:
                            if self.allocation_mode == AllocationModeEnum.NoAutoAllocation.v:
                                add_error(u'商品明細数と座席数が一致していません (座席数=%d 商品明細数=%d)' % (len(cpi.seats), cpi.quantity))
                            else:
                                if len(cpi.seats) > 0:
                                    add_error(u'自動配席が有効になっていて、かつ一部の座席が指定されています。指定のない座席は自動的に決定されます。 (座席数=%d 商品明細数=%d)' % (len(cpi.seats), cpi.quantity), level=IMPORT_WARNING)
                                else:
                                    if cart.original_order is not None:
                                        add_error(u'座席は自動的に決定されます (予定配席数=%d)' % (cpi.quantity,), level=IMPORT_WARNING)

                        for seat in cpi.seats:
                            if seat.status == SeatStatusEnum.Ordered.v:
                                order = self.session.query(Order) \
                                    .join(Order.items) \
                                    .join(OrderedProduct.elements) \
                                    .join(OrderedProductItem.seats) \
                                    .filter(Seat.id == seat.id) \
                                    .filter(Order.canceled_at == None) \
                                    .first()
                                if order != cart.original_order:
                                    if order is not None:
                                        if order.order_no not in original_order_nos:
                                            add_error(u'座席「%s」(id=%ld, l0_id=%s) は予約 %s に配席済みです' % (seat.name, seat.id, seat.l0_id, order.order_no))
                                    else:
                                        add_error(u'座席「%s」(id=%ld, l0_id=%s) は配席済みです' % (seat.name, seat.id, seat.l0_id))
                            elif seat.status in (SeatStatusEnum.InCart.v, SeatStatusEnum.Keep.v):
                                add_error(u'座席「%s」(id=%ld, l0_id=%s) はカートに入っています' % (seat.name, seat.id, seat.l0_id))
                            elif seat.status != SeatStatusEnum.Vacant.v:
                                add_error(u'座席「%s」(id=%ld, l0_id=%s) は選択できません' % (seat.name, seat.id, seat.l0_id))

                for product_item in cp.product.items:
                    cpi = product_item_to_element_map.get(product_item.id)
                    if cpi is None:
                        add_error(
                            u'商品「%s」の商品明細「%s」 (id=%s) に対応する要素が存在しません」' % (
                                product_item.product.name,
                                product_item.name,
                                product_item.id
                                )
                            )

            for plugin in lookup_plugin(self.request, cart.payment_delivery_pair):
                if plugin is None:
                    continue
                try:
                    plugin.validate_order(self.request, cart, update=(cart.original_order is not None))
                except OrderLikeValidationFailure as e:
                    add_error(u'「%s」の入力値が不正です (%s)' % (japanese_columns[e.path], e.message))

            # エラーがなければインポート対象に
            if ref not in refs_excluded:
                cart.order_import_task = order_import_task
                carts_to_be_imported.append(cart)
        return carts_to_be_imported, errors

    def __call__(self, reader, operator, organization, performance=None, event=None):
        task = OrderImportTask(
            operator=operator,
            status=ImportStatusEnum.ConfirmNeeded.v,
            performance=performance,
            organization=organization,
            import_type=self.import_type,
            allocation_mode=self.allocation_mode,
            entrust_separate_seats=self.entrust_separate_seats,
            merge_order_attributes=self.merge_order_attributes,
            data=u'{}',
            errors=u'{}',
            count=0
            )
        parser = ImportCSVParser(self.request, self.session, task, organization, performance=performance, event=event)
        carts, parser_errors = parser(reader) # この時点での carts はエラーが出たものも含め全部
        carts, validation_errors = self.pass2(carts, task) # ここで carts はインポート可能なものに絞られる

        # パーサーのエラーとバリデーションエラーを合体
        combined_errors = OrderedDict((ref, [error]) for ref, error in six.iteritems(parser_errors))
        for ref, errors in six.iteritems(validation_errors):
            errors_for_order = combined_errors.get(ref)
            if errors_for_order is None:
                errors_for_order = combined_errors[ref] = []
            errors_for_order.extend(errors)

        task.count = len(carts)
        return task, combined_errors


def initiate_import_task(request, task, session_for_task):
    from altair.app.ticketing.models import DBSession
    logging.info('starting order_import_task (%s)...' % task.id)
    errors_dict = None
    try:
        task_ = DBSession.query(OrderImportTask).filter_by(id=task.id).one()
        errors = run_import_task(request, task_)
        if errors is None:
            transaction.commit()
            task.status = ImportStatusEnum.Imported.v
        else:
            transaction.abort()
            errors_dict = dict(
                (ref, (errors_for_order[0].order_no, [error.message for error in errors_for_order]))
                for ref, errors_for_order in six.iteritems(errors)
                )
            task.status = ImportStatusEnum.Aborted.v
        logging.info('order_import_task (%s) ended with %s errors' % (task.id, (unicode(len(errors_dict)) if errors_dict else u'no')))
    except Exception as e:
        logging.exception('order_import_task(%s) aborted: %s' % (task.id, e))
        task.status = ImportStatusEnum.Aborted.v
    finally:
        if errors_dict:
            task.errors = json.dumps(errors_dict)
            for ref, (order_no, errors_for_order) in six.iteritems(errors_dict):
                try:
                    proto_order = session_for_task.query(ProtoOrder).filter_by(order_import_task=task, ref=ref).one()
                    attributes = proto_order.attributes
                    if attributes is None:
                        attributes = proto_order.attributes = {}
                    attributes.setdefault('errors', []).extend(errors_for_order)
                    session_for_task.add(proto_order)
                except:
                    logger.exception(ref)
        else:
            task.errors = None
        session_for_task.commit()

def run_import_task(request, task):
    from altair.app.ticketing.models import DBSession
    reserving = cart_api.get_reserving(request)
    stocker = cart_api.get_stocker(request)

    def add_note(proto_order, order):
        note = re.split(ur'\r\n|\r|\n', order.note)
        # これは実時間でよいような
        imported_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if proto_order.original_order is None or proto_order.order_no != proto_order.original_order.order_no:
            note.append(u'CSVファイル内の予約番号 (グループキー): %s' % proto_order.ref)
        note.append(u'インポート日時: %s' % imported_at)
        order.note = u'\n'.join(note)
        # 決済日時はコンビニ決済でないなら維持 (これは同じ処理を他でやっているはずなので必要ないかも)
        payment_plugin_id = order.payment_delivery_pair.payment_method.payment_plugin_id
        if payment_plugin_id != payments_plugins.SEJ_PAYMENT_PLUGIN_ID:
            order.paid_at = proto_order.new_order_paid_at

    try:
        create_or_update_orders_from_proto_orders(
            request,
            reserving=reserving,
            stocker=stocker,
            proto_orders=task.proto_orders,
            import_type=task.import_type,
            allocation_mode=task.allocation_mode,
            entrust_separate_seats=task.entrust_separate_seats,
            order_modifier=add_note,
            channel_for_new_orders=ChannelEnum.IMPORT.v
            )
    except MassOrderCreationError as e:
        return e.errors
    return None
