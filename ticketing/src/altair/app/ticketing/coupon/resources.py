# -*- coding:utf-8 -*-

import logging
from pyramid.decorator import reify
from datetime import datetime, timedelta
from altair.sqlahelper import get_db_session
from altair.app.ticketing.users.models import Membership
from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.orders.models import Order, Performance
from altair.app.ticketing.payments.plugins import RESERVE_NUMBER_DELIVERY_PLUGIN_ID
from altair.app.ticketing.payments.plugins.models import ReservedNumber
from altair.app.ticketing.core.models import SalesSegment, SalesSegmentSetting
from .security import CouponSecurity

logger = logging.getLogger(__name__)


class DefaultResource(object):
    def __init__(self, request):
        self.request = request


class CouponResourceBase(object):

    def __init__(self, request):
        self.request = request
        self.session = get_db_session(request, name="slave")

    @reify
    def organization(self):
        return cart_api.get_organization(self.request)

    @reify
    def primary_membership(self):
        return self.session.query(Membership) \
            .filter_by(organization_id=self.organization.id) \
            .first()

    @reify
    def available_memberships(self):
        return self.session.query(Membership) \
            .filter_by(organization_id=self.organization.id) \
            .all()


class CouponViewResource(CouponResourceBase):

    @property
    def reserved_number(self):
        reserved_number = self.request.matchdict.get('reserved_number', None)
        return self.session.query(ReservedNumber).filter(ReservedNumber.number == reserved_number).first()

    @property
    def order(self):
        if self.reserved_number is not None:
            return Order.query.join(SalesSegment, Order.sales_segment_id == SalesSegment.id). \
                join(SalesSegmentSetting, SalesSegment.id == SalesSegmentSetting.sales_segment_id). \
                filter(Order.organization_id == self.organization.id). \
                filter(Order.order_no == self.reserved_number.order_no).first()

    @property
    def can_use(self):
        if not self.order:
            return False

        delivery_method = self.order.payment_delivery_method_pair.delivery_method
        preferences = delivery_method.preferences.get(unicode(RESERVE_NUMBER_DELIVERY_PLUGIN_ID), {})

        # 有効期限があった場合は優先
        if 'expiration_date' in preferences:
            expiration_date = preferences['expiration_date']
            if str(expiration_date).isdigit():
                start = self.order.created_at < datetime.today()
                end = datetime.now().date() < (self.order.created_at.date() + timedelta(days=(int(expiration_date) + 1)))
                if start and end:
                    return True

        # 有効期限がない場合は、公演日
        perf = self.session.query(Performance).filter(Performance.id == self.order.performance_id).first()
        if perf.start_on > datetime.today() + timedelta(minutes=1):
            if perf.end_on is None:
                return True
            if perf.end_on >= datetime.today():
                return True
        return False


    @property
    def coupon_security(self):
        return CouponSecurity()

    @property
    def all_coupon_used(self):
        for attr in self.order.items:
            for element in attr.elements:
                if element.printed_at is None:
                    return False
                for token in element.tokens:
                    if token.printed_at is None:
                        return False
        return True

    @staticmethod
    def ordered_product_item_used(element):
        for token in element.tokens:
            if token.printed_at is None:
                return False
        return True

    def use_coupon(self):
        now = datetime.now()
        token_id = self.request.matchdict.get('token_id', None)

        # 対象のクーポンだけ、発券済みにし、使用したこととする。
        for attr in self.order.items:
            for element in attr.elements:
                for token in element.tokens:
                    if str(token.id) == token_id:
                        token.printed_at = now

                    if self.ordered_product_item_used(element):
                        element.printed_at = now

        # 全てのクーポンが使用済みの場合、オーダーも発券済みとする。
        if self.all_coupon_used:
            self.order.printed_at = now
