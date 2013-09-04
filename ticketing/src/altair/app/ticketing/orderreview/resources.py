# -*- coding:utf-8 -*-

from datetime import datetime
from dateutil import parser
from pyramid.decorator import reify
from altair.app.ticketing.core.models import DBSession, Order
from altair.app.ticketing.users.models import User, UserCredential, Membership, UserProfile
from altair.app.ticketing.sej.models import SejOrder
import altair.app.ticketing.core.api as core_api

from sqlalchemy.orm.exc import NoResultFound
import logging

logger = logging.getLogger(__name__)

def get_membership_from_request(request):
    organization = core_api.get_organization(request)
    return Membership.query.filter_by(deleted_at=None, organization=organization).first()

def get_credential(cart_id, membership_name):
    return UserCredential.query.filter(
        UserCredential.auth_identifier==str(cart_id),
        ).filter(
        UserCredential.membership_id==Membership.id
        ).filter(
            Membership.name==membership_name
        ).first()

def create_credential(cart_id, membership_name):
    membership = Membership.query.filter(Membership.name==membership_name).first()
    user = User()
    credential = UserCredential(user=user, auth_identifier=str(cart_id), membership=membership)
    return credential

class OrderReviewResource(object):
    def __init__(self, request):
        self.request = request

    @property
    def organization_id(self):
        return self.membership.organization_id

    @reify
    def membership_name(self):
        return get_membership_from_request(self.request).name

    @reify
    def membership(self):
        return Membership.query.filter(Membership.name==self.membership_name).first()

    def get_or_create_user(self):
        from altair.app.ticketing.cart import api
        cart = api.get_cart(self.request)
        credential = get_credential(cart.id, self.membership_name)
        if credential:
            user = credential.user
            return user
        ## 本当にこれつくって良いの？
        credential = create_credential(cart.id, self.membership_name)
        DBSession.add(credential)
        return credential.user

    def get_order(self):
        order_no = self.request.params.get('order_no')
        order = Order.filter_by(
            organization_id=self.organization_id,
            order_no=order_no
        ).first()
        logger.info("organization_id=%s, order_no=%s, order=%s" % (self.organization_id, order_no, order))
        sej_order = None
        if order:
            payment_method_plugin_id = order.payment_delivery_pair.payment_method.payment_plugin.id
            delivery_method_plugin_id = order.payment_delivery_pair.delivery_method.delivery_plugin.id
            if payment_method_plugin_id == 3 or delivery_method_plugin_id == 2:
                sej_order = SejOrder.filter(SejOrder.order_id == order_no).first()

        return order, sej_order

