# -*- coding:utf-8 -*-

import logging
from datetime import datetime
from dateutil import parser
from pyramid.decorator import reify
from pyramid.security import effective_principals, Allow, Authenticated, DENY_ALL
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound
from altair.sqlahelper import get_db_session
from altair.app.ticketing.cart.api import get_auth_info
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.orders.models import Order
from altair.app.ticketing.core.models import SalesSegment, SalesSegmentSetting, ShippingAddress, Organization
from altair.app.ticketing.lots.models import LotEntry
from altair.app.ticketing.users.models import User, UserCredential, Membership, UserProfile
import webhelpers.paginate as paginate
from altair.app.ticketing.core import api as core_api
from altair.app.ticketing.cart import api as cart_api
from .api import get_user_point_accounts

logger = logging.getLogger(__name__)

class DefaultResource(object):
    def __init__(self, request):
        self.request = request

class OrderReviewResourceBase(object):
    __acl__ = [
        (Allow, Authenticated, '*'),
        DENY_ALL,
        ]

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

    @reify
    def user_point_accounts(self):
        if not self.order:
            return None
        return get_user_point_accounts(self.request, self.order.user_id)

    def authenticated_user(self):
        """現在認証中のユーザ"""
        return get_auth_info(self.request)


class LandingViewResource(OrderReviewResourceBase):
    pass

class MyPageListViewResource(OrderReviewResourceBase):
    def get_orders(self, user, page, per):
        #disp_orderreviewは、マイページに表示するかしないかのフラグとなった
        orders = self.session.query(Order).join(SalesSegment, Order.sales_segment_id==SalesSegment.id). \
            join(SalesSegmentSetting, SalesSegment.id == SalesSegmentSetting.sales_segment_id). \
            filter(Order.organization_id==self.organization.id). \
            filter(Order.user_id==user.id). \
            filter(SalesSegmentSetting.disp_orderreview==True). \
            order_by(Order.updated_at.desc())

        orders = paginate.Page(orders.all(), page, per, url=paginate.PageURL_WebOb(self.request))
        return orders

    def get_lots_entries(self, user, page, per):
        entries = LotEntry.query.filter(
            LotEntry.user_id==user.id
        ).order_by(LotEntry.updated_at.desc())
        entries = paginate.Page(entries.all(), page, per, url=paginate.PageURL_WebOb(self.request))
        return entries


class OrderReviewResource(OrderReviewResourceBase): 
    def __init__(self, request):
        super(OrderReviewResource, self).__init__(request)
        try:
            self.order_no = self.request.params['order_no']
        except KeyError:
            raise HTTPNotFound()
        self._order = None

    def _populate_order(self):
        if self._order is not None:
            return
        order_no = self.order_no
        order = self.session.query(Order).join(SalesSegment, Order.sales_segment_id==SalesSegment.id). \
            join(SalesSegmentSetting, SalesSegment.id == SalesSegmentSetting.sales_segment_id). \
            filter(Order.organization_id==self.organization.id). \
            filter(Order.order_no==order_no).first()
        logger.info("organization_id=%s, order_no=%s, order=%s" % (self.organization.id, order_no, order))
        self._order = order

    @property
    def order(self):
        self._populate_order()
        return self._order

    @reify
    def cart_setting(self):
        return self.order.cart_setting

    def order_detail_panel(self, order):
        panel_name = 'order_detail.%s' % self.cart_setting.type
        return self.request.layout_manager.render_panel(panel_name, self.order, self.user_point_accounts)


class QRViewResource(OrderReviewResourceBase):
    pass

class EventGateViewResource(OrderReviewResourceBase):
    pass

class ContactViewResource(OrderReviewResourceBase):
    pass
