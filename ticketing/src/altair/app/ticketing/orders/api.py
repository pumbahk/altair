# encoding: utf-8

import logging
import re
import json
import itertools
import transaction
from decimal import Decimal
from datetime import date, datetime
from dateutil.parser import parse as parsedate

from sqlalchemy.sql.expression import and_, or_, desc
from sqlalchemy.sql import functions as safunc
from sqlalchemy import orm
from pyramid.interfaces import IRequest
from pyramid.i18n import TranslationString as _

from altair.viewhelpers.datetime_ import create_date_time_formatter

from altair.app.ticketing.models import DBSession, asc_or_desc
from altair.app.ticketing.utils import todatetime
from altair.app.ticketing.core.models import (
    Venue,
    Product,
    ProductItem,
    SalesSegment,
    SalesSegmentGroup,
    PaymentMethod,
    PaymentDeliveryMethodPair,
    DeliveryMethod,
    ShippingAddress,
    Seat,
    Stock,
    Performance,
    SeatStatusEnum,
    ChannelEnum,
    )
from altair.app.ticketing.core import api as core_api
from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.checkout import api as checkout_api
from altair.app.ticketing.cart.stocker import (
    NotEnoughStockException,
    InvalidProductSelectionException,
    )
from altair.app.ticketing.cart.reserving import (
    NotEnoughAdjacencyException,
    InvalidSeatSelectionException,
    )
from altair.app.ticketing.cart.models import (
    Cart,
    CartedProduct,
    CartedProductItem,
    )
from altair.app.ticketing.users.models import (
    User,
    UserCredential,
    )
from altair.app.ticketing.sej.models import (
    SejOrder,
    )
from altair.app.ticketing.payments.payment import Payment
from altair.app.ticketing.payments.api import lookup_plugin, get_payment_delivery_plugin, get_payment_plugin, get_delivery_plugin
from altair.app.ticketing.payments.interfaces import IPaymentCart
from altair.app.ticketing.payments.exceptions import (
    OrderLikeValidationFailure,
    PaymentDeliveryMethodPairNotFound,
    PaymentPluginException,
    CancellationValidationFailure
    )
from altair.app.ticketing.payments import plugins as payments_plugins
from altair.multicheckout.util import get_multicheckout_ahead_com_name
from altair.multicheckout.models import MultiCheckoutStatusEnum
from altair.multicheckout.api import get_multicheckout_3d_api
from .models import (
    Order,
    OrderedProduct,
    OrderedProductItem,
    OrderedProductItemToken,
    OrderAttribute,
    OrderSummary,
    ProtoOrder,
    ImportTypeEnum,
    )
from .interfaces import IOrderDescriptorRegistry, IOrderDescriptorRenderer
## backward compatibility
from altair.app.ticketing.orders.models import OrderedProductAttribute
from .metadata import (
    METADATA_NAME_ORDERED_PRODUCT,
    METADATA_NAME_ORDER
)
from .exceptions import OrderCreationError, MassOrderCreationError, OrderCancellationError
from functools import partial

logger = logging.getLogger(__name__)


class QueryBuilderError(Exception):
    pass

def must_be_combined_with(*params):
    def _(fn):
        name = fn.func_name[1:]
        def wrapper(self, *args, **kwargs):
            if not any(param in self.formdata and self.formdata[param] for param in params):
                if self.key_name_resolver is None:
                    raise QueryBuilderError
                else:
                    raise QueryBuilderError(u'検索に時間がかかるため、%sは必ず%sと一緒に使ってください' % (self.key_name_resolver(name), u', '.join(self.key_name_resolver(param) for param in params)))
            return fn(self, *args, **kwargs)
        wrapper.func_name = fn.func_name
        return wrapper
    return _

def post(fn):
    def wrapper(self, query, value):
        self.post_queue.append((fn, value))
        return query
    return fn

class SearchQueryBuilderBase(object):
    def __init__(self, formdata, key_name_resolver=None, targets=None, excludes=[], sort=True):
        self.formdata = formdata
        self.key_name_resolver = key_name_resolver
        if targets:
            self.targets = targets
        self.excludes = excludes
        self.sort = sort
        self.post_queue = None

    def handle_sort(self, query):
        if self.formdata['sort']:
            try:
                query = asc_or_desc(query, getattr(self.targets['subject'], self.formdata['sort']), self.formdata['direction'], 'asc')
            except AttributeError:
                pass

        return query

    def __call__(self, query):
        self.post_queue = []
        for k, v in self.formdata.items():
            if v and k not in self.excludes:
                callable = getattr(self, '_' + k, None)
                if callable:
                    query = callable(query, v)
        for fn, value in self.post_queue:
            query = fn(self, query, value)
        if self.sort:
            query = self.handle_sort(query)
        return query

class BaseSearchQueryBuilderMixin(object):
    def _order_no(self, query, value):
        if isinstance(value, basestring):
            value = re.split(ur'[ \t　]+', value)
        return query.filter(self.targets['subject'].order_no.in_(value))

    def _performance_id(self, query, value):
        return query.filter(self.targets['subject'].performance_id == value)

    def _event_id(self, query, value):
        return query.join(self.targets['subject'].performance).filter(self.targets['Performance'].event_id == value)

    def _payment_method(self, query, value):
        query = query.join(self.targets['subject'].payment_delivery_pair)
        query = query.join(self.targets['PaymentMethod'])
        if isinstance(value, list):
            query = query.filter(self.targets['PaymentMethod'].id.in_(value))
        else:
            query = query.filter(self.targets['PaymentMethod'].id == value)
        return query

    def _delivery_method(self, query, value):
        query = query.join(self.targets['subject'].payment_delivery_pair)
        query = query.join(self.targets['DeliveryMethod'])
        query = query.filter(self.targets['DeliveryMethod'].id.in_(value))
        return query

    def _tel(self, query, value):
        return query.join(self.targets['subject'].shipping_address) \
            .filter(or_(self.targets['ShippingAddress'].tel_1==value,
                        self.targets['ShippingAddress'].tel_2==value))

    def _name(self, query, value):
        query = query.join(self.targets['subject'].shipping_address)
        items = re.split(ur'[ \t　]+', value)
        # 前方一致で十分かと
        for item in items:
            query = query.filter(
                or_(
                    or_(self.targets['ShippingAddress'].first_name.like('%s%%' % item),
                        self.targets['ShippingAddress'].last_name.like('%s%%' % item)),
                    or_(self.targets['ShippingAddress'].first_name_kana.like('%s%%' % item),
                        self.targets['ShippingAddress'].last_name_kana.like('%s%%' % item))
                    )
                )
        return query

    def _email(self, query, value):
        query = query.join(self.targets['subject'].shipping_address)
        # 完全一致です
        return query \
            .join(self.targets['subject'].shipping_address) \
            .filter(or_(self.targets['ShippingAddress'].email_1 == value,
                        self.targets['ShippingAddress'].email_2 == value))

    def _start_on_from(self, query, value):
        return query.join(self.targets['subject'].performance).filter(self.targets['Performance'].start_on>=value)

    def _start_on_to(self, query, value):
        return query.join(self.targets['subject'].performance).filter(self.targets['Performance'].start_on<=todatetime(value).replace(hour=23, minute=59, second=59))

    def handle_sort(self, query):
        if self.formdata['sort']:
            query = super(BaseSearchQueryBuilderMixin, self).handle_sort(query)
        else:
            query = asc_or_desc(query, self.targets['subject'].order_no, 'desc')
        return query

class CartSearchQueryBuilder(SearchQueryBuilderBase, BaseSearchQueryBuilderMixin):
    targets = {
        'subject': Cart,
        'Cart': Cart,
        'CartedProduct': CartedProduct,
        'CartedProductItem': CartedProductItem,
        'Product': Product,
        'Seat': Seat,
        'Performance': Performance,
        'ShippingAddress': ShippingAddress,
        'PaymentDeliveryMethodPair': PaymentDeliveryMethodPair,
        'PaymentMethod': PaymentMethod,
        'DeliveryMethod': DeliveryMethod,
        'SalesSegment': SalesSegment,
        'SalesSegmentGroup': SalesSegmentGroup,
        }

    def _carted_from(self, query, value):
        return query.filter(self.targets['subject'].created_at >= value)

    def _carted_to(self, query, value):
        return query.filter(self.targets['subject'].created_at <= value)

    def _sales_segment_group_id(self, query, value):
        if value and '' not in value:
            query = query.join(self.targets['subject'].sales_segment)
            query = query.filter(self.targets['SalesSegment'].sales_segment_group_id.in_(value))
        return query

    def _sales_segment_id(self, query, value):
        if value and '' not in value:
            query = query.filter(self.targets['subject'].sales_segment_id.in_(value))
        return query

    def _seat_number(self, query, value):
        query = query.join(self.targets['Cart'].items)
        query = query.join(self.targets['CartedProduct'].elements)
        query = query.join(self.targets['CartedProductItem'].seats)
        query = query.filter(self.targets['Seat'].name.like('%s%%' % value))
        return query

    def _status(self, query, value):
        if value == 'completed':
            query = query.filter(self.targets['subject'].order_id != None)
        elif value == 'incomplete':
            query = query.filter(self.targets['subject'].order_id == None)
        return query

    def _browserid(self, query, value):
        query = query.filter(self.targets['subject'].browserid == value)
        return query


class OrderSearchQueryBuilder(SearchQueryBuilderBase, BaseSearchQueryBuilderMixin):
    targets = {
        'subject': Order,
        'Order': Order,
        'OrderedProduct': OrderedProduct,
        'OrderedProductItem': OrderedProductItem,
        'Product': Product,
        'ProductItem': ProductItem,
        'SalesSegment': SalesSegment,
        'SalesSegmentGroup': SalesSegmentGroup,
        'Seat': Seat,
        'SejOrder': SejOrder,
        'Performance': Performance,
        'ShippingAddress': ShippingAddress,
        'PaymentDeliveryMethodPair': PaymentDeliveryMethodPair,
        'PaymentMethod': PaymentMethod,
        'DeliveryMethod': DeliveryMethod,
        }

    def _ordered_from(self, query, value):
        return query.filter(self.targets['subject'].created_at >= value)

    def _ordered_to(self, query, value):
        return query.filter(self.targets['subject'].created_at <= value)

    def _status(self, query, value):
        status_cond = []
        if 'ordered' in value:
            status_cond.append(and_(self.targets['subject'].canceled_at==None, self.targets['subject'].delivered_at==None))
        if 'delivered' in value:
            status_cond.append(and_(self.targets['subject'].canceled_at==None, self.targets['subject'].delivered_at!=None))
        if 'canceled' in value:
            status_cond.append(and_(self.targets['subject'].canceled_at!=None))

        if status_cond:
            query = query.filter(or_(*status_cond))
        return query

    def _issue_status(self, query, value):
        issue_cond = []
        if 'issued' in value:
            issue_cond.append(self.targets['subject'].issued==True)
        if 'unissued' in value:
            issue_cond.append(self.targets['subject'].issued==False)

        if issue_cond:
            query = query.filter(or_(*issue_cond))
        return query

    def _sales_segment_id(self, query, value):
        if value and '' not in value:
            query = query.join(self.targets['subject'].ordered_products)
            query = query.join(self.targets['OrderedProduct'].product)
            query = query.filter(self.targets['Product'].sales_segment_id.in_(value))
        return query

    def _payment_status(self, query, value):
        payment_cond = []
        if 'unpaid' in value:
            payment_cond.append(and_(self.targets['subject'].refunded_at==None, self.targets['subject'].refund_id==None, self.targets['subject'].paid_at==None))
        if 'paid' in value:
            payment_cond.append(and_(self.targets['subject'].refunded_at==None, self.targets['subject'].refund_id==None, self.targets['subject'].paid_at!=None))
        if 'refunding' in value:
            payment_cond.append(and_(self.targets['subject'].refunded_at==None, self.targets['subject'].refund_id!=None))
        if 'refunded' in value:
            payment_cond.append(and_(self.targets['subject'].refunded_at!=None))
        if payment_cond:
            query = query.filter(or_(*payment_cond))
        return query

    def _member_id(self, query, value):
        return query.join(self.targets['subject'].user).join(User.user_credential).filter(UserCredential.auth_identifier==value)

    def _seat_number(self, query, value):
        query = query.join(self.targets['subject'].items)
        query = query.join(self.targets['OrderedProduct'].elements)
        query = query.join(self.targets['OrderedProductItem'].seats)
        query = query.filter(Seat.name.like('%s%%' % value))
        return query

    @must_be_combined_with('event_id', 'performance_id')
    def _number_of_tickets(self, query, value):
        aliased_targets = dict(
            (k, orm.aliased(v)) for k, v in self.targets.items()
            )
        minimum_price_query = query.session.query(safunc.min(aliased_targets['ProductItem'].price)).filter(aliased_targets['ProductItem'].price != 0)
        performance_id = self.formdata.get('performance_id')
        if performance_id:
            minimum_price_query = minimum_price_query \
                .join(aliased_targets['Product']) \
                .join(aliased_targets['SalesSegment']) \
                .filter(aliased_targets['SalesSegment'].performance_id == performance_id)
        else:
            event_id = self.formdata.get('event_id')
            if event_id:
                minimum_price_query = minimum_price_query \
                    .join(aliased_targets['Product']) \
                    .join(aliased_targets['SalesSegment']) \
                    .join(aliased_targets['SalesSegmentGroup']) \
                    .filter(aliased_targets['SalesSegmentGroup'].event_id == event_id)
        minimum_price = minimum_price_query.scalar()
        if minimum_price:
            query = query.filter(
                self.targets['subject'].id.in_(
                    self.__class__(self.formdata, self.key_name_resolver, aliased_targets, excludes=['number_of_tickets'], sort=False)(
                        query.session.query(aliased_targets['subject'].id) \
                            .join(aliased_targets['OrderedProduct']) \
                            .join(aliased_targets['OrderedProductItem']) \
                            .distinct()
                        ) \
                        .filter(aliased_targets['subject'].total_amount > minimum_price * value) \
                        .group_by(aliased_targets['subject'].id,
                                  aliased_targets['OrderedProductItem'].product_item_id) \
                        .having(safunc.sum(aliased_targets['OrderedProductItem'].quantity) == value) \
                    )
                )
        return query

    def _billing_or_exchange_number(self, query, value):
        query = query \
            .join(
                self.targets['SejOrder'],
                self.targets['subject'].order_no == self.targets['SejOrder'].order_no
                ) \
            .filter(or_(
                self.targets['SejOrder'].billing_number == value,
                self.targets['SejOrder'].exchange_number == value
                ))
        return query

class OrderSummarySearchQueryBuilder(SearchQueryBuilderBase):
    targets = {
        'subject': OrderSummary,
        'OrderedProduct': OrderedProduct,
        'OrderedProductItem': OrderedProductItem,
        'Product': Product,
        'ProductItem': ProductItem,
        'SalesSegment': SalesSegment,
        'SalesSegmentGroup': SalesSegmentGroup,
        'Seat': Seat,
        'SejOrder': SejOrder,
        }

    def _order_no(self, query, value):
        if isinstance(value, basestring):
            value = re.split(ur'[ \t　]+', value)
        return query.filter(self.targets['subject'].order_no.in_(value))

    def _performance_id(self, query, value):
        if isinstance(value, list):
            query = query.filter(self.targets['subject'].performance_id.in_(value))
        else:
            query = query.filter(self.targets['subject'].performance_id == value)
        return query

    def _event_id(self, query, value):
        return query.filter(self.targets['subject'].event_id == value)

    def _refund_id(self, query, value):
        return query.filter(self.targets['subject'].refund_id == value)

    def _payment_method(self, query, value):
        if isinstance(value, list):
            query = query.filter(self.targets['subject'].payment_method_id.in_(value))
        else:
            query = query.filter(self.targets['subject'].payment_method_id == value)
        return query

    def _delivery_method(self, query, value):
        query = query.filter(self.targets['subject'].delivery_method_id.in_(value))
        return query

    def _tel(self, query, value):
        return query.filter(or_(self.targets['subject'].tel_1==value,
                                self.targets['subject'].tel_2==value))

    def _name(self, query, value):
        items = re.split(ur'[ \t　]+', value)
        # 前方一致で十分かと
        for item in items:
            query = query.filter(
                or_(
                    or_(self.targets['subject'].first_name.like('%s%%' % item),
                        self.targets['subject'].last_name.like('%s%%' % item)),
                    or_(self.targets['subject'].first_name_kana.like('%s%%' % item),
                        self.targets['subject'].last_name_kana.like('%s%%' % item))
                    )
                )
        return query

    def _email(self, query, value):
        # 完全一致です
        return query \
            .filter(or_(self.targets['subject'].email_1 == value,
                        self.targets['subject'].email_2 == value))

    def _start_on_from(self, query, value):
        return query.filter(self.targets['subject'].performance_start_on>=value)

    def _start_on_to(self, query, value):
        return query.filter(self.targets['subject'].performance_start_on<=todatetime(value).replace(hour=23, minute=59, second=59))

    def _ordered_from(self, query, value):
        return query.filter(self.targets['subject'].created_at >= value)

    def _ordered_to(self, query, value):
        return query.filter(self.targets['subject'].created_at <= value)

    def _status(self, query, value):
        status_cond = []
        if 'ordered' in value:
            status_cond.append(and_(self.targets['subject'].canceled_at==None, self.targets['subject'].delivered_at==None))
        if 'delivered' in value:
            status_cond.append(and_(self.targets['subject'].canceled_at==None, self.targets['subject'].delivered_at!=None))
        if 'canceled' in value:
            status_cond.append(and_(self.targets['subject'].canceled_at!=None))

        if status_cond:
            query = query.filter(or_(*status_cond))
        return query

    def _issue_status(self, query, value):
        issue_cond = []
        if 'issued' in value:
            issue_cond.append(self.targets['subject'].issued==True)
        if 'unissued' in value:
            issue_cond.append(self.targets['subject'].issued==False)

        if issue_cond:
            query = query.filter(or_(*issue_cond))
        return query

    def _sales_segment_group_id(self, query, value):
        if value and '' not in value:
            query = query.join(self.targets['subject'].items)
            query = query.join(self.targets['OrderedProduct'].product)
            query = query.join(self.targets['Product'].sales_segment)
            query = query.filter(self.targets['SalesSegment'].sales_segment_group_id.in_(value))
        return query

    def _sales_segment_id(self, query, value):
        if value and '' not in value:
            query = query.join(self.targets['subject'].items)
            query = query.join(self.targets['OrderedProduct'].product)
            query = query.filter(self.targets['Product'].sales_segment_id.in_(value))
        return query

    def _payment_status(self, query, value):
        payment_cond = []
        if 'unpaid' in value:
            payment_cond.append(and_(self.targets['subject'].refunded_at==None, self.targets['subject'].refund_id==None, self.targets['subject'].paid_at==None))
        if 'paid' in value:
            payment_cond.append(and_(self.targets['subject'].refunded_at==None, self.targets['subject'].refund_id==None, self.targets['subject'].paid_at!=None))
        if 'refunding' in value:
            payment_cond.append(and_(self.targets['subject'].refunded_at==None, self.targets['subject'].refund_id!=None))
        if 'refunded' in value:
            payment_cond.append(and_(self.targets['subject'].refunded_at!=None))
        if payment_cond:
            query = query.filter(or_(*payment_cond))
        return query

    def _member_id(self, query, value):
        return query.filter(self.targets['subject'].auth_identifier==value)

    def _seat_number(self, query, value):
        query = query.join(self.targets['subject'].items)
        query = query.join(self.targets['OrderedProduct'].elements)
        query = query.join(self.targets['OrderedProductItem'].seats)
        query = query.filter(self.targets['Seat'].name.like('%s%%' % value))
        return query

    @must_be_combined_with('event_id', 'performance_id')
    def _number_of_tickets(self, query, value):
        aliased_targets = dict(
            (k, orm.aliased(v)) for k, v in OrderSearchQueryBuilder.targets.items()
            )
        minimum_price_query = query.session.query(safunc.min(aliased_targets['ProductItem'].price)).filter(aliased_targets['ProductItem'].price != 0)
        performance_id = self.formdata.get('performance_id')
        if performance_id:
            minimum_price_query = minimum_price_query \
                .join(aliased_targets['Product']) \
                .join(aliased_targets['SalesSegment']) \
                .filter(aliased_targets['SalesSegment'].performance_id == performance_id)
        else:
            event_id = self.formdata.get('event_id')
            if event_id:
                minimum_price_query = minimum_price_query \
                    .join(aliased_targets['Product']) \
                    .join(aliased_targets['SalesSegment']) \
                    .join(aliased_targets['SalesSegmentGroup']) \
                    .filter(aliased_targets['SalesSegmentGroup'].event_id == event_id)
        minimum_price = minimum_price_query.scalar()
        if minimum_price:
            query = query.filter(
                self.targets['subject'].id.in_(
                    OrderSearchQueryBuilder(self.formdata, self.key_name_resolver, aliased_targets, excludes=['number_of_tickets'], sort=False)(
                        query.session.query(aliased_targets['Order'].id) \
                            .join(aliased_targets['OrderedProduct']) \
                            .join(aliased_targets['OrderedProductItem']) \
                            .distinct()
                        ) \
                        .filter(aliased_targets['Order'].total_amount > minimum_price * value) \
                        .group_by(aliased_targets['Order'].id,
                                  aliased_targets['OrderedProductItem'].product_item_id) \
                        .having(safunc.sum(aliased_targets['OrderedProductItem'].quantity) >= value) \
                    )
                )
        return query

    def _billing_or_exchange_number(self, query, value):
        query = query \
            .join(
                self.targets['SejOrder'],
                self.targets['subject'].order_no == self.targets['SejOrder'].order_no
                ) \
            .filter(or_(
                self.targets['SejOrder'].billing_number == value,
                self.targets['SejOrder'].exchange_number == value
                ))
        return query

    def handle_sort(self, query):
        if self.formdata['sort']:
            query = super(OrderSummarySearchQueryBuilder, self).handle_sort(query)
        else:
            query = asc_or_desc(query, self.targets['subject'].order_no, 'desc')
        return query


def _validate_order_cancellation(request, order, now):
    """キャンセル可能かvalidationする
    :param request: リクエスト
    :param order: バリデーション対象
    :return: エラーメッセージ(list)
    """
    if not order.can_cancel():
        logger.error(
            u'予約がキャンセルできる状態ではありません (予約No: {order_no}, 予約ステータス: {status}, 支払ステータス: {payment_status})'.format(
                order_no=order.order_no,
                status=order.status,
                payment_status=order.payment_status
            )
        )
        raise

    # 各プラグイン固有のバリデーション
    payment_delivery_plugin, payment_plugin, delivery_plugin = lookup_plugin(request, order.payment_delivery_pair)
    if payment_delivery_plugin is not None:
        plugins = [payment_delivery_plugin]
    else:
        plugins = [payment_plugin, delivery_plugin]
    for plugin in plugins:
        try:
            plugin.validate_order_cancellation(request, order, now)
        except CancellationValidationFailure as e:
            raise


def cancel_order(request, order, now=None):
    """
    Orderをキャンセル状態にする。（決済キャンセル、在庫解放含む）
    :param request: リクエスト
    :param order: キャンセル対象
    :param now: キャンセル時刻
    :return: 注意メッセージ(list)（例外ではない）
    """
    logger.info('canceling order: %s' % order.order_no)
    warnings = []
    now = now or datetime.now()

    # キャンセル処理の前にvalidationする
    try:
        _validate_order_cancellation(request, order, now)
    except:
        import sys
        exc_info = sys.exc_info()
        raise OrderCancellationError(
            order.order_no,
            _(u'the order cannot be canceled. OrderStatus=${status}, PaymentStatus=${payment_status})', mapping=dict(status=order.status, payment_status=order.payment_status)).interpolate(),
            nested_exc_info=exc_info
        )

    '''
    決済方法ごとに払戻処理
    '''
    payment_delivery_plugin, payment_plugin, delivery_plugin = lookup_plugin(request, order.payment_delivery_pair)

    # インナー予約の場合はAPI決済していないのでスキップ
    # ただしコンビニ決済はインナー予約でもAPIで通知しているので処理する
    if order.is_inner_channel and order.payment_plugin_id not in (payments_plugins.SEJ_PAYMENT_PLUGIN_ID, payments_plugins.FAMIPORT_PAYMENT_PLUGIN_ID):
        warnings.append(_(u'インナー予約のキャンセルなので決済払戻処理をスキップします'))
        payment_plugin = None

    # 入金済みなら決済をキャンセル
    try:
        if payment_delivery_plugin:
            payment_delivery_plugin.cancel(request, order)
        else:
            if payment_plugin is not None:
                payment_plugin.cancel(request, order)
            if delivery_plugin is not None:
                delivery_plugin.cancel(request, order)
    except PaymentPluginException:
        logger.exception(u'キャンセルに失敗しました')
        raise

    # 在庫を戻す
    logger.info('try release stock (order_no=%s)' % order.order_no)
    order.release()
    order.mark_canceled()
    if order.payment_status == 'paid':
        order.mark_refunded()

    order.save()
    logger.info('success order cancel (order_no=%s)' % order.order_no)
    return warnings

def refund_order(request, order, payment_method=None, now=None):
    logger.info('refunding order: %s (payment method override=%s)' % (order.order_no, payment_method.payment_plugin_id if payment_method is not None else '-'))
    warnings = []
    now = now or datetime.now()
    if not order.can_refund() or order.payment_status != 'refunding':
        raise OrderCancellationError(order.order_no, _(u'予約が払戻できる状態ではありません (予約ステータス: ${status}, 支払ステータス: ${payment_status})', mapping=dict(status=order.status, payment_status=order.payment_status)).interpolate())

    '''
    決済方法ごとに払戻処理
    '''
    if payment_method:
        payment_plugin_id = payment_method.payment_plugin_id
    else:
        payment_plugin_id = order.payment_delivery_pair.payment_method.payment_plugin_id
    delivery_plugin_id = order.payment_delivery_pair.delivery_method.delivery_plugin_id

    # SEJの払戻は PaymentPlugin 単体では行われないので
    # delivery_pluginをオーバライドする...
    if payment_plugin_id == payments_plugins.SEJ_PAYMENT_PLUGIN_ID:
        delivery_plugin_id = payments_plugins.SEJ_DELIVERY_PLUGIN_ID

    if not payment_plugin_id:
        return False

    # インナー予約の場合はAPI決済していないのでスキップ
    # ただしコンビニ決済はインナー予約でもAPIで通知しているので処理する
    if order.is_inner_channel and \
       payment_plugin_id != payments_plugins.SEJ_PAYMENT_PLUGIN_ID and \
       delivery_plugin_id != payments_plugins.SEJ_DELIVERY_PLUGIN_ID:
        warnings.append(_(u'インナー予約のキャンセルなので決済払戻処理をスキップします'))

    payment_delivery_plugin = get_payment_delivery_plugin(request, payment_plugin_id, delivery_plugin_id)
    payment_plugin = get_payment_plugin(request, payment_plugin_id)
    delivery_plugin = get_delivery_plugin(request, delivery_plugin_id)
    if payment_delivery_plugin is not None:
        payment_plugin = payment_delivery_plugin
        delivery_plugin = None
    else:
        if payment_plugin is None and delivery_plugin is None:
            raise PaymentDeliveryMethodPairNotFound(u"対応する決済プラグインか配送プラグインが見つかりませんでした")

    try:
        payment_plugin.refund(request, order, order)
    except PaymentPluginException:
        logger.exception(u'キャンセルに失敗しました')
        raise

    order.mark_refunded()
    order.save()
    logger.info('success order refund (order_no=%s)' % order.order_no)
    return warnings

def call_payment_delivery_plugin(request, order_like, included_payment_plugin_ids=None, excluded_payment_plugin_ids=[]):
    payment_plugin_id = order_like.payment_delivery_pair.payment_method.payment_plugin_id
    delivery_plugin_id = order_like.payment_delivery_pair.delivery_method.delivery_plugin_id
    payment_delivery_plugin, payment_plugin, delivery_plugin = lookup_plugin(request, order_like.payment_delivery_pair)

    if payment_delivery_plugin is not None:
        payment_plugin = payment_delivery_plugin
        delivery_plugin = None
    if (included_payment_plugin_ids is not None and payment_plugin_id not in included_payment_plugin_ids) or \
       (payment_plugin_id in excluded_payment_plugin_ids):
        payment_plugin = None

    if payment_plugin is not None:
        payment_plugin.finish2(request, order_like)
    if delivery_plugin is not None:
        delivery_plugin.finish2(request, order_like)


def create_inner_order(request, order_like, note, session=None):
    if session is None:
        from altair.app.ticketing.models import DBSession
        session = DBSession

    payment = Payment(order_like, request)
    if order_like.payment_delivery_pair.payment_method.pay_at_store() or \
       order_like.payment_delivery_pair.payment_method.cash_on_reservation():
        # コンビニ決済か窓口支払か無料のみ決済処理を行う
        order = payment.call_payment()
    else:
        if IPaymentCart.providedBy(order_like):
            order = Order.create_from_cart(order_like)
            order.organization_id = order.performance.event.organization_id
            session.add(order)
        else:
            order = order_like

        # 配送手続: 以下のモデルを生成する
        # - コンビニ受取: SejOrder
        # - QR: OrderedProductItemToken
        # - 窓口: ReservedNumber
        payment.call_delivery(order)
        if IPaymentCart.providedBy(order_like):
            order_like.finish()

    order.note = note
    add_booster_attributes(request, order)
    return order

def add_booster_attributes(request, order):
    from altair.app.ticketing.cart.view_support import get_extra_form_schema, DummyCartContext
    schema = get_extra_form_schema(
        DummyCartContext(request, order),
        request,
        order.sales_segment
        )
    for field in schema:
        attribute = OrderAttribute(
            order=order,
            name=field['name'],
            value=u''
            )
        DBSession.add(attribute)

def refresh_order(request, session, order):
    logger.info('Trying to refresh order %s (id=%d, payment_delivery_pair={ payment_method=%s, delivery_method=%s })...'
                        % (order.order_no, order.id, order.payment_delivery_pair.payment_method.name, order.payment_delivery_pair.delivery_method.name))
    os = order.organization.setting
    payment_delivery_plugin, payment_plugin, delivery_plugin = lookup_plugin(request, order.payment_delivery_pair)
    if payment_delivery_plugin is not None:
        logger.info('payment_delivery_plugin.refresh')
        payment_delivery_plugin.refresh(request, order)
    else:
        logger.info('payment_plugin.refresh')
        payment_plugin.refresh(request, order)
        logger.info('delivery_plugin.refresh')
        delivery_plugin.refresh(request, order)
    logger.info('Finished refreshing order %s (id=%d)' % (order.order_no, order.id))

def recalculate_total_amount_for_order(request, order_like):
    return \
        order_like.transaction_fee + \
        order_like.delivery_fee + \
        order_like.system_fee + \
        order_like.special_fee + \
        order_like.sales_segment.get_products_amount_without_fee(
            order_like.payment_delivery_pair,
            [ (item.product, item.price, item.quantity) for item in order_like.items ]
            )

def validate_order(request, order_like, ref, update=False):
    retval = []
    sum_quantity = dict()

    # 合計金額
    calculated_total_amount = recalculate_total_amount_for_order(request, order_like)
    if order_like.total_amount != calculated_total_amount:
        retval.append(OrderCreationError(
            ref,
            order_like.order_no,
            u'合計金額が正しくありません (期待値: ${expected_amount}, 入力された数値: ${input_amount})',
            dict(
                input_amount=order_like.total_amount,
                expected_amount=calculated_total_amount
                )
            ))

    for item in order_like.items:
        product_item_element_map = {}
        for element in item.elements:
            prev_element = product_item_element_map.get(element.product_item.id)
            if prev_element is not None:
                retval.append(OrderCreationError(
                    ref,
                    order_like.order_no,
                    u'商品「${product_name}」の同じ商品明細「${product_item_name}」(id=${product_item_id}) に紐づく要素が複数存在しています',
                    dict(
                        product_name=item.product.name,
                        product_item_name=element.product_item.name,
                        product_item_id=element.product_item.id
                        )
                    ))
            product_item_element_map[element.product_item.id] = element
            if element.quantity % item.quantity != 0:
                retval.append(OrderCreationError(
                    ref,
                    order_like.order_no,
                    u'element_quantity is not a multiple of item_quantity'
                    ))

            for seat in element.seats:
                if seat.status != SeatStatusEnum.Ordered.v:
                    retval.append(OrderCreationError(
                        ref,
                        order_like.order_no,
                        u'Seat(l0_id=${l0_id}) の状態は注文済みではありませんでした (${status})',
                        dict(l0_id=repr(seat.l0_id), status=seat.status)
                        ))
        for product_item in item.product.items:
            element = product_item_element_map.get(product_item.id)
            if element is None:
                retval.append(OrderCreationError(
                    ref,
                    order_like.order_no,
                    u'商品「${product_name}」の商品明細「${product_item_name}」 (id=${product_item_id}) に対応する要素が存在しません」',
                    dict(
                        product_name=product_item.product.name,
                        product_item_name=product_item.name,
                        product_item_id=product_item.id
                        )
                    ))

    payment_delivery_plugin, payment_plugin, delivery_plugin = lookup_plugin(request, order_like.payment_delivery_pair)
    if payment_delivery_plugin is not None:
        plugins = [payment_delivery_plugin]
    else:
        plugins = [payment_plugin, delivery_plugin]
    for plugin in plugins:
        try:
            plugin.validate_order(request, order_like, update=update)
        except OrderLikeValidationFailure as e:
            from .export import japanese_columns
            retval.append(OrderCreationError(
                ref,
                order_like.order_no,
                u'「${path}」の入力値が不正です (${message})',
                dict(
                    path=japanese_columns.get(e.path, e.path),
                    message=e.message
                    )
                ))
    return retval

def get_order_by_id(request, order_id, session=None, include_deleted=False):
    if session is None:
        from altair.app.ticketing.models import DBSession
        session = DBSession
    _Order = orm.aliased(Order)
    q = session.query(Order, include_deleted=True) \
        .outerjoin(_Order, Order.order_no == _Order.order_no) \
        .filter(Order.id == order_id) \
        .order_by(desc(_Order.branch_no)) \
        .with_entities(_Order)
    if not include_deleted:
        q = q.filter(_Order.deleted_at == None)
    order = q.first()
    return order

def get_order_by_order_no(request, order_no, session=None, include_deleted=False):
    if session is None:
        from altair.app.ticketing.models import DBSession
        session = DBSession
    try:
        q = session.query(Order, include_deleted=include_deleted).filter_by(order_no=order_no)
        if include_deleted:
            q = q.options(orm.undefer(Order.deleted_at))
        q = q.order_by(desc(Order.branch_no))
        return q.first()
    except orm.exc.NoResultFound:
        return None

def create_order_from_proto_order(request, reserving, stocker, proto_order, prev_order=None, entrust_separate_seats=False, default_channel=ChannelEnum.INNER.v):
    if prev_order is not None:
        # バリデーションは最初にやる
        # そうでないと、select が走るタイミングで flush されてしまって
        # IntegrityError などになってしまう
        assert prev_order.order_no == proto_order.order_no
        assert prev_order.ordered_from == proto_order.organization

    def take_stock_and_find_out_required_seats(proto_order):
        # XXX: 商品はすべて販売区分単位となったので、performance_id は不要では?
        stock_status_pairs = stocker.take_stock(proto_order.performance_id, [(item.product, item.quantity) for item in proto_order.items])
        stock_status_for_stock = {}
        for stock_status, quantity in stock_status_pairs:
            stock_status_for_stock[stock_status.stock_id] = stock_status
        logger.debug('stock_status_pairs=%r' % stock_status_pairs)
        num_seats_required_for_stock = {}
        seats_required_for_stock = {}
        seats_required_for_element = {}
        for item in proto_order.items:
            for orig_element in item.elements:
                assert orig_element.quantity == len(orig_element.tokens), u'orig_element.id=%ld / orig_element.quantity (%d) != len(orig_element.tokens) (%d)' % (orig_element.id, orig_element.quantity, len(orig_element.tokens))
                stock = orig_element.product_item.stock
                quantity_only = stock.stock_type.quantity_only
                if not quantity_only:
                    assert orig_element.seats is not None
                    seats = orig_element.seats
                    num_seats_newly_required = len(orig_element.tokens) - len(seats)
                    logger.info('len(seats)=%d, num_seats_newly_required=%d' % (len(seats), num_seats_newly_required))
                    _seats = seats_required_for_element.get(orig_element.product_item)
                    if _seats is None:
                        seats_required_for_element[orig_element.product_item] = _seats = []
                    if len(seats) > 0:
                        reserving.reserve_selected_seats(
                            stockstatus=[(stock_status_for_stock[stock.id], len(seats))],
                            performance_id=proto_order.performance_id,
                            selected_seat_l0_ids=[seat.l0_id for seat in seats],
                            reserve_status=SeatStatusEnum.Ordered.v
                            )
                        _seats.extend(seats)
                    # もし token の数より seat の数が少なければ、おまかせで座席を取得して足す
                    if num_seats_newly_required > 0:
                        num_seats_required_for_stock[stock.id] = num_seats_required_for_stock.get(stock.id, 0) + num_seats_newly_required
                        _seats.extend([None] * num_seats_newly_required)
                else:
                    assert orig_element.seats is None or len(orig_element.seats) == 0
        for stock_id, num_seats_required in num_seats_required_for_stock.items():
            _seats = seats_required_for_stock.get(stock_id)
            if _seats is None:
                seats_required_for_stock[stock_id] = _seats = []
            _seats.extend(
                reserving.reserve_seats(
                    stock_id=stock_id,
                    quantity=num_seats_required,
                    reserve_status=SeatStatusEnum.Ordered.v,
                    separate_seats=entrust_separate_seats
                    )
                )
        for product_item, _seats in seats_required_for_element.items():
            for i in range(0, len(_seats)):
                seat = _seats[i]
                if seat is None:
                    _seats[i] = seats_required_for_stock[product_item.stock.id].pop(0)
        return seats_required_for_element

    def build_element(seats_required_for_element, orig_element):
        assert orig_element.quantity == len(orig_element.tokens), u'orig_element.id=%ld / orig_element.quantity (%d) != len(orig_element.tokens) (%d)' % (orig_element.id, orig_element.quantity, len(orig_element.tokens))
        seats = []
        tokens = []
        quantity_only = orig_element.product_item.stock.stock_type.quantity_only
        if not quantity_only:
            assert orig_element.seats is not None
            seats = seats_required_for_element.pop(orig_element.product_item)
        else:
            assert orig_element.seats is None or len(orig_element.seats) == 0

        retval = OrderedProductItem(
            product_item=orig_element.product_item,
            price=orig_element.price,
            quantity=len(orig_element.tokens),
            seats=seats
            )
        retval.tokens=[
            OrderedProductItemToken(
                serial=serial,
                seat=seat,
                valid=True
                )
            for serial, seat in core_api.iterate_serial_and_seat(retval)
            ]
        return retval

    def build_item(seats_required_for_element, item):
        return OrderedProduct(
            product=item.product,
            price=item.price,
            quantity=item.quantity,
            elements=[
                build_element(seats_required_for_element, element)
                for element in item.elements
                ]
            )

    seats_required_for_element = take_stock_and_find_out_required_seats(proto_order)

    order = Order(
        order_no=proto_order.order_no,
        channel=default_channel,
        total_amount=proto_order.total_amount,
        shipping_address=proto_order.shipping_address,
        payment_delivery_pair=proto_order.payment_delivery_pair,
        system_fee=proto_order.system_fee,
        special_fee_name=proto_order.special_fee_name,
        special_fee=proto_order.special_fee,
        transaction_fee=proto_order.transaction_fee,
        delivery_fee=proto_order.delivery_fee,
        performance=proto_order.performance,
        sales_segment=proto_order.sales_segment,
        organization_id=proto_order.organization_id,
        operator=proto_order.operator,
        user=proto_order.user,
        membership=proto_order.membership,
        membergroup=proto_order.membergroup,
        issuing_start_at=proto_order.issuing_start_at,
        issuing_end_at=proto_order.issuing_end_at,
        payment_start_at=proto_order.payment_start_at,
        payment_due_at=proto_order.payment_due_at,
        note=proto_order.note,
        attributes=proto_order.attributes or {},
        items=[build_item(seats_required_for_element, item) for item in proto_order.items],
        created_at=proto_order.new_order_created_at or (prev_order and prev_order.created_at),
        paid_at=proto_order.new_order_paid_at or (prev_order and prev_order.paid_at),
        cart_setting_id=proto_order.cart_setting_id,
        user_point_accounts=proto_order.user_point_accounts
        )
    attributes = proto_order.attributes
    if prev_order is not None:
        order.branch_no = (prev_order.branch_no or 0) + 1
        for k in ['channel', 'delivered_at', 'fraud_suspect', 'issued', 'issued_at', 'printed_at', 'refund_id', 'refunded_at', 'manual_point_grant', 'refund_total_amount', 'refund_system_fee', 'refund_transaction_fee', 'refund_delivery_fee', 'refund_special_fee']:
            setattr(order, k, getattr(prev_order, k))
        if attributes is None:
            attributes = prev_order.attributes
    if attributes is not None:
        order.attributes = attributes
    return order

def label_for_object(v):
    from altair.app.ticketing.cart.models import Cart
    from altair.app.ticketing.lots.models import LotEntry
    if isinstance(v, Cart):
        return u'カート'
    elif isinstance(v, LotEntry):
        return u'抽選'
    elif isinstance(v, Order):
        return u'注文'
    return u'(未使用)'

def get_relevant_object(request, order_no, session=None, include_deleted=False):
    if session is None:
        from altair.app.ticketing.models import DBSession
        session = session
    from altair.app.ticketing.cart.models import Cart
    from altair.app.ticketing.lots.models import LotEntry
    # 必ず最初に Order を探すこと
    order = get_order_by_order_no(request, order_no, session=session, include_deleted=include_deleted)
    if order is not None:
        return order
    lot_entry = session.query(LotEntry, include_deleted=include_deleted).filter_by(entry_no=order_no).first()
    if lot_entry is not None:
        return lot_entry
    cart = session.query(Cart, include_deleted=include_deleted).filter_by(order_no=order_no).first()
    if cart is not None:
        return cart
    return None

def create_or_update_orders_from_proto_orders(request, reserving, stocker, proto_orders, import_type, allocation_mode, entrust_separate_seats, order_modifier=None, now=None, channel_for_new_orders=ChannelEnum.INNER.v):
    from altair.app.ticketing.models import DBSession
    errors_map = {}

    # まず最初に order をリリースする
    orders_will_be_created = bool(int(import_type) & int(ImportTypeEnum.Create))
    orders_will_be_updated = bool(int(import_type) & int(ImportTypeEnum.Update))
    always_issue_order_no = bool(int(import_type) & int(ImportTypeEnum.AlwaysIssueOrderNo))

    if orders_will_be_updated:
        for proto_order in proto_orders:
            if proto_order.original_order:
                logger.info('releasing order (%s)' % proto_order.original_order.order_no)
                try:
                    assert proto_order.order_no == proto_order.original_order.order_no
                    proto_order.original_order.release()
                    if now is not None:
                        now_ = now
                    else:
                        now_ = datetime.now()
                    proto_order.original_order.mark_canceled(now_)
                    proto_order.original_order.deleted_at = now_
                except Exception as e:
                    logger.exception(u'error occurred during releasing the orders')
                    errors_map.setdefault(proto_order.ref, []).append(
                        OrderCreationError(
                            proto_order.ref,
                            proto_order.order_no,
                            u'座席の解放に失敗しました',
                            {}
                            )
                        )
                    raise MassOrderCreationError(u'error occurred during releasing the orders', errors_map)
                logger.info('finished releasing order (%s)' % proto_order.original_order.order_no)
                DBSession.flush()
    else:
        assert orders_will_be_created and not any(proto_order.original_order for proto_order in proto_orders)

    created_orders = []
    updated_orders = []
    for proto_order in proto_orders:
        errors_for_proto_order = []
        if proto_order.original_order is not None:
            logger.info('updating order (%s)' % proto_order.order_no)
        else:
            logger.info('creating order (%s)' % proto_order.order_no)
        try:
            new_order = create_order_from_proto_order(
                request,
                reserving=reserving,
                stocker=stocker,
                proto_order=proto_order,
                prev_order=proto_order.original_order,
                entrust_separate_seats=entrust_separate_seats,
                default_channel=channel_for_new_orders
                )
            errors_for_proto_order.extend(validate_order(request, new_order, proto_order.ref, update=(proto_order.original_order is not None)))
        except NotEnoughStockException as e:
            import sys
            logger.info('cannot reserve stock (stock_id=%s, required=%d, available=%d)' % (e.stock.id, e.required, e.actualy), exc_info=sys.exc_info())
            errors_for_proto_order.append(
                OrderCreationError(
                    proto_order.ref,
                    proto_order.order_no,
                    u'在庫がありません (席種: ${stock_type_name}, 個数: ${required})',
                    dict(
                        stock_type_name=e.stock.stock_type.name,
                        required=e.required
                        )
                    )
                )
        except NotEnoughAdjacencyException as e:
            import sys
            logger.info('cannot allocate seat (stock_id=%s, quantity=%d)' % (e.stock_id, e.quantity), exc_info=sys.exc_info())
            stock = DBSession.query(Stock).filter_by(id=e.stock_id).one()
            errors_for_proto_order.append(
                OrderCreationError(
                    proto_order.ref,
                    proto_order.order_no,
                    u'配席可能な座席がありません (席種: ${stock_type_name}, 個数: ${quantity})',
                    dict(
                        stock_type_name=stock.stock_type.name,
                        quantity=e.quantity
                        )
                    )
                )
        except InvalidProductSelectionException as e:
            import sys
            logger.info('cannot take stocks', exc_info=sys.exc_info())
            errors_for_proto_order.append(
                OrderCreationError(
                    proto_order.ref,
                    proto_order.order_no,
                    u'バグが発生しています (商品/商品明細に紐づいている公演とorderのperformanceが違うとかそのような理由だけどバリデーションできていない)',
                    {}
                    )
                )
        except InvalidSeatSelectionException as e:
            import sys
            logger.info('cannot allocate selected seats', exc_info=sys.exc_info())
            errors_for_proto_order.append(
                OrderCreationError(
                    proto_order.ref,
                    proto_order.order_no,
                    u'既に予約済か選択できない座席です。',
                    {}
                    )
                )
        if len(errors_for_proto_order) > 0:
            errors_map[proto_order.ref] = errors_for_proto_order
            continue
        if order_modifier is not None:
            order_modifier(proto_order, new_order)
        if now is not None:
            now_ = now
        else:
            now_ = datetime.now()
        proto_order.processed_at = now_
        DBSession.add(proto_order)
        DBSession.add(new_order)
        DBSession.flush()
        if proto_order.original_order is not None:
            logger.info('finished creating an updated order (%s)' % proto_order.order_no)
            proto_order.original_order.deleted_at = now_
            updated_orders.append((proto_order, new_order))
        else:
            logger.info('finished creating a new order (%s)' % proto_order.order_no)
            created_orders.append((proto_order, new_order))

    if len(errors_map) > 0:
        raise MassOrderCreationError(u'failed to create or update orders', errors_map)

    for proto_order, order in updated_orders:
        logger.info('reflecting the status of updated order to the payment / delivery plugins (%s)' % order.order_no)
        try:
            DBSession.merge(order)
            refresh_order(request, DBSession, order)
        except Exception as e:
            import sys
            exc_info = sys.exc_info()
            logger.error(u'[EMERGENCY] failed to update order %s' % order.order_no, exc_info=exc_info)
            errors_map.setdefault(proto_order.ref, []).append(
                OrderCreationError(
                    proto_order.ref,
                    order.order_no,
                    u'注文情報の送信中に致命的なエラーが発生しました (${error})',
                    dict(error=unicode(e)),
                    nested_exc_info=exc_info
                    )
                )
            break # 本当に致命的なので途中で処理を中断する
    if len(errors_map) > 0:
        raise MassOrderCreationError(u'failed to update orders', errors_map)

    for proto_order, order in created_orders:
        logger.info('reflecting the status of new order to the payment / delivery plugins (%s)' % order.order_no)
        try:
            DBSession.merge(order)
            call_payment_delivery_plugin(
                request,
                order,
                included_payment_plugin_ids=[
                    payments_plugins.SEJ_PAYMENT_PLUGIN_ID,
                    payments_plugins.RESERVE_NUMBER_PAYMENT_PLUGIN_ID,
                    payments_plugins.FREE_PAYMENT_PLUGIN_ID,
                    payments_plugins.FAMIPORT_PAYMENT_PLUGIN_ID
                    ]
                )
        except Exception as e:
            import sys
            exc_info = sys.exc_info()
            logger.error(u'failed to create inner order %s' % order.order_no, exc_info=exc_info)
            errors_map.setdefault(proto_order.ref, []).append(
                OrderCreationError(
                    proto_order.ref,
                    order.order_no,
                    u'注文情報の送信中に致命的なエラーが発生しました (${error})',
                    dict(error=unicode(e)),
                    nested_exc_info=exc_info
                    )
                )
            order.release()
            # 処理は中断せず、次の予約に進む
    if len(errors_map) > 0:
        raise MassOrderCreationError(u'failed to create orders', errors_map)

def save_order_modifications_from_proto_orders(request, order_proto_order_pairs, session=None, now=None):
    if session is None:
        from altair.app.ticketing.models import DBSession
        session = DBSession
    if now is None:
        now = datetime.now()
    reserving = cart_api.get_reserving(request)
    stocker = cart_api.get_stocker(request)

    # まず最初に order をリリースする
    for prev_order, _ in order_proto_order_pairs:
        prev_order.release()

    # proto_order から枝版を生成する
    retval = []
    errors_map = {}
    for prev_order, proto_order in order_proto_order_pairs:
        errors = []
        try:
            # 次に ProtoOrder から Order を生成して
            new_order = create_order_from_proto_order(request, reserving, stocker, proto_order, prev_order)
            # 在庫の状態など正しいか判定する
            errors.extend(validate_order(request, new_order, proto_order.ref, update=(proto_order.original_order is not None)))
        except NotEnoughStockException as e:
            import sys
            logger.info('cannot reserve stock (stock_id=%s, required=%d, available=%d)' % (e.stock.id, e.required, e.actualy), exc_info=sys.exc_info())
            errors.append(
                OrderCreationError(
                    proto_order.ref,
                    proto_order.order_no,
                    u'在庫がありません (席種: ${stock_type_name}, 個数: ${required})',
                    dict(
                        stock_type_name=e.stock.stock_type.name,
                        required=e.required
                        )
                    )
                )
        except NotEnoughAdjacencyException as e:
            import sys
            logger.info('cannot allocate seat (stock_id=%s, quantity=%d)' % (e.stock_id, e.quantity), exc_info=sys.exc_info())
            stock = DBSession.query(Stock).filter_by(id=e.stock_id).one()
            errors.append(
                OrderCreationError(
                    proto_order.ref,
                    proto_order.order_no,
                    u'配席可能な座席がありません (席種: ${stock_type_name}, 個数: ${quantity})',
                    dict(
                        stock_type_name=stock.stock_type.name,
                        quantity=e.quantity
                        )
                    )
                )
        except InvalidProductSelectionException as e:
            import sys
            logger.info('cannot take stocks', exc_info=sys.exc_info())
            errors.append(
                OrderCreationError(
                    proto_order.ref,
                    proto_order.order_no,
                    u'バグが発生しています (商品/商品明細に紐づいている公演とorderのperformanceが違うとかそのような理由だけどバリデーションできていない)',
                    {}
                    )
                )
        except InvalidSeatSelectionException as e:
            import sys
            logger.info('cannot allocate selected seats', exc_info=sys.exc_info())
            errors.append(
                OrderCreationError(
                    proto_order.ref,
                    proto_order.order_no,
                    u'既に予約済か選択できない座席です。',
                    {}
                    )
                )
        if len(errors) > 0:
            errors_map[proto_order.order_no] = errors
            continue
        prev_order.deleted_at = now
        proto_order.processed_at = now
        session.add(proto_order)
        session.add(new_order)
        session.flush()
        retval.append((prev_order, proto_order, new_order))
    if errors_map:
        raise MassOrderCreationError(u'failed to modify orders', errors_map)

    # 決済・引取モジュールの状態に反映
    for _, _, new_order in retval:
        refresh_order(request, DBSession, new_order)

    return retval

def create_proto_order_from_modify_data(request, original_order, modify_data, operator):
    errors = []
    warnings = []

    # --- modify_data の構造 ---
    # {
    #     'performance_id': 1,
    #     'sales_segment_id': 1,
    #     'transaction_fee': 0,
    #     'delivery_fee': 0,
    #     'system_fee': 0,
    #     'special_fee': 0,
    #     'issuing_start_at': '...',
    #     'issuing_end_at': '...',
    #     'payment_start_at': '...',
    #     'payment_due_at': '...',
    #     'items': [
    #         {
    #             'id': 1,
    #             'product_id': 1,
    #             'quantity': 1,
    #             'price': 0,
    #             'elements': [
    #                 {
    #                     'id': 1,
    #                     'product_item': {
    #                         'id': 1,
    #                         'name': '',
    #                         'price': 0,
    #                         'quantity': 1,
    #                         'stock_holder_name': '',
    #                         'stock_type_id': 0,
    #                         'is_seat': False,
    #                         'quantity_only': False,
    #                         },
    #                     'product_item_id': 0, # これは new でサポート
    #                     'quantity': 1,
    #                     'price': 0, # これは new でサポート
    #                     'seats': [
    #                         {
    #                             'id': 1, # 実は l0_id
    #                             'l0_id': 1, # 実は l0_id、これは new でサポート
    #                             }
    #                         ]
    #                     }
    #                 ]
    #             }
    #         ]
    #     }

    transaction_fee_v = modify_data.get('transaction_fee')
    delivery_fee_v = modify_data.get('delivery_fee')
    system_fee_v = modify_data.get('system_fee')
    special_fee_v = modify_data.get('special_fee')
    performance_id_v = modify_data.get('performance_id')
    sales_segment_id_v = modify_data.get('sales_segment_id')
    issuing_start_at_v = modify_data.get('issuing_start_at')
    issuing_end_at_v = modify_data.get('issuing_end_at')
    payment_start_at_v = modify_data.get('payment_start_at')
    payment_due_at_v = modify_data.get('payment_due_at')

    transaction_fee = Decimal(transaction_fee_v) if transaction_fee_v is not None else None
    delivery_fee = Decimal(delivery_fee_v) if delivery_fee_v is not None else None
    system_fee = Decimal(system_fee_v) if system_fee_v is not None else None
    _special_fee = Decimal(special_fee_v) if special_fee_v is not None else None
    if _special_fee is not None:
        special_fee = Decimal(_special_fee)
    else:
        special_fee = None

    performance_id = long(performance_id_v) if performance_id_v is not None else original_order.performance_id
    sales_segment_id = long(sales_segment_id_v) if sales_segment_id_v is not None else original_order.sales_segment_id
    if operator is None:
        operator = original_order.operator

    issuing_start_at = original_order.issuing_start_at
    if issuing_start_at_v is not None:
        if isinstance(issuing_start_at_v, date):
            issuing_start_at = issuing_start_at_v
        else:
            issuing_start_at = parsedate(issuing_start_at_v)

    issuing_end_at = original_order.issuing_end_at
    if issuing_end_at_v is not None:
        if isinstance(issuing_end_at_v, date):
            issuing_end_at = issuing_end_at_v
        else:
            issuing_end_at = parsedate(issuing_end_at_v)

    payment_start_at = original_order.payment_start_at
    if payment_start_at_v is not None:
        if isinstance(payment_start_at_v, date):
            payment_start_at = payment_start_at_v
        else:
            payment_start_at = parsedate(payment_start_at_v)

    payment_due_at = original_order.payment_due_at
    if payment_due_at_v is not None:
        if isinstance(payment_due_at_v, date):
            payment_due_at = payment_due_at_v
        else:
            payment_due_at = parsedate(payment_due_at_v)

    issuing_start_at = todatetime(issuing_start_at) if issuing_start_at else None
    issuing_end_at = todatetime(issuing_end_at) if issuing_end_at else None
    payment_start_at = todatetime(payment_start_at) if payment_start_at else None
    payment_due_at = todatetime(payment_due_at) if payment_due_at else None
    attributes = modify_data.get('attributes')
    if attributes is None:
        attributes = dict(original_order.attributes)
    proto_order = ProtoOrder(
        order_no=original_order.order_no,
        organization=original_order.ordered_from,
        shipping_address=original_order.shipping_address,
        performance_id=performance_id,
        sales_segment_id=sales_segment_id,
        user=original_order.user,
        payment_delivery_pair=original_order.payment_delivery_pair,
        special_fee_name=original_order.special_fee_name,
        operator=operator,
        issuing_start_at=issuing_start_at,
        issuing_end_at=issuing_end_at,
        payment_start_at=payment_start_at,
        payment_due_at=payment_due_at,
        original_order=original_order,
        new_order_created_at=original_order.created_at,
        cart_setting_id=original_order.cart_setting_id,
        note=original_order.note,
        attributes=attributes,
        user_point_accounts=original_order.user_point_accounts,
        membership=original_order.membership,
        membergroup=original_order.membergroup
        )
    # item => OrderedProduct, element => OrderedProductItem になる
    # この分かりにくい対応は歴史的経緯によるものです...
    md_items = modify_data.get('items')
    if md_items is None:
        # XXX: backwards compatibility
        md_items = modify_data.get('ordered_products')
        if md_items is None:
            raise Exception("neither 'items' nor 'ordered_products' exists in modified_data")

    # calculated_total_amount の初期値
    calculated_total_amount = Decimal(0)
    calculated_transaction_fee = Decimal(0)
    calculated_delivery_fee = Decimal(0)
    calculated_system_fee = Decimal(0)
    calculated_special_fee = Decimal(0)

    payment_delivery_pair = proto_order.payment_delivery_pair
    for md_item in md_items:
        item_price = md_item.get('price') # ないかも
        item_quantity = int(md_item['quantity'])
        if item_quantity == 0:
            # 0 なら商品削除っぽい
            continue
        old_item_id = md_item['id']
        product_id = md_item['product_id']
        product = Product.query.filter_by(id=product_id).one()
        if item_price is None:
            logger.debug('item_price is None; assuming it to be the same as product.price')
            item_price = product.price
        else:
            if not item_price: # 0だったら
                warnings.append(_(u'商品「${product_name}」の価格が0に設定されています') % dict(product_name=product.name))
        new_item = OrderedProduct(
            product=product,
            price=Decimal(item_price),
            quantity=item_quantity
            )
        # elements を処理
        md_elements = md_item.get('elements')
        if md_elements is None:
            md_elements = md_item.get('ordered_product_items')
            if md_elements is None:
                raise Exception("neither 'elements' nor 'ordered_product_items' exists in modified_data['items'][...]")
        element_total = 0
        for md_element in md_elements:
            old_element_id = md_element['id']
            element_quantity = int(md_element['quantity']) if md_element.get('quantity') else 0 # 0 だと明細削除
            product_item_dict = md_element.get('product_item') # 互換性のため
            element_price = None
            if product_item_dict is None:
                # 新しい構造
                product_item_id = md_element.get('product_item_id')
                product_item = ProductItem.query.filter_by(id=product_item_id).one()
                element_price = md_element.get('price') # ないかも
            else:
                # 古い構造
                product_item = ProductItem.query.filter_by(id=product_item_dict['id']).one()
                element_price = Decimal(product_item_dict['price'])
            if element_price is None:
                logger.debug('element_price is None; assuming it to be the same as product_item.price')
                element_price = product_item.price
            else:
                if not element_price: # 0 だったら
                    warnings.append(_(u'商品「${product_name}」の商品明細「${product_item_name}」の価格が0に設定されています') % dict(product_name=product.name, product_item_name=product_item.name))
            if element_quantity % item_quantity != 0:
                raise OrderCreationError(
                    proto_order.ref,
                    proto_order.order_no,
                    'element_quantity is not a multiple of item_quantity'
                    )
            md_seats = md_element.get('seats') # 数受けの場合は存在しない
            if md_seats:
                new_seats = Seat.query \
                    .join(Seat.venue) \
                    .filter(
                        Venue.performance_id == performance_id,
                        Seat.l0_id.in_((md_seat.get('l0_id') or md_seat.get('id')) for md_seat in md_seats)
                    ).all()
                if len(new_seats) < element_quantity:
                    raise OrderCreationError(
                        proto_order.ref,
                        proto_order.order_no,
                        u'商品「${product_name}」の商品明細「${product_item_name}」に割り当てられている座席数が在庫引当数より少なくなっています',
                        dict(product_name=product.name, product_item_name=product_item.name)
                        )
            else:
                new_seats = []
            new_tokens = [
                OrderedProductItemToken(
                    serial=i,
                    seat=(new_seats[i] if i < len(new_seats) else None),
                    valid=True
                    )
                for i in range(0, element_quantity)
                ]
            new_element = OrderedProductItem(
                product_item=product_item,
                price=Decimal(element_price),
                quantity=element_quantity,
                seats=new_seats,
                tokens=new_tokens
                )
            new_item.elements.append(new_element)
            element_total += element_price * element_quantity
        item_total = new_item.price * new_item.quantity
        if element_total != item_total:
            warnings.append(_(u'商品「${product_name}」の商品明細の価格の合計が商品の価格と一致しません (${element_total} ≠ ${item_total})') % dict(product_name=product.name, product_item_name=product_item.name, element_total=element_total, item_total=item_total))

        calculated_total_amount += item_total
        num_principal_tickets = new_item.product.num_principal_tickets(payment_delivery_pair)
        calculated_transaction_fee += \
            (
                payment_delivery_pair.transaction_fee_per_product + \
                payment_delivery_pair.transaction_fee_per_ticket * num_principal_tickets
                ) * new_item.quantity
        calculated_delivery_fee += \
            (
                payment_delivery_pair.delivery_fee_per_product + \
                payment_delivery_pair.delivery_fee_per_ticket * num_principal_tickets
                ) * new_item.quantity
        calculated_system_fee += \
            (
                payment_delivery_pair.system_fee_per_product + \
                payment_delivery_pair.system_fee_per_ticket * num_principal_tickets
                ) * new_item.quantity
        calculated_special_fee += \
            (
                payment_delivery_pair.special_fee_per_product + \
                payment_delivery_pair.special_fee_per_ticket * num_principal_tickets
                ) * new_item.quantity
        proto_order.items.append(new_item)

    calculated_transaction_fee += payment_delivery_pair.transaction_fee_per_order
    calculated_delivery_fee += payment_delivery_pair.delivery_fee_per_order
    calculated_system_fee += payment_delivery_pair.system_fee_per_order
    calculated_special_fee += payment_delivery_pair.special_fee_per_order

    if delivery_fee is None:
        delivery_fee = calculated_delivery_fee
    if transaction_fee is None:
        transaction_fee = calculated_transaction_fee
    if system_fee is None:
        system_fee = calculated_system_fee
    if special_fee is None:
        special_fee = calculated_special_fee
    calculated_total_amount += delivery_fee + transaction_fee + system_fee + special_fee

    proto_order.total_amount = calculated_total_amount
    proto_order.delivery_fee = delivery_fee
    proto_order.transaction_fee = transaction_fee
    proto_order.system_fee = system_fee
    proto_order.special_fee = special_fee

    return proto_order, warnings

def save_order_modification_new(request, order, modify_data, session=None):
    assert order.canceled_at is None
    assert order.deleted_at is None
    if session is None:
        from altair.app.ticketing.models import DBSession
        session = DBSession
    operator = None
    if hasattr(request, 'context') and hasattr(request.context, 'user'):
        operator = request.context.user
    proto_order, warnings = create_proto_order_from_modify_data(request, order, modify_data, operator)
    session.add(proto_order)
    for warning in warnings:
        logger.info(u'WARNING - %s' % (warning.interpolate() if hasattr(warning, 'interpolate') else warning))
    try:
        new_orders = save_order_modifications_from_proto_orders(request, [(order, proto_order)])
    except MassOrderCreationError as e:
        raise e.errors[proto_order.order_no][0]
    finally:
        session.flush()
    return new_orders[0][2], warnings

def save_order_modification_old(request, order, modify_data, session=None):
    if session is None:
        from altair.app.ticketing.models import DBSession
        session = DBSession

    reserving = cart_api.get_reserving(request)
    stocker = cart_api.get_stocker(request)

    order = Order.query.filter_by(id=order.id).with_lockmode('update').one()
    modify_order = Order.clone(order, deep=True)
    modify_order.performance_id = modify_data.get('performance_id')
    modify_order.sales_segment_id = modify_data.get('sales_segment_id')
    modify_order.transaction_fee = modify_data.get('transaction_fee')
    modify_order.delivery_fee = modify_data.get('delivery_fee')
    modify_order.system_fee = modify_data.get('system_fee')
    modify_order.specialfee = modify_data.get('special_fee')
    modify_order.total_amount = modify_data.get('total_amount')
    modify_order.operator = request.context.user if hasattr(request.context, 'user') else order.operator

    try:
        op_zip = itertools.izip(order.items, modify_order.items)
        for i, (op, mop) in enumerate(op_zip):
            op_data = None
            ordered_products = modify_data.get('ordered_products')
            if ordered_products is None:
                ordered_products = modify_data['items']
            for data in ordered_products:
                if data.get('id') == op.id and data.get('product_id') == op.product_id:
                    op_data = data
                    break
            logger.debug('op_data %s' % op_data)

            # 商品削除
            if op_data is None or op_data.get('quantity') == 0:
                logger.info('delete ordered_product %s' % mop.id)
                mop.release()
                mop.delete()
                modify_order.items.pop(i)
                continue

            # 商品数および座席変更
            mop.price = long(op_data.get('price'))
            mop.quantity = long(op_data.get('quantity'))

            opi_zip = itertools.izip(op.elements, mop.elements)
            for j, (opi, mopi) in enumerate(opi_zip):
                opi_data = None
                ordered_product_items = op_data.get('ordered_product_items')
                if ordered_product_items is None:
                    ordered_product_items = op_data['elements']
                for data in ordered_product_items:
                    if data.get('id') == opi.id:
                        opi_data = data
                        break
                logger.info('opi_data %s' % opi_data)

                # 商品明細削除
                opi_quantity = long(opi_data.get('quantity'))
                if opi_data is None or opi_quantity == 0:
                    logger.info('delete ordered_product_item %s' % mopi.id)
                    mopi.release()
                    mopi.delete()
                    mop.elements.pop(j)
                    continue

                # 座席変更
                mopi.release()
                mopi.seats = []

                product_item_data = opi_data.get('product_item')
                if product_item_data is not None:
                    price = product_item_data.get('price')
                else:
                    price = opi_data['price']
                mopi.price = Decimal(price)
                mopi.quantity = opi_quantity

                product_requires = [(mop.product, mop.quantity)]
                stock_statuses = stocker.take_stock(modify_order.performance_id, product_requires)
                if not mopi.product_item.stock.stock_type.quantity_only:
                    seats_data = opi_data.get('seats')
                    seats = reserving.reserve_selected_seats(
                        stock_statuses,
                        modify_order.performance_id,
                        [(s.get('l0_id') or s.get('id')) for s in seats_data],
                        SeatStatusEnum.Ordered
                    )
                    mopi.seats += seats
                    logger.info('seats_data %s' % seats_data)

                for token in mopi.tokens:
                    DBSession.delete(token)
                    DBSession.flush()
                mopi.tokens = []

                for i, seat in core_api.iterate_serial_and_seat(mopi):
                    token = OrderedProductItemToken(
                        serial = i,
                        seat = seat,
                        valid=True
                        )
                    mopi.tokens.append(token)

        # 商品追加
        ordered_products = modify_data.get('ordered_products')
        if ordered_products is None:
            ordered_products = modify_data['items']
        for op_data in ordered_products:
            add_product = False
            if not op_data.get('id'):
                if op_data.get('quantity') > 0:
                    add_product = True
            else:
                for op in order.items:
                    if op_data.get('id') == op.id and op_data.get('product_id') != op.product_id:
                        add_product = True
                        break

            if add_product:
                logger.info('add ordered_product %s' % op_data)
                product = Product.get(long(op_data.get('product_id')))
                op_quantity = long(op_data.get('quantity'))
                ordered_product = OrderedProduct(
                    order=modify_order, product=product, price=product.price, quantity=op_quantity)
                for product_item in product.items:
                    seats = []
                    product_requires = [(product, op_quantity)]
                    stock_statuses = stocker.take_stock(modify_order.performance_id, product_requires)
                    if not product_item.stock.stock_type.quantity_only:
                        seats_data = []
                        ordered_product_items = op_data.get('ordered_product_items')
                        if ordered_product_items is None:
                            ordered_product_items = op_data['elements']
                        for opi_data in ordered_product_items:
                            if opi_data.get('seats'):
                                seats_data = opi_data.get('seats')
                                logger.info('seats_data %s' % seats_data)
                                break
                        seats = reserving.reserve_selected_seats(
                            stock_statuses,
                            modify_order.performance_id,
                            [(s.get('l0_id') or s.get('id')) for s in seats_data],
                            SeatStatusEnum.Ordered
                        )
                    ordered_product_item = OrderedProductItem(
                        ordered_product=ordered_product,
                        product_item=product_item,
                        price=product_item.price,
                        quantity=product_item.quantity * op_quantity,
                        seats=seats
                    )
                    for i, seat in core_api.iterate_serial_and_seat(ordered_product_item):
                        token = OrderedProductItemToken(
                            serial = i,
                            seat = seat,
                            valid=True
                            )
                        ordered_product_item.tokens.append(token)
    except InvalidSeatSelectionException:
        import sys
        raise OrderCreationError(
            None,
            modify_order.order_no,
            u'既に予約済か選択できない座席です。画面を最新の情報に更新した上で再度座席を選択してください。',
            nested_exc_info=sys.exc_info()
            )
    except NotEnoughStockException as e:
        import sys
        logger.info("not enough stock quantity :%s" % e)
        raise OrderCreationError(
            None,
            modify_order.order_no,
            u'${required_quantity} 席 (個) 引き当てようとしましたが ${available_quantity} 席 (個) しか在庫がありません (席種: ${stock_type_name}, 枠: ${stock_holder_name})',
            dict(
                required_quantity=e.required,
                available_quantity=e.actualy,
                stock_type_name=e.stock_type_name,
                stock_holder_name=e.stock_holder_name
                ),
            nested_exc_info=sys.exc_info()
            )

    total_amount = sum(mop.price * mop.quantity for mop in modify_order.items)
    total_amount += modify_order.transaction_fee + modify_order.delivery_fee + modify_order.system_fee + modify_order.special_fee
    logger.info('total amount = %s' % total_amount)
    if total_amount != modify_order.total_amount:
        logger.info('total amount of the modified order does not match to the expected amount (%s expected, %s actual)' % (total_amount, modify_order.total_amount))
        raise OrderCreationError(
            None,
            modify_order.order_no,
            u'合計金額を確認してください。計算では${calculated_total_amount}ですが${total_amount}が指定されています',
            dict(
                calculated_total_amount=total_amount,
                total_amount=modify_order.total_amount
                )
            )

    session.add(modify_order)

    # 金額変更をAPIで更新
    payment_plugin_id = order.payment_delivery_pair.payment_method.payment_plugin_id
    delivery_plugin_id = order.payment_delivery_pair.delivery_method.delivery_plugin_id
    if order.total_amount > modify_order.total_amount or \
       payment_plugin_id == payments_plugins.SEJ_PAYMENT_PLUGIN_ID or \
       delivery_plugin_id == payments_plugins.SEJ_DELIVERY_PLUGIN_ID:
        refresh_order(request, DBSession, modify_order)

    return modify_order, []

save_order_modification = save_order_modification_new

def get_refund_per_order_fee(refund, order):
    pdmp = order.payment_delivery_pair
    fee = 0
    if refund.include_system_fee:
        fee += order.refund_system_fee
    if refund.include_special_fee:
        fee += order.refund_special_fee
    if refund.include_transaction_fee:
        fee += pdmp.transaction_fee_per_order
    if refund.include_delivery_fee:
        fee += pdmp.delivery_fee_per_order
    if refund.include_item:
        # チケットに紐づかない商品明細分の合計金額
        for op in order.items:
            for opi in op.elements:
                if not opi.product_item.ticket_bundle_id:
                    fee += opi.refund_price * opi.quantity
    return fee

def get_refund_per_ticket_fee(refund, order):
    pdmp = order.payment_delivery_pair
    fee = 0
    if refund.include_transaction_fee:
        fee += pdmp.transaction_fee_per_ticket
    if refund.include_delivery_fee:
        fee += pdmp.delivery_fee_per_ticket
    return fee

def get_refund_ticket_price(refund, order, product_item_id):
    if not refund.include_item:
        return 0
    for op in order.items:
        for opi in op.elements:
            if opi.product_item_id == product_item_id:
                return opi.refund_price
    return 0

def get_anshin_checkout_object(request, order):
    if order.payment_delivery_pair.payment_method.payment_plugin_id == payments_plugins.CHECKOUT_PAYMENT_PLUGIN_ID:
        service = checkout_api.get_checkout_service(request, order.ordered_from, core_api.get_channel(order.channel))
        return service.get_checkout_object_by_order_no(order.order_no)
    else:
        return None

def get_multicheckout_info(request, order):
    multicheckout_info = None
    if order.payment_delivery_pair.payment_method.payment_plugin_id == payments_plugins.MULTICHECKOUT_PAYMENT_PLUGIN_ID:
        organization = order.organization
        multicheckout_api = get_multicheckout_3d_api(request, organization.setting.multicheckout_shop_name)
        recs, _ = multicheckout_api.get_transaction_info(order.order_no)
        for rec in recs:
            if rec['status'] == str(MultiCheckoutStatusEnum.Authorized): # authorization successful
                multicheckout_info = rec
                break
    if multicheckout_info is not None:
        multicheckout_info['ahead_com_name'] = get_multicheckout_ahead_com_name(multicheckout_info['ahead_com_cd'])
    return multicheckout_info


def get_extra_form_fields_for_order(request, order_like, for_=None, mode=None):
    if order_like.sales_segment is None:
        return []
    from altair.app.ticketing.cart.view_support import get_extra_form_schema, filter_extra_form_schema, DummyCartContext
    if for_ is None:
        if hasattr(order_like, 'created_from_lot_entry') and \
           order_like.created_from_lot_entry:
            for_ = 'lots'
        else:
            for_ = 'cart'
    extra_form_fields = get_extra_form_schema(
        DummyCartContext(request, order_like),
        request,
        order_like.sales_segment,
        for_,
        )
    extra_form_fields = filter_extra_form_schema(extra_form_fields, mode) 
    if not extra_form_fields:
        return []
    return extra_form_fields

def get_order_attribute_pair_pairs(request, order_like, include_undefined_items=False, for_=None, mode=None):
    from altair.app.ticketing.cart.view_support import render_display_value
    retval = []
    values = OrderAttributeIO(include_undefined_items=include_undefined_items, for_=for_, mode=mode).marshal(request, order_like)
    for field_name, display_name, field_value, _, field_desc in values:
        if field_desc is not None:
            display_value = render_display_value(request, field_desc, field_value)
        else:
            display_value = field_value
        retval.append(
            (
                (
                    field_name,
                    field_value
                    ),
                (
                    display_name,
                    display_value
                    )
                )
            )
    return retval

class OrderAttributeIO(object):
    def __init__(self, blank_value=u"", include_undefined_items=False, for_=None, mode=None):
        self.blank_value = blank_value
        self.include_undefined_items = include_undefined_items
        self.for_ = for_
        self.mode = mode

    def blank_if_none(self, v):
        return self.blank_value if v is None else v

    def get_extra_form_fields(self, request, order_like):
        return get_extra_form_fields_for_order(request, order_like, self.for_, self.mode)

    def marshal(self, request, order_like):
        retval = []
        remaining_attributes = set(order_like.attributes.keys())
        for field_desc in self.get_extra_form_fields(request, order_like): 
            if field_desc['kind'] == 'description_only':
                continue
            field_name = field_desc['name']
            field_value = order_like.attributes.get(field_name)
            stringized_value = None
            if field_desc['kind'] in ('text', 'password', 'textarea'):
                stringized_value = self.blank_if_none(field_value)
            elif field_desc['kind'] in ('select', 'radio'):
                v = [pair for pair in field_desc['choices'] if pair['value'] == field_value]
                if len(v) > 0:
                    stringized_value = v[0]['label']
                else:
                    # 選択肢に該当する値がない => DBに入っている値をそのまま出す
                    logger.info(u"no corresponding value for %s exists in the schema of field %s" % (field_value, field_name))
                    stringized_value = self.blank_if_none(field_value)
            elif field_desc['kind'] in ('multiple_select', 'checkbox'):
                field_value = field_value.strip() if field_value is not None else u''
                if len(field_value) > 0:
                    field_value = [c.strip() for c in field_value.split(',')]
                else:
                    field_value = []
                stringized_value = []
                for c in field_value:
                    v = [pair for pair in field_desc['choices'] if pair['value'] == c]
                    if len(v) > 0:
                        v = v[0]['label']
                    else:
                        # 選択肢に該当する値がない => DBに入っている値をそのまま出す
                        logger.info(u"no corresponding value for %s exists in the schema of field %s" % (c, field_name))
                        v = c
                    stringized_value.append(v)
                stringized_value = u','.join(stringized_value)
            elif field_desc['kind'] == 'bool':
                if field_value is not None:
                    try:
                        field_value = int(field_value)
                    except (ValueError, TypeError):
                        pass
                    field_value = bool(field_value)
                    stringized_value = u'1' if field_value else u'0'
                else:
                    stringized_value = self.blank_value
            elif field_desc['kind'] == 'date':
                if field_value is not None:
                    try:
                        field_value = parsedate(field_value)
                        stringized_value = u'{0.year:04d}-{0.month:02d}-{0.day:02d}'.format(field_value)
                    except:
                        logger.info(u"%s cannot be parsed as date, field %s" % (field_value, field_name))
                        stringized_value = self.blank_value
                else:
                    stringized_value = self.blank_value
            else:
                logger.warning('unsupported kind: %s' % field_desc['kind'])
                stringized_value = self.blank_if_none(field_value)
            if field_name in remaining_attributes:
                remaining_attributes.remove(field_name)
            retval.append(
                (
                    field_name,
                    field_desc['display_name'],
                    field_value,
                    stringized_value,
                    field_desc,
                    )
                )
        if self.include_undefined_items:
            for field_name in remaining_attributes:
                field_value = order_like.attributes[field_name]
                retval.append(
                    (
                        field_name,
                        field_name,
                        field_value,
                        field_value,
                        None,
                        )
                    )
        return retval

    def unmarshal(self, request, order_like, params):
        remaining_attributes = set(params.keys())
        for field_desc in self.get_extra_form_fields(request, order_like): 
            if field_desc['kind'] == 'description_only':
                continue
            field_name = field_desc['name']
            v = params.get(field_name)
            stored_value = None
            if field_desc['kind'] in ('text', 'password', 'textarea'):
                stored_value = v
            elif field_desc['kind'] in ('select', 'radio'):
                for pair in field_desc['choices']:
                    if pair['label'] == v:
                        stored_value = pair['value']
                        break
                else:
                    # 選択肢に該当する値がない => 値をそのままDBに入れる
                    logger.info(u"no corresponding label for %s exists in the schema of field %s" % (v, field_name))
                    stored_value = v
            elif field_desc['kind'] in ('multiple_select', 'checkbox'):
                if v is not None:
                    v = [c.strip() for c in v.split(',')]
                    d = dict((pair['label'], pair['value']) for pair in field_desc['choices'])
                    _stored_value = []
                    for i in v:
                        if i in d:
                            _stored_value.append(d[i])
                        else:
                            logger.info(u"no corresponding label for %s exists in the schema of field %s" % (i, field_name))
                            _stored_value.append(i)
                    stored_value = u','.join(_stored_value)
                else:
                    stored_value = u''
            elif field_desc['kind'] == 'bool':
                if v is None:
                    stored_value = self.blank_value
                else:
                    if v == u'0':
                        stored_value = u'0'
                    else:
                        stored_value = u'1' if v != self.blank_value else None
            elif field_desc['kind'] == 'date':
                if v is not None:
                    if v == self.blank_value:
                        stored_value = None
                    else:
                        try:
                            field_value = parsedate(v)
                            stored_value = u'{0.year:04d}-{0.month:02d}-{0.day:02d}'.format(field_value)
                        except:
                            logger.info(u"%s cannot be parsed as date, field %s" % (v, field_name), exc_info=True)
                            stored_value = v
            else:
                logger.warning('unsupported kind: %s' % field_desc['kind'])
                stored_value = v
            if field_name in remaining_attributes:
                remaining_attributes.remove(field_name)
            order_like.attributes[field_name] = stored_value
        if self.include_undefined_items:
            for field_name in remaining_attributes:
                stored_value = params.get(field_name)
                order_like.attributes[field_name] = stored_value

def get_order_info_descriptor_registry(request_or_registry):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    return registry.queryUtility(IOrderDescriptorRegistry)

def get_payment_delivery_plugin_info(request, order, flavor='html'):
    payment_delivery_plugin, payment_plugin, delivery_plugin = lookup_plugin(request, order.payment_delivery_method_pair)

    if payment_delivery_plugin is not None:
        payment_plugin = payment_delivery_plugin
        delivery_plugin = None

    descr_registry = get_order_info_descriptor_registry(request)

    from collections import OrderedDict
    if payment_plugin is not None:
        _payment_plugin_info = payment_plugin.get_order_info(request, order)
        payment_plugin_info = OrderedDict()
        for k, v in _payment_plugin_info.items():
            descr = descr_registry.get_descriptor(payment_plugin, k)
            pair = None
            if descr is not None:
                renderer = descr.get_renderer(flavor)
                if renderer is not None:
                    pair = (
                        descr.get_display_name(request),
                        renderer(request, descr_registry, descr, v)
                        )
            if pair is None:
                default_renderer = request.registry.queryUtility(IOrderDescriptorRenderer, name=flavor)
                pair = (k, default_renderer(request, descr_registry, None, v) if default_renderer else u'(unrenderable)')
            payment_plugin_info[k] = pair
    else:
        payment_plugin_info = None
    if delivery_plugin is not None:
        _delivery_plugin_info = delivery_plugin.get_order_info(request, order)
        delivery_plugin_info = OrderedDict()
        for k, v in _delivery_plugin_info.items():
            descr = descr_registry.get_descriptor(delivery_plugin, k)
            pair = None
            if descr is not None:
                renderer = descr.get_renderer(flavor)
                if renderer is not None:
                    pair = (
                        descr.get_display_name(request),
                        renderer(request, descr_registry, descr, v)
                        )
            if pair is None:
                default_renderer = request.registry.queryUtility(IOrderDescriptorRenderer, name=flavor)
                pair = (k, default_renderer(request, descr_registry, None, v) if default_renderer else u'(unrenderable)')
            delivery_plugin_info[k] = pair
    else:
        delivery_plugin_info = None
    return payment_plugin_info, delivery_plugin_info

