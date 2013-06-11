# encoding: utf-8

import re
from sqlalchemy.sql.expression import and_, or_
from sqlalchemy.sql import functions as safunc
from sqlalchemy.orm import aliased
from ticketing.models import asc_or_desc
from ticketing.helpers import todatetime
from ticketing.core.models import (
    Order,
    OrderedProduct,
    OrderedProductItem,
    Product,
    PaymentMethod,
    DeliveryMethod,
    ShippingAddress,
    Seat,
    Performance,
    )
from ticketing.cart.models import (
    Cart,
    CartedProduct,
    CartedProductItem,
    )
from ticketing.users.models import (
    User,
    UserCredential,
    )

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
    def __init__(self, formdata, key_name_resolver=None, targets=None, excludes=[]):
        self.formdata = formdata
        self.key_name_resolver = key_name_resolver
        if targets:
            self.targets = targets
        self.excludes = excludes
        self.post_queue = None

    def handle_sort(self, query):
        if self.formdata['sort']:
            try:
                query = asc_or_desc(query, getattr(self.target, self.formdata['sort']), self.formdata['direction'], 'asc')
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
        query = self.handle_sort(query)
        return query

class BaseSearchQueryBuilderMixin(object):
    def _order_no(self, query, value):
        return query.filter(self.targets['subject'].order_no == value)

    def _performance_id(self, query, value):
        return query.filter(self.targets['subject'].performance_id == value)

    def _event_id(self, query, value):
        return query.join(self.targets['subject'].performance).filter(Performance.event_id == value)

    def _payment_method(self, query, value):
        query = query.join(self.targets['subject'].payment_delivery_pair)
        query = query.join(PaymentMethod)
        if isinstance(value, list):
            query = query.filter(PaymentMethod.id.in_(value))
        else:
            query = query.filter(PaymentMethod.id == value)
        return query

    def _delivery_method(self, query, value):
        query = query.join(self.targets['subject'].payment_delivery_pair)
        query = query.join(DeliveryMethod)
        query = query.filter(DeliveryMethod.id.in_(value))
        return query

    def _tel(self, query, value):
        return query.join(self.targets['subject'].shipping_address).filter(or_(ShippingAddress.tel_1==value, ShippingAddress.tel_2==value))

    def _name(self, query, value):
        query = query.join(self.targets['subject'].shipping_address)
        items = re.split(ur'[ 　]', value)
        # 前方一致で十分かと
        for item in items:
            query = query.filter(
                or_(
                    or_(ShippingAddress.first_name.like('%s%%' % item),
                        ShippingAddress.last_name.like('%s%%' % item)),
                    or_(ShippingAddress.first_name_kana.like('%s%%' % item),
                        ShippingAddress.last_name_kana.like('%s%%' % item))
                    )
                )
        return query

    def _email(self, query, value): 
        query = query.join(self.targets['subject'].shipping_address)
        # 完全一致です
        return query \
            .join(self.targets['subject'].shipping_address) \
            .filter(or_(ShippingAddress.email_1 == value,
                        ShippingAddress.email_2 == value))

    def _start_on_from(self, query, value):
        return query.join(self.targets['subject'].performance).filter(Performance.start_on>=value)

    def _start_on_to(self, query, value):
        return query.join(self.targets['subject'].performance).filter(Performance.start_on<=todatetime(value).replace(hour=23, minute=59, second=59))

class CartSearchQueryBuilder(SearchQueryBuilderBase, BaseSearchQueryBuilderMixin):
    targets = {
        'subject': Cart,
        'CartedProduct': CartedProduct,
        'CartedProductItem': CartedProductItem,
        'Product': Product,
        'Seat': Seat,
        }

    def _carted_from(self, query, value):
        return query.filter(self.targets['subject'].created_at >= value)

    def _carted_to(self, query, value):
        return query.filter(self.targets['subject'].created_at <= value)

    def _sales_segment_id(self, query, value):
        if value and '' not in value:
            query = query.join(self.targets['subject'].products)
            query = query.join(self.targets['CartedProduct'].product)
            query = query.filter(self.targets['Product'].sales_segment_id.in_(value))
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
        'OrderedProduct': OrderedProduct,
        'OrderedProductItem': OrderedProductItem,
        'Product': Product,
        'Seat': Seat,
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
        query = query.filter(
            self.targets['subject'].id.in_(
                self.__class__(self.formdata, self.key_name_resolver, aliased_targets, excludes=['number_of_tickets'])(
                    query.session.query(aliased_targets['subject'].id) \
                        .join(aliased_targets['OrderedProduct']) \
                        .join(aliased_targets['OrderedProductItem']) \
                        .distinct()
                    ) \
                    .group_by(aliased_targets['subject'].id,
                              aliased_targets['OrderedProductItem'].product_item_id) \
                    .having(safunc.sum(aliased_targets['OrderedProductItem'].quantity) >= value) \
                )
            )
        return query
