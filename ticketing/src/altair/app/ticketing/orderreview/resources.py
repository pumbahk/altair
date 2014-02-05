# -*- coding:utf-8 -*-

import logging
from datetime import datetime
from dateutil import parser
from pyramid.decorator import reify
from sqlalchemy.orm.exc import NoResultFound
from altair.sqlahelper import get_db_session
from altair.app.ticketing.core.models import DBSession, Order, ShippingAddress
from altair.app.ticketing.lots.models import LotEntry
from altair.app.ticketing.users.models import User, UserCredential, Membership, UserProfile
from altair.app.ticketing.sej.api import get_sej_order
import webhelpers.paginate as paginate
import altair.app.ticketing.core.api as core_api
from altair.app.ticketing.payments.plugins import (
    SEJ_PAYMENT_PLUGIN_ID, 
    SEJ_DELIVERY_PLUGIN_ID,
    )
from ..core import api as c_api

logger = logging.getLogger(__name__)

class OrderReviewResource(object):
    def __init__(self, request):
        self.request = request
        self.session = get_db_session(request, name="slave")

    @reify
    def organization_id(self):
        organization = core_api.get_organization(self.request)
        return organization.id if organization else None

    @reify
    def membership(self):
        return self.session.query(Membership) \
            .filter_by(
                deleted_at=None,
                organization_id=self.organization_id
                ) \
            .first()

    @property
    def membership_name(self):
        return self.membership.name

    @property
    def order_no(self):
        return self.request.params.get('order_no')

    def authenticated_user(self):
        """現在認証中のユーザ"""
        from altair.rakuten_auth.api import authenticated_user
        user = authenticated_user(self.request)
        return user or { 'is_guest': True }

    def get_order(self):
        order_no = self.order_no
        order = self.session.query(Order).filter_by(
            organization_id=self.organization_id,
            order_no=order_no
        ).first()
        logger.info("organization_id=%s, order_no=%s, order=%s" % (self.organization_id, order_no, order))
        sej_order = None
        if order:
            payment_method_plugin_id = order.payment_delivery_pair.payment_method.payment_plugin.id
            delivery_method_plugin_id = order.payment_delivery_pair.delivery_method.delivery_plugin.id
            if payment_method_plugin_id == SEJ_PAYMENT_PLUGIN_ID or \
               delivery_method_plugin_id == SEJ_DELIVERY_PLUGIN_ID:
                sej_order = get_sej_order(order_no, self.session)

        return order, sej_order

    def get_membership(self):
        org = c_api.get_organization(self.request)
        membership = Membership.query.filter(Membership.organization_id==org.id).first()
        return membership

    def get_shipping_address(self, user):
        shipping_address = ShippingAddress.query.filter(
            ShippingAddress.user_id==user.id
        ).first()
        return shipping_address

    def get_orders(self, user, page, per):
        orders = Order.query.filter(
            Order.user_id==user.id
        ).order_by(Order.updated_at.desc())
        orders = paginate.Page(orders.all(), page, per, url=paginate.PageURL_WebOb(self.request))
        return orders

    def get_lots_entries(self, user, page, per):
        entries = LotEntry.query.filter(
            LotEntry.user_id==user.id
        ).order_by(LotEntry.updated_at.desc())
        entries = paginate.Page(entries.all(), page, per, url=paginate.PageURL_WebOb(self.request))
        return entries
