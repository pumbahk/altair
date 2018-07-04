# -*- coding:utf-8 -*-

import logging
from datetime import datetime, timedelta

from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.core.models import SalesSegment, SalesSegmentSetting
from altair.app.ticketing.orders.models import Order, Performance
from altair.app.ticketing.payments.plugins import RESERVE_NUMBER_DELIVERY_PLUGIN_ID
from altair.app.ticketing.payments.plugins.models import ReservedNumber
from altair.app.ticketing.users.models import Membership
from altair.sqlahelper import get_db_session
from pyramid.decorator import reify

import api
from models import PassportUser
from .helper import PassportHelper
from .security import PassportSecurity

logger = logging.getLogger(__name__)


class DefaultResource(object):
    def __init__(self, request):
        self.request = request


class PassportResourceBase(object):

    def __init__(self, request):
        self.request = request
        self.session = get_db_session(request, name="slave")
        self.helper = PassportHelper()

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


class PassportViewResource(PassportResourceBase):

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

        # 相対有効期限があった場合は優先
        if 'expiration_date' in preferences:
            expiration_date = preferences['expiration_date']
            if str(expiration_date).isdigit():
                return self.can_use_expiration_date(expiration_date)

        # 相対有効期限がない場合は、公演期間のみ使用可
        return self.can_use_performance_term()

    def can_use_expiration_date(self, expiration_date):
        if not self.order.created_at < datetime.today():
            return False

        if not (datetime.now().date() <= (self.order.created_at.date() + timedelta(days=(int(expiration_date))))):
            return False

        return True

    def can_use_performance_term(self):
        perf = self.session.query(Performance).filter(Performance.id == self.order.performance_id).first()
        if perf.end_on:
            # 終了日時が指定されている場合は、その時刻まで入場できる
            if datetime.today() < perf.end_on:
                return True
        else:
            # 終了日時が指定されていない場合は、公演時刻まで入れる
            if datetime.today() <= perf.start_on:
                return True
        return False

    @property
    def passport_user(self):
        passport_user_id = self.request.matchdict.get('passport_user_id', None)
        return PassportUser.get(passport_user_id)

    @property
    def passport_security(self):
        return PassportSecurity()

    @property
    def all_passport_used(self):
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

    def use_passport(self, passport_user_id=None):
        if not passport_user_id:
            passport_user_id = self.request.matchdict.get('passport_user_id', None)
        api.use_passport(passport_user_id)

    def use_all_passport(self):
        for user in self.order.users:
            api.use_passport(user.id)
