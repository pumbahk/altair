# -*- coding:utf-8 -*-

"""

TODO: 引き当て処理自体はResourceから分離する。
TODO: cart取得
"""
import logging

from datetime import datetime, date
import itertools
from sqlalchemy import sql
from sqlalchemy.orm import joinedload
from pyramid.security import Everyone, Authenticated
from pyramid.security import Allow
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound
#from sqlalchemy.orm import joinedload
from zope.interface import implementer
from .interfaces import ICartPayment, ICartDelivery
from ticketing.payments.interfaces import IOrderPayment, IOrderDelivery 
from ticketing.users import api as user_api

from .exceptions import (
    OutTermSalesException,
    NoSalesSegment,
    NoPerformanceError,
)
from ..core import models as c_models
from ..core import api as core_api
from ..users import models as u_models
from . import models as m
from zope.deprecation import deprecate

logger = logging.getLogger(__name__)

class TicketingCartResource(object):
    __acl__ = [
        (Allow, Authenticated, 'view'),
    ]

    def __init__(self, request):
        self.request = request
        self.now = datetime.now()
        self._event_id = None
        self._event = None
        self._sales_segment_id = None
        self._populate_params()

    def _populate_params(self):
        if self.request.matchdict:
            try:
                self._event_id = long(self.request.matchdict.get('event_id'))
            except (ValueError, TypeError):
                pass
            try:
                self._sales_segment_id = long(self.request.matchdict.get('sales_segment_id'))
            except (ValueError, TypeError):
                pass

    def _get_event_id(self):
        return self._event_id

    def _set_event_id(self, value):
        self._event_id = value
        self._event = None

    event_id = property(_get_event_id, _set_event_id)

    # @property
    # def memberships(self):
    #     membergroups = self.membergroups
    #     if not membergroups:
    #         return []
    #     return [m.membership for m in membergroups]
    @property
    def memberships(self):
        organization = core_api.get_organization(self.request)
        logger.debug('organization %s' % organization.code)
        logger.debug('memberships %s' % organization.memberships)
        return organization.memberships

    @property
    def event(self):
        if self._event is None:
            # TODO: ドメインで許可されるeventのみを使う
            organization = core_api.get_organization(self.request)
            try:
                self._event = c_models.Event.filter(c_models.Event.id==self.event_id).filter(c_models.Event.organization==organization).one()
            except NoResultFound:
                self._event = None
        return self._event

    @property
    def performance(self):
        return self.sales_segment.performance

    @reify
    def membergroups(self):
        sales_segment = self.sales_segment
        if sales_segment is None:
            return []
        return sales_segment.membergroups

    ## なぜ２つ?
    def available_payment_delivery_method_pairs(self, sales_segment):
        return sales_segment.available_payment_delivery_method_pairs(getattr(self, 'now', datetime.now()))
    ## 
    def get_payment_delivery_method_pair(self, start_on=None):
        segment = self.sales_segment
        q = c_models.PaymentDeliveryMethodPair.query.filter(
            c_models.PaymentDeliveryMethodPair.sales_segment_group_id==segment.id
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
    def sales_segments(self):
        """現在認証済みのユーザとイベントに関連する全販売区分"""
        if self.event is None:
            raise HTTPNotFound()
        return self.event.query_sales_segments(
            user=self.authenticated_user(),
            type='all'
        ).options(
            joinedload(c_models.SalesSegment.payment_delivery_method_pairs),
            joinedload(c_models.SalesSegment.performance),
            joinedload(c_models.SalesSegment.performance,
                       c_models.Performance.venue),
            joinedload(c_models.SalesSegment.performance,
                       c_models.Performance.event),
        ).all()

    @reify
    def available_sales_segments(self):
        """現在認証済みのユーザが今買える全販売区分"""
        per_performance_sales_segments_dict = {}
        for sales_segment in self.sales_segments:
            if sales_segment.available_payment_delivery_method_pairs(self.now) and \
               sales_segment.in_term(self.now):
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
            # 次の販売区分があるなら
            data = c_models.Event.find_next_and_last_sales_segment_period(
                sales_segments=self.sales_segments,
                now=self.now)
            if any(data):
                for datum in data:
                    if datum is not None:
                        datum['event'] = datum['performance'].event
                raise OutTermSalesException(*data)
            else:
                raise HTTPNotFound()
        return retval

    @reify
    def sales_segment(self):
        """ 該当イベントのSalesSegment取得
        """
        if self._sales_segment_id is None:
            raise NoSalesSegment()

        # XXX: 件数少ないしリニアサーチでいいよね
        for sales_segment in self.available_sales_segments:
            if sales_segment.id == self._sales_segment_id:
                return sales_segment

        raise NoSalesSegment()

    def get_sales_segment(self):
        return self.sales_segment

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

    @deprecate('use ticketing.users.api.get_or_create_user')
    def get_or_create_user(self):
        return user_api.get_or_create_user(self.authenticated_user())

    @reify
    def host_base_url(self):
        return core_api.get_host_base_url(self.request)

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
