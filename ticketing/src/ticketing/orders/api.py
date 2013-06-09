# encoding: utf-8

import re
from sqlalchemy.sql.expression import and_, or_
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

class SearchQueryBuilderBase(object):
    def __init__(self, formdata):
        self.formdata = formdata

    def handle_sort(self, query):
        if self.formdata['sort']:
            try:
                query = asc_or_desc(query, getattr(self.target, self.formdata['sort']), self.formdata['direction'], 'asc')
            except AttributeError:
                pass

        return query

    def __call__(self, query):
        for k, v in self.formdata.items():
            if v:
                callable = getattr(self, '_' + k, None)
                if callable:
                    query = callable(query, v)
        query = self.handle_sort(query)
        return query

class BaseSearchQueryBuilderMixin(object):
    def _order_no(self, query, value):
        return query.filter(self.target.order_no == value)

    def _performance_id(self, query, value):
        return query.filter(self.target.performance_id == value)

    def _event_id(self, query, value):
        return query.join(self.target.performance).filter(Performance.event_id == value)

    def _payment_method(self, query, value):
        query = query.join(self.target.payment_delivery_pair)
        query = query.join(PaymentMethod)
        if isinstance(value, list):
            query = query.filter(PaymentMethod.id.in_(value))
        else:
            query = query.filter(PaymentMethod.id == value)
        return query

    def _delivery_method(self, query, value):
        query = query.join(self.target.payment_delivery_pair)
        query = query.join(DeliveryMethod)
        query = query.filter(DeliveryMethod.id.in_(value))
        return query

    def _tel(self, query, value):
        return query.join(self.target.shipping_address).filter(or_(ShippingAddress.tel_1==value, ShippingAddress.tel_2==value))

    def _name(self, query, value):
        query = query.join(self.target.shipping_address)
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
        query = query.join(self.target.shipping_address)
        # 完全一致です
        return query \
            .join(self.target.shipping_address) \
            .filter(or_(ShippingAddress.email_1 == value,
                        ShippingAddress.email_2 == value))

    def _start_on_from(self, query, value):
        return query.join(self.target.performance).filter(Performance.start_on>=value)

    def _start_on_to(self, query, value):
        return query.join(self.target.performance).filter(Performance.start_on<=todatetime(value).replace(hour=23, minute=59, second=59))

class CartSearchQueryBuilder(SearchQueryBuilderBase, BaseSearchQueryBuilderMixin):
    target = Cart

    def _carted_from(self, query, value):
        return query.filter(self.target.created_at >= value)

    def _carted_to(self, query, value):
        return query.filter(self.target.created_at <= value)

    def _sales_segment_id(self, query, value):
        if value and '' not in value:
            query = query.join(Cart.products)
            query = query.join(CartedProduct.product)
            query = query.filter(Product.sales_segment_id.in_(value))
        return query

    def _seat_number(self, query, value):
        query = query.join(Cart.products)
        query = query.join(CartedProduct.items)
        query = query.join(CartedProductItem.seats)
        query = query.filter(Seat.name.like('%s%%' % value))
        return query

    def _status(self, query, value):
        if value == 'completed':
            query = query.filter(self.target.order_id != None)
        elif value == 'incomplete':
            query = query.filter(self.target.order_id == None)
        return query

class OrderSearchQueryBuilder(SearchQueryBuilderBase, BaseSearchQueryBuilderMixin):
    target = Order

    def _ordered_from(self, query, value):
        return query.filter(self.target.created_at >= value)

    def _ordered_to(self, query, value):
        return query.filter(self.target.created_at <= value)

    def _status(self, query, value):
        status_cond = []
        if 'ordered' in value:
            status_cond.append(and_(self.target.canceled_at==None, self.target.delivered_at==None))
        if 'delivered' in value:
            status_cond.append(and_(self.target.canceled_at==None, self.target.delivered_at!=None))
        if 'canceled' in value:
            status_cond.append(and_(self.target.canceled_at!=None))

        if status_cond:
            query = query.filter(or_(*status_cond))
        return query

    def _issue_status(self, query, value):
        issue_cond = []
        if 'issued' in value:
            issue_cond.append(self.target.issued==True)
        if 'unissued' in value:
            issue_cond.append(self.target.issued==False)

        if issue_cond:
            query = query.filter(or_(*issue_cond))
        return query

    def _sales_segment_id(self, query, value):
        if value and '' not in value:
            query = query.join(Order.ordered_products)
            query = query.join(OrderedProduct.product)
            query = query.filter(Product.sales_segment_id.in_(value))
        return query

    def _payment_status(self, query, value):
        payment_cond = []
        if 'unpaid' in value:
            payment_cond.append(and_(self.target.refunded_at==None, self.target.refund_id==None, self.target.paid_at==None))
        if 'paid' in value:
            payment_cond.append(and_(self.target.refunded_at==None, self.target.refund_id==None, self.target.paid_at!=None))
        if 'refunding' in value:
            payment_cond.append(and_(self.target.refunded_at==None, self.target.refund_id!=None))
        if 'refunded' in value:
            payment_cond.append(and_(self.target.refunded_at!=None))
        if payment_cond:
            query = query.filter(or_(*payment_cond))
        return query

    def _member_id(self, query, value):
        return query.join(self.target.user).join(User.user_credential).filter(UserCredential.auth_identifier==value)

    def _seat_number(self, query, value):
        query = query.join(Order.ordered_products)
        query = query.join(OrderedProduct.ordered_product_items)
        query = query.join(OrderedProductItem.seats)
        query = query.filter(Seat.name.like('%s%%' % value))
        return query
