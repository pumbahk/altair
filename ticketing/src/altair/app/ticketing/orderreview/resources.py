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
from altair.app.ticketing.payments import plugins
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.orders.models import Order
from altair.app.ticketing.core.models import SalesSegment, SalesSegmentSetting, ShippingAddress, Organization
from altair.app.ticketing.lots.models import LotEntry
from altair.app.ticketing.users.models import User, UserCredential, Membership, UserProfile
import webhelpers.paginate as paginate
from altair.app.ticketing.core import api as core_api
from altair.app.ticketing.cart import api as cart_api
from .views import unsuspicious_order_filter
from .schemas import OrderReviewSchema
from .exceptions import InvalidForm

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
        return self.order.user_point_accounts

    def authenticated_user(self):
        """現在認証中のユーザ"""
        return get_auth_info(self.request)


class LandingViewResource(OrderReviewResourceBase):
    pass

from .views import unsuspicious_order_filter

class MyPageListViewResource(OrderReviewResourceBase):
    def get_orders(self, user, page, per):
        #disp_orderreviewは、マイページに表示するかしないかのフラグとなった
        orders = self.session.query(Order).join(SalesSegment, Order.sales_segment_id==SalesSegment.id). \
            join(SalesSegmentSetting, SalesSegment.id == SalesSegmentSetting.sales_segment_id). \
            filter(Order.organization_id==self.organization.id). \
            filter(Order.user_id==user.id). \
            filter(SalesSegmentSetting.disp_orderreview==True). \
            order_by(Order.updated_at.desc())
        orders = unsuspicious_order_filter(orders)  # refs 10883
        orders = paginate.Page(orders, page, per, url=paginate.PageURL_WebOb(self.request))
        return orders

    def get_lots_entries(self, user, page, per):
        entries = LotEntry.query.filter(
            LotEntry.user_id==user.id
        ).order_by(LotEntry.updated_at.desc())

        entries = unsuspicious_order_filter(entries)  # refs 10883
        entries = paginate.Page(entries, page, per, url=paginate.PageURL_WebOb(self.request))

        return entries


class OrderReviewResource(OrderReviewResourceBase):
    def __init__(self, request):
        super(OrderReviewResource, self).__init__(request)
        form = OrderReviewSchema(self.request.POST)
        if not form.validate():
            raise InvalidForm(form)
        order_no = form.order_no.data
        order = self.session.query(Order).join(SalesSegment, Order.sales_segment_id==SalesSegment.id). \
            join(SalesSegmentSetting, SalesSegment.id == SalesSegmentSetting.sales_segment_id). \
            filter(Order.organization_id==self.organization.id). \
            filter(Order.order_no==order_no).first()
        logger.info("organization_id=%s, order_no=%s, order=%s" % (self.organization.id, order_no, order))
        if order is None:
            raise InvalidForm(form, errors=[u'受付番号または電話番号が違います。'])
        tel = form.tel.data
        if not order.shipping_address or tel not in [_tel.replace('-', '') for _tel in order.shipping_address.tels]:
            raise InvalidForm(form, errors=[u'受付番号または電話番号が違います。'])
        if order.payment_delivery_pair.delivery_method.delivery_plugin_id == plugins.ORION_DELIVERY_PLUGIN_ID and \
           (order.performance is None or order.performance.orion is None):
            logger.warn("Performance %s has not OrionPerformance." % order.performance.code)
        self.form = form
        self.order = order

    @reify
    def cart_setting(self):
        return self.order.cart_setting

    def order_detail_panel(self, order):
        panel_name = 'order_detail.%s' % self.cart_setting.type
        return self.request.layout_manager.render_panel(panel_name, self.order, self.user_point_accounts)


class MyPageOrderReviewResource(OrderReviewResourceBase): 
    def __init__(self, request):
        super(MyPageOrderReviewResource, self).__init__(request)
        order_no = self.request.params['order_no']
        order = self.session.query(Order).join(SalesSegment, Order.sales_segment_id==SalesSegment.id). \
            join(SalesSegmentSetting, SalesSegment.id == SalesSegmentSetting.sales_segment_id). \
            filter(Order.organization_id==self.organization.id). \
            filter(Order.order_no==order_no).first()
        logger.info("organization_id=%s, order_no=%s, order=%s" % (self.organization.id, order_no, order))
        if order is None:
            raise HTTPNotFound()
        if order.payment_delivery_pair.delivery_method.delivery_plugin_id == plugins.ORION_DELIVERY_PLUGIN_ID and \
           (order.performance is None or order.performance.orion is None):
            logger.warn("Performance %s has not OrionPerformance." % order.performance.code)
        self.order = order
        authenticated_user = self.authenticated_user()
        user = cart_api.get_user(authenticated_user)
        if user is None or self.order.user_id != user.id:
            raise HTTPNotFound() 

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
