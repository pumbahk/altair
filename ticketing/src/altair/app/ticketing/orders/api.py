# encoding: utf-8

import re
from sqlalchemy.sql.expression import and_, or_
from sqlalchemy.sql import functions as safunc
from sqlalchemy.orm import aliased
from pyramid.interfaces import IRequest
from altair.app.ticketing.models import asc_or_desc
from altair.app.ticketing.utils import todatetime
from altair.app.ticketing.core.models import (
    Order,
    OrderedProduct,
    OrderedProductItem,
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
from .models import OrderSummary


## backward compatibility
from altair.metadata.api import get_metadata_provider_registry
from .metadata import METADATA_NAME_ORDERED_PRODUCT
from functools import partial
get_ordered_product_metadata_provider_registry = partial(get_metadata_provider_registry,
                                                         name=METADATA_NAME_ORDERED_PRODUCT)

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
                self.targets['subject'].order_no == self.targets['SejOrder'].order_id
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
                self.targets['subject'].order_no == self.targets['SejOrder'].order_id
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
