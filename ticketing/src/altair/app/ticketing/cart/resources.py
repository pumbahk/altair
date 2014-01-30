# -*- coding:utf-8 -*-

import logging

from datetime import datetime, date
import itertools
from sqlalchemy import sql
from pyramid.security import Everyone, Authenticated
from pyramid.security import Allow
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.orm import joinedload, joinedload_all
from sqlalchemy.orm.exc import NoResultFound
from zope.interface import implementer
from .interfaces import ICartPayment, ICartDelivery
from altair.app.ticketing.payments.interfaces import IOrderPayment, IOrderDelivery 
from altair.app.ticketing.users import api as user_api
from altair.app.ticketing.users import models as u_models
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.core import api as core_api
from altair.app.ticketing.core.interfaces import IOrderQueryable
from altair.app.ticketing.users import models as u_models
from . import models as m
from .api import get_cart_safe
from .exceptions import NoCartError
from .interfaces import ICartContext
from .exceptions import (
    OutTermSalesException,
    NoSalesSegment,
    NoPerformanceError,
    OverOrderLimitException,
    OverQuantityLimitException,
)
from zope.deprecation import deprecate
from altair.now import get_now
import functools

logger = logging.getLogger(__name__)

# https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
class memoize(object):
    def __init__(self, cache_attr_name=None):
        self.cache_attr_name = cache_attr_name

    def __call__(self, fn):
        if self.cache_attr_name is None:
            cache_attr_name = '_cache_%s' % fn.__name__
        else:
            cache_attr_name = self.cache_attr_name
        @functools.wraps(fn)
        def memoizer(_self, *args, **kwargs):
            cache = getattr(_self, cache_attr_name, None)
            if cache is None:
                cache = {}
                setattr(_self, cache_attr_name, cache)
            key = (args, tuple(kwargs.items()))
            if key not in cache:
                cache[key] = fn(_self, *args, **kwargs)
            return cache[key]
        return memoizer

@implementer(ICartContext)
class TicketingCartResourceBase(object):
    __acl__ = [
        (Allow, Authenticated, 'view'),
    ]

    def __init__(self, request, sales_segment_id=None):
        self.request = request
        self.now = get_now(request)
        self._sales_segment_id = sales_segment_id
        self._sales_segment = None
        self._populate_params()

    def _populate_params(self):
        if self.request.matchdict:
            self._populate_matchdict_params()

    def _populate_matchdict_params(self):
        try:
            self._sales_segment_id = long(self.request.matchdict.get('sales_segment_id'))
        except (ValueError, TypeError):
            pass

    @reify
    def cart(self):
        return get_cart_safe(self.request, for_update=True) 

    @property
    def sales_segments(self):
        """現在のURLから決定できるすべての販売区分"""
        raise NotImplementedError()

    @property
    def event(self):
        raise NotImplementedError()

    @property
    def performance(self):
        raise NotImplementedError()

    @property
    def memberships(self):
        organization = core_api.get_organization(self.request)
        logger.debug('organization %s' % organization.code)
        logger.debug('memberships %s' % organization.memberships)
        return organization.memberships

    @reify
    def membergroups(self):
        sales_segment = self.sales_segment
        if sales_segment is None:
            return []
        return sales_segment.membergroups

    ## なぜ２つ?
    def available_payment_delivery_method_pairs(self, sales_segment):
        return sales_segment.available_payment_delivery_method_pairs(self.now) #xxx?
    ## 

    def get_payment_delivery_method_pair(self, start_on=None):
        sales_segment = self.sales_segment
        q = c_models.PaymentDeliveryMethodPair.query.filter(
            c_models.PaymentDeliveryMethodPair.sales_segment_group_id==sales_segment.id
        ).filter(
            c_models.PaymentDeliveryMethodPair.public==1,
        ).order_by(
            c_models.PaymentDeliveryMethodPair.transaction_fee,
            c_models.PaymentDeliveryMethodPair.payment_method_id,
            c_models.PaymentDeliveryMethodPair.delivery_fee,
            c_models.PaymentDeliveryMethodPair.delivery_method_id,
        )
        if start_on:
            today = date.today()
            period_days = date(start_on.year, start_on.month, start_on.day) - today
            q = q.filter(
                c_models.PaymentDeliveryMethodPair.unavailable_period_days<=period_days.days
            )
        pairs = q.all()
        return pairs

    def authenticated_user(self):
        """現在認証中のユーザ"""
        from altair.rakuten_auth.api import authenticated_user
        user = authenticated_user(self.request)
        return user or { 'is_guest': True }

    @reify
    def available_sales_segments(self):
        """現在認証済みのユーザが今買える全販売区分"""
        per_performance_sales_segments_dict = {}
        cart = None
        try:
            cart = self.cart
        except NoCartError as e:
            logger.info('cart is not created (%s)' % e)

        for sales_segment in self.sales_segments:
            if (cart and cart.sales_segment_id == sales_segment.id) \
               or (sales_segment.available_payment_delivery_method_pairs(self.now) and \
                   sales_segment.in_term(self.now)):
                per_performance_sales_segments = \
                    per_performance_sales_segments_dict.get(sales_segment.performance_id)
                if per_performance_sales_segments is None:
                    per_performance_sales_segments = per_performance_sales_segments_dict[sales_segment.performance_id] = ([], [])
                per_performance_sales_segments[sales_segment.sales_segment_group.has_guest and 1 or 0].append(sales_segment)

        # 何してるか意味不明だと思うんですけど
        # per_performance_sales_segment_dict = {
        #    1L: ([非guest用販売区分, ...], [guest用販売区分, ...]),
        #    2L: ([非guest用販売区分, ...], [guest用販売区分, ...]),
        #    ...
        # }
        # となっていて、(キーはパフォーマンスのid)
        # 各パフォーマンスで非guest用の販売区分があればそれを優先し
        # guest用の販売区分しかなければそれを使うということをする
        # 
        # itertools.chain([[非guest用販売区分, ...], [guest用販売区分, ...], [guest用販売区分...]])
        #
        # ということ。
        # ここで performance の情報を捨ててしまうのがちょっともったいない。

        retval = list(itertools.chain(*((pair[0] or pair[1]) for pair in per_performance_sales_segments_dict.itervalues())))
        if not retval:
            # 公演が指定されてるなら販売区分を絞る
            sales_segments = self.sales_segments
            # 次の販売区分があるなら
            data = c_models.Event.find_next_and_last_sales_segment_period(
                sales_segments=sales_segments,
                now=self.now)
            if any(data):
                for datum in data:
                    if datum is not None:
                        datum['event'] = datum['performance'].event
                raise OutTermSalesException.from_resource(self, self.request, next=data[0], last=data[1], type_=self.__class__)
            else:
                raise HTTPNotFound()
        return retval

    @reify
    def sales_segment(self):
        """ 該当イベントのSalesSegment取得
        """
        if self._sales_segment_id is None:
            logger.info("sales_segment_id is not provided")
            raise NoSalesSegment.from_resource(self, self.request, sales_segment_id=None)

        # XXX: 件数少ないしリニアサーチでいいよね
        for sales_segment in self.available_sales_segments:
            if sales_segment.id == self._sales_segment_id:
                return sales_segment

        raise NoSalesSegment.from_resource(self, self.request, sales_segment_id=None)

    def get_sales_segment(self):
        return self.sales_segment

    @property
    def raw_sales_segment(self):
        if self._sales_segment is None:
            if self._sales_segment_id is None:
                return None
            organization = core_api.get_organization(self.request)
            sales_segment = None
            try:
                sales_segment = c_models.SalesSegment.query \
                    .join(c_models.SalesSegment.sales_segment_group) \
                    .join(c_models.SalesSegmentGroup.event) \
                    .filter(c_models.Event.organization_id == organization.id) \
                    .filter(c_models.SalesSegment.id == self._sales_segment_id) \
                    .one()
            except:
                pass
            self._sales_segment = sales_segment
        return self._sales_segment

    @property
    def membership(self):
        from altair.rakuten_auth.api import authenticated_user
        user = authenticated_user(self.request)
        if user is None:
            return None
        if 'membership' not in user:
            return None

        membership = user['membership']
        return membership

    @reify
    def user_object(self):
        return user_api.get_user(self.authenticated_user())

    @reify
    def host_base_url(self):
        return core_api.get_host_base_url(self.request)

    @memoize()
    def get_total_orders_and_quantities_per_user(self, sales_segment):
        """ユーザごとのこれまでの注文数や購入数を取得する"""
        setting = sales_segment.setting
        user = self.user_object
        mail_addresses = None
        try:
            mail_addresses = self.cart.shipping_address and self.cart.shipping_address.emails
        except NoCartError:
            pass
        retval = []
        if user or mail_addresses:
            while setting is not None:
                # 設定なしの場合は何度でも購入可能
                container = setting.container
                if IOrderQueryable.providedBy(container):
                    from altair.app.ticketing.models import DBSession
                    if user:
                        order_query = container.query_orders_by_user(user, filter_canceled=True)
                    elif mail_addresses:
                        order_query = container.query_orders_by_mailaddresses(mail_addresses, filter_canceled=True)
                    query = order_query.add_columns(sql.expression.func.sum(c_models.OrderedProductItem.quantity)) \
                        .outerjoin(c_models.OrderedProduct, c_models.Order.items) \
                        .outerjoin(c_models.OrderedProductItem, c_models.OrderedProduct.elements) \
                        .group_by(c_models.Order.id)
                    quantities_per_order = list(int(quantity_sum or 0) for _, quantity_sum in query)
                    logger.info(
                        "%r(id=%d): order_limit=%r, max_quantity_per_user=%r, orders=%d, total_quantity=%d" % (
                            container.__class__,
                            container.id,
                            setting.order_limit,
                            setting.max_quantity_per_user,
                            len(quantities_per_order),
                            sum(quantities_per_order)
                            )
                        )
                    retval.append(
                        (
                            container,
                            dict(
                                order_count=len(quantities_per_order),
                                total_quantity=sum(quantities_per_order),
                                order_limit=setting.order_limit,
                                max_quantity_per_user=setting.max_quantity_per_user
                                )
                            )
                        )
                else:
                    logger.info("%s does not implement IOrderQueryable. skip" % container.__class__)
                setting = setting.super
        return retval

    def check_order_limit(self):
        """ 購入回数および購入枚数制限チェック
        設定なしの場合は何度でも購入可能です。
        カウントするOrder数にcancelされたOrderは含まれません。
        """
        cart_total_quantity = sum(element.quantity for item in self.cart.items for element in item.elements)
        total_orders_and_quantities_per_user = self.get_total_orders_and_quantities_per_user(self.cart.sales_segment)
        for container, record in total_orders_and_quantities_per_user:
            order_limit = record['order_limit']
            max_quantity_per_user = record['max_quantity_per_user']
            order_count = record['order_count']
            total_quantity = record['total_quantity']
            # XXX: order_limit はかつて 0 が無効値だった...
            if order_limit and order_count >= order_limit:
                logger.info("order_limit exceeded: %d >= %d" % (order_count, order_limit))
                raise OverOrderLimitException.from_resource(self, self.request, order_limit=order_limit)
            if max_quantity_per_user is not None:
                if total_quantity + cart_total_quantity > max_quantity_per_user:
                    logger.info("order_limit exceeded: %d >= %d" % (total_quantity, max_quantity_per_user))
                    raise OverQuantityLimitException.from_resource(self, self.request, quantity_limit=max_quantity_per_user)

    @reify
    def login_required(self):
        if self.event is None:
            return False
        if self.event.organization.setting.auth_type == "rakuten":
            return True

        """ 指定イベントがログイン画面を必要とするか """
        # 終了分もあわせて、このeventからひもづく sales_segment -> membergroupに1つでもguestがあれば True 
        q = u_models.MemberGroup.query.filter(
            u_models.MemberGroup.is_guest==False
        ).filter(
            u_models.MemberGroup.id == u_models.MemberGroup_SalesSegment.c.membergroup_id
        ).filter(
            c_models.SalesSegment.id == u_models.MemberGroup_SalesSegment.c.sales_segment_id
        )
        while True:
            # まずは販売区分を見る
            sales_segment = None
            try:
                sales_segment = self.sales_segment
            except:
                pass
            if sales_segment is not None:
                q = q.filter(
                    c_models.SalesSegment.sales_segment_id == sales_segment.id
                )
                break

            # 次にパフォーマンス
            performance = None
            try:
                performance = self.performance
            except:
                pass
            if performance is not None:
                q = q.filter(
                    c_models.SalesSegment.performance_id == performance.id
                    )
                break

            # 最後にイベントを見て
            event = None
            try:
                event = self.event
            except:
                pass
            if event is not None:
                q = q.filter(
                    c_models.SalesSegment.event_id == event.id
                    )
                break

            # MemberGroup を特定できるものがなければ、エラーにする
            logger.error("could not determine the event, performance nor sales_segment from the request URI")
            return True

        logger.info(str(q))
        return q.first() is not None


class EventOrientedTicketingCartResource(TicketingCartResourceBase):
    def __init__(self, request, event_id=None):
        self._event_id = event_id
        self._event = None
        super(EventOrientedTicketingCartResource, self).__init__(request)

    def _populate_matchdict_params(self):
        super(EventOrientedTicketingCartResource, self)._populate_matchdict_params()
        if self._event_id is None:
            try:
                self._event_id = long(self.request.matchdict.get('event_id'))
            except (ValueError, TypeError):
                pass

    @property
    def event(self):
        performance = self.performance
        if performance is not None:
            return performance.event

        if self._event is None:
            organization = core_api.get_organization(self.request)
            event = None
            try:
                event = c_models.Event.query \
                    .options(joinedload(c_models.Event.setting)) \
                    .filter(c_models.Event.id==self._event_id) \
                    .filter(c_models.Event.organization==organization) \
                    .one()
            except NoResultFound:
                pass
            self._event = event
        return self._event

    @property
    def performance(self):
        sales_segment = self.raw_sales_segment
        if sales_segment is not None and sales_segment.sales_segment_group.event_id == self._event_id:
            return sales_segment.performance
        cart = None
        try:
            cart = self.cart
        except NoCartError:
            pass
        if cart is not None and (self._event_id is None or cart.performance.event_id == self._event_id):
            return cart.performance
        return None

    @reify
    def sales_segments(self):
        """現在認証済みのユーザとイベントに関連する全販売区分"""
        if self.event is None:
            raise HTTPNotFound()
        return self.event.query_sales_segments(
            user=self.authenticated_user(),
            type='all').all()

class PerformanceOrientedTicketingCartResource(TicketingCartResourceBase):
    def __init__(self, request, performance_id=None):
        self._performance_id = performance_id
        self._performance = None
        super(PerformanceOrientedTicketingCartResource, self).__init__(request)

    def _populate_matchdict_params(self):
        super(PerformanceOrientedTicketingCartResource, self)._populate_matchdict_params()
        if self._performance_id is None:
            try:
                self._performance_id = long(self.request.matchdict.get('performance_id'))
            except (ValueError, TypeError):
                pass

    @property
    def performance(self):
        if self._performance_id is None:
            cart = None
            try:
                cart = self.cart
            except NoCartError:
                pass
            if cart is not None:
                return cart.performance
        else:
            if self._performance is None:
                organization = core_api.get_organization(self.request)
                performance = None
                try:
                    performance = c_models.Performance.query \
                        .options(joinedload_all(c_models.Performance.event, c_models.Event.setting)) \
                        .join(c_models.Performance.event) \
                        .filter(c_models.Performance.id == self._performance_id) \
                        .filter(c_models.Event.organization_id == organization.id) \
                        .one()
                except NoResultFound:
                    pass
                if performance is None:
                    raise NoPerformanceError('Performance (id=%d) not found' % self._performance_id)
                self._performance = performance
            return self._performance

    @property
    def event(self):
        return self.performance.event

    @reify
    def sales_segments(self):
        """現在認証済みのユーザとパフォーマンスに関連する全販売区分"""
        if self.performance is None:
            raise HTTPNotFound()
        return self.performance.query_sales_segments(
            user=self.authenticated_user(),
            type='all').all()


class SalesSegmentOrientedTicketingCartResource(TicketingCartResourceBase):
    def __init__(self, request, sales_segment_id=None):
        super(SalesSegmentOrientedTicketingCartResource, self).__init__(request, sales_segment_id)

    @reify
    def sales_segment(self):
        return self.raw_sales_segment

    @property
    def performance(self):
        return self.raw_sales_segment.performance

    @property
    def event(self):
        return self.performance.event

    @reify
    def sales_segments(self):
        """現在認証済みのユーザとパフォーマンスに関連する全販売区分"""
        if self.sales_segment is None:
            raise HTTPNotFound()
        return [self.sales_segment] if self.sales_segment.applicable(user=self.authenticated_user(), type='all') else []

# def compat_ticketing_cart_resource_factory(request):
#     from .resources import EventOrientedTicketingCartResource, PerformanceOrientedTicketingCartResource
#     performance_id = None
#     try:
#         performance_id = long(request.params.get('pid') or request.params.get('performance'))
#     except (ValueError, TypeError):
#         pass
#     if performance_id is not None:
#         return PerformanceOrientedTicketingCartResource(request, performance_id)
#     else:
#         return EventOrientedTicketingCartResource(request)

compat_ticketing_cart_resource_factory = EventOrientedTicketingCartResource

@implementer(IOrderDelivery)
class OrderDelivery(object):
    def __init__(self, order):
        self.order = order

@implementer(ICartDelivery)
class CartDelivery(object):
    def __init__(self, cart):
        self.cart = cart

@implementer(IOrderPayment)
class OrderPayment(object):
    def __init__(self, order):
        self.order = order

@implementer(ICartPayment)
class CartPayment(object):
    def __init__(self, cart):
        self.cart = cart
