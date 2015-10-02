# -*- coding:utf-8 -*-

import logging
from pyramid.decorator import reify
from pyramid.security import effective_principals, Allow, Authenticated, DENY_ALL
from altair.sqlahelper import get_db_session
from altair.app.ticketing.cart.api import get_auth_info
from altair.app.ticketing.users.models import Membership
from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.orders.models import Order
from altair.app.ticketing.payments.plugins.models import ReservedNumber
from altair.app.ticketing.core.models import SalesSegment, SalesSegmentSetting, ShippingAddress, Organization

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
        return self.session.query(ReservedNumber).filter(ReservedNumber.number==reserved_number).first()

    @property
    def order(self):
        if self.reserved_number is not None:
            return Order.query.join(SalesSegment, Order.sales_segment_id==SalesSegment.id). \
                join(SalesSegmentSetting, SalesSegment.id == SalesSegmentSetting.sales_segment_id). \
                filter(Order.organization_id==self.organization.id). \
                filter(Order.order_no==self.reserved_number.order_no).first()
