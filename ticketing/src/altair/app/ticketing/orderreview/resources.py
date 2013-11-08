# -*- coding:utf-8 -*-

import logging
from datetime import datetime
from dateutil import parser
from pyramid.decorator import reify
from sqlalchemy.orm.exc import NoResultFound
from altair.sqlahelper import get_db_session

from altair.app.ticketing.core.models import DBSession, Order
from altair.app.ticketing.users.models import User, UserCredential, Membership, UserProfile
from altair.app.ticketing.sej.api import get_sej_order
import altair.app.ticketing.core.api as core_api
from altair.app.ticketing.payments.plugins import (
    SEJ_PAYMENT_PLUGIN_ID, 
    SEJ_DELIVERY_PLUGIN_ID,
    )

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

