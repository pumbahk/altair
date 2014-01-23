# encoding: utf-8

import logging
import re
import itertools

from sqlalchemy.sql.expression import and_, or_
from sqlalchemy.sql import functions as safunc
from sqlalchemy.orm import aliased
from pyramid.interfaces import IRequest
from pyramid.threadlocal import get_current_request

from altair.app.ticketing.models import DBSession, asc_or_desc
from altair.app.ticketing.utils import todatetime
from altair.app.ticketing.core.models import (
    Order,
    OrderedProduct,
    OrderedProductItem,
    OrderedProductItemToken,
    Product,
    ProductItem,
    SalesSegment,
    SalesSegmentGroup,
    PaymentMethod,
    PaymentDeliveryMethodPair,
    DeliveryMethod,
    ShippingAddress,
    Seat,
    Performance,
    ChannelEnum,
    SeatStatusEnum,
    )
from altair.app.ticketing.cart import api as cart_api
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
from altair.app.ticketing.payments.api import get_delivery_plugin
from altair.app.ticketing.payments import plugins as payments_plugins
from .models import OrderSummary


## backward compatibility
from altair.metadata.api import get_metadata_provider_registry
from .metadata import (
    METADATA_NAME_ORDERED_PRODUCT, 
    METADATA_NAME_ORDER
)
from functools import partial
get_ordered_product_metadata_provider_registry = partial(get_metadata_provider_registry,
                                                         name=METADATA_NAME_ORDERED_PRODUCT)
get_order_metadata_provider_registry = partial(get_metadata_provider_registry,
                                               name=METADATA_NAME_ORDER)

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
            query = fn(self, queue, value)
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
        query = query.join(self.targets['Cart'].products)
        query = query.join(self.targets['CartedProduct'].items)
        query = query.join(self.targets['CartedProductItem'].seats)
        query = query.filter(self.targets['Seat'].name.like('%s%%' % value))
        return query

    def _status(self, query, value):
        if value == 'completed':
            query = query.filter(self.targets['subject'].order_id != None)
        elif value == 'incomplete':
            query = query.filter(self.targets['subject'].order_id == None)
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
        query = query.join(self.targets['subject'].ordered_products)
        query = query.join(self.targets['OrderedProduct'].ordered_product_items)
        query = query.join(self.targets['OrderedProductItem'].seats)
        query = query.filter(Seat.name.like('%s%%' % value))
        return query

    @must_be_combined_with('event_id', 'performance_id')
    def _number_of_tickets(self, query, value):
        aliased_targets = dict(
            (k, aliased(v)) for k, v in self.targets.items()
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
        return query.filter(self.targets['subject'].performance_id == value)

    def _event_id(self, query, value):
        return query.filter(self.targets['subject'].event_id == value)

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
            query = query.join(self.targets['subject'].ordered_products)
            query = query.join(self.targets['OrderedProduct'].product)
            query = query.join(self.targets['Product'].sales_segment)
            query = query.filter(self.targets['SalesSegment'].sales_segment_group_id.in_(value))
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
        return query.filter(self.targets['subject'].auth_identifier==value)

    def _seat_number(self, query, value):
        query = query.join(self.targets['subject'].ordered_products)
        query = query.join(self.targets['OrderedProduct'].ordered_product_items)
        query = query.join(self.targets['OrderedProductItem'].seats)
        query = query.filter(self.targets['Seat'].name.like('%s%%' % value))
        return query

    @must_be_combined_with('event_id', 'performance_id')
    def _number_of_tickets(self, query, value):
        aliased_targets = dict(
            (k, aliased(v)) for k, v in OrderSearchQueryBuilder.targets.items()
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


def create_inner_order(cart, note):
    request = get_current_request()
    payment_plugin_id = cart.payment_delivery_pair.payment_method.payment_plugin_id

    if payment_plugin_id == payments_plugins.SEJ_PAYMENT_PLUGIN_ID:
        # コンビニ決済のみ決済処理を行う
        payment = Payment(cart, request)
        order = payment.call_payment()
    else:
        order = Order.create_from_cart(cart)
        order.organization_id = order.performance.event.organization_id
        order.save()
        cart.order = order

        # 配送手続: 以下のモデルを生成する
        # - コンビニ受取: SejOrder
        # - QR: OrderedProductItemToken
        # - 窓口: ReservedNumber
        delivery_plugin_id = cart.payment_delivery_pair.delivery_method.delivery_plugin_id
        delivery_plugin = get_delivery_plugin(request, delivery_plugin_id)
        if delivery_plugin:
            try:
                delivery_plugin.finish(request, cart)
            except Exception as e:
                logger.error('call delivery plugin error(%s)' % e.message)
                raise Exception(u'配送手続でエラーが発生しました')
        cart.finish()

    order.note = note
    return order

def save_order_modification(order, modify_data):
    request = get_current_request()
    reserving = cart_api.get_reserving(request)
    stocker = cart_api.get_stocker(request)
    modify_order = Order.clone(order, deep=True)

    if order.channel == ChannelEnum.INNER.v:
        ppid = order.payment_delivery_pair.payment_method.payment_plugin_id
        dpid = order.payment_delivery_pair.delivery_method.delivery_plugin_id
        if ppid == payments_plugins.SEJ_PAYMENT_PLUGIN_ID or dpid == payments_plugins.SEJ_DELIVERY_PLUGIN_ID:
            raise HTTPBadRequest(body=json.dumps(dict(message=u'コンビニ決済/コンビニ発券の予約はまだ変更できません')))
    else:
        if order.payment_status != 'paid' or order.is_issued():
            logger.info('order.payment_status=%s, order.is_issued=%s' % (order.payment_status, order.is_issued()))
            raise HTTPBadRequest(body=json.dumps(dict(message=u'未決済または発券済みの予約は変更できません')))
        if order.total_amount < long(modify_data.get('total_amount')):
            raise HTTPBadRequest(body=json.dumps(dict(message=u'決済金額が増額となる変更はできません')))
        if order.total_amount > long(modify_data.get('total_amount')):
            raise HTTPBadRequest(body=json.dumps(dict(message=u'決済金額が減額となる変更はまだできません')))

    op_zip = itertools.izip(order.items, modify_order.items)
    for i, (op, mop) in enumerate(op_zip):
        op_data = None
        for op_data in modify_data.get('ordered_products'):
            if op_data.get('id') == op.id and op_data.get('product_id') == op.product_id: break
        if op_data is None:
            raise HTTPBadRequest(body=json.dumps(dict(message=u'不正なデータです')))
        logger.debug('op_data %s' % op_data)

        # 商品変更
        mop.price = long(op_data.get('price'))
        mop.quantity = long(op_data.get('quantity'))

        opi_zip = itertools.izip(op.ordered_product_items, mop.ordered_product_items)
        for j, (opi, mopi) in enumerate(opi_zip):
            opi_data = None
            for opi_data in op_data.get('ordered_product_items'):
                if opi_data.get('id') == opi.id: break
            if opi_data is None:
                raise HTTPBadRequest(body=json.dumps({'message':u'不正なデータです'}))
            logger.info('opi_data %s' % opi_data)

            # 座席開放
            mopi.release()
            mopi.seats = []

            # 座席がないなら商品明細削除
            opi_quantity = long(opi_data.get('quantity'))
            if opi_quantity == 0:
                logger.info('delete ordered_product_item %s' % opi_data.get('id'))
                del_item = mop.ordered_product_items.pop(j)
                del_item.delete()
                continue

            # 座席確保
            seats_data = opi_data.get('seats')
            product_requires = [(mop.product, opi_quantity)]
            stock_statuses = stocker.take_stock(order.performance_id, product_requires)
            seats = reserving.reserve_selected_seats(
                stock_statuses,
                order.performance_id,
                [s.get('id') for s in seats_data],
                SeatStatusEnum.Ordered
            )
            mopi.seats += seats
            mopi.price = long(opi_data.get('product_item').get('price'))
            mopi.quantity = opi_quantity
            logger.info('seats_data %s' % seats_data)

            for token in mopi.tokens:
                DBSession.delete(token)
            for i, seat in mopi.iterate_serial_and_seat():
                token = OrderedProductItemToken(
                    serial = i,
                    seat = seat,
                    valid=True
                    )
                mopi.tokens.append(token)

        # 商品削除
        if op_data.get('quantity') == 0:
            logger.info('delete ordered_product %s' % op_data.get('id'))
            del_product = modify_order.items.pop(i)
            del_product.delete()

    # 商品追加
    for op_data in modify_data.get('ordered_products'):
        if not op_data.get('id') and op_data.get('quantity') > 0:
            logger.info('add ordered_product %s' % op_data)
            product = Product.get(long(op_data.get('product_id')))
            op_quantity = long(op_data.get('quantity'))
            ordered_product = OrderedProduct(
                order=modify_order, product=product, price=product.price, quantity=op_quantity)
            for product_item in product.items:
                seats = []
                opi_quantity = long(opi_data.get('quantity'))
                if product_item.stock.stock_type.is_seat:
                    seats_data = []
                    for opi_data in op_data.get('ordered_product_items'):
                        if opi_data.get('seats'):
                            seats_data = opi_data.get('seats')
                            #1Product複数座席ProductItemでうまくいかない？
                            break
                    product_requires = [(product, opi_quantity)]
                    stock_statuses = stocker.take_stock(order.performance_id, product_requires)
                    seats = reserving.reserve_selected_seats(
                        stock_statuses,
                        order.performance_id,
                        [s.get('id') for s in seats_data],
                        SeatStatusEnum.Ordered
                    )
                    logger.info('seats_data %s' % seats_data)
                ordered_product_item = OrderedProductItem(
                    ordered_product=ordered_product,
                    product_item=product_item,
                    price=product_item.price,
                    quantity=opi_quantity,
                    seats=seats
                )
                for i, seat in ordered_product_item.iterate_serial_and_seat():
                    token = OrderedProductItemToken(
                        serial = i,
                        seat = seat,
                        valid=True
                        )
                    ordered_product_item.tokens.append(token)

    modify_order.transaction_fee = modify_data.get('transaction_fee')
    modify_order.delivery_fee = modify_data.get('delivery_fee')
    modify_order.system_fee = modify_data.get('system_fee')
    modify_order.specialfee = modify_data.get('special_fee')
    modify_order.total_amount = modify_data.get('total_amount')

    total_amount = sum(mop.price * mop.quantity for mop in modify_order.items)
    total_amount += modify_order.transaction_fee + modify_order.delivery_fee + modify_order.system_fee + modify_order.special_fee
    logger.info('total_amount %s == %s' % (total_amount, modify_order.total_amount))
    if total_amount != modify_order.total_amount:
        raise HTTPBadRequest(body=json.dumps(dict(message=u'合計金額を確認してください')))

    modify_order.operator = request.context.user
    modify_order.save()
    return modify_order

