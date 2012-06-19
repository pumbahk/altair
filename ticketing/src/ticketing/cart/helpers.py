# -*- coding:utf-8 -*-

"""
TODO: cart取得はリソースの役目
"""

from webhelpers.html.tags import *
from webhelpers.number import format_number as _format_number
from .models import Cart, PaymentMethodManager, DBSession
from .interfaces import IPaymentMethodManager
from ..users.models import User, UserCredential, MemberShip
from pyramid.view import render_view_to_response
from markupsafe import Markup
from zope.interface import implementer


def format_number(num, thousands=","):
    return _format_number(int(num), thousands)

def format_currency(num, thousands=","):
    return "￥" + format_number(num, thousands)

def set_cart(request, cart):
    request.session['ticketing.cart_id'] = cart.id
    request._cart = cart

def get_cart(request):
    if hasattr(request, '_cart'):
        return request._cart

    cart_id = request.session.get('ticketing.cart_id')
    if cart_id is None:
        return None

    request._cart = Cart.query.filter(Cart.id==cart_id).first()
    return request._cart

def remove_cart(request):
    if hasattr(request, '_cart'):
        delattr(request, '_cart')
    del request.session['ticketing.cart_id']

def has_cart(request):
    return 'ticketing.cart_id' in request.session or hasattr(request, '_cart')

def get_item_name(request, performance):
    base_item_name = request.registry.settings['cart.item_name']
    return maybe_encoded(base_item_name) + " " + str(performance.id)

def maybe_encoded(s, encoding='utf-8'):
    if isinstance(s, unicode):
        return s
    return s.decode(encoding)

def get_payment_method_manager(request=None, registry=None):
    if request is not None:
        registry = request.registry

    payment_method_manager = registry.utilities.lookup([], IPaymentMethodManager, "")
    if payment_method_manager is None:
        payment_method_manager = PaymentMethodManager()
        registry.utilities.register([], IPaymentMethodManager, "", payment_method_manager)
    return payment_method_manager

def get_payment_method_url(request, payment_method_id, route_args={}):
    payment_method_manager = get_payment_method_manager(request)
    route_name = payment_method_manager.get_route_name(str(payment_method_id))
    if route_name:
        return request.route_url(route_name, **route_args)
    else:
        return ""

def get_or_create_user(request, clamed_id):
    credential = UserCredential.query.filter(
        UserCredential.auth_identifier==clamed_id
    ).filter(
        UserCredential.membership_id==MemberShip.id
    ).filter(
        MemberShip.name=='rakuten'
    ).first()
    if credential:
        return credential.user
    
    user = User()
    membership = MemberShip.query.filter(MemberShip.name=='rakuten').first()
    if membership is None:
        membership = MemberShip(name='rakuten')
        DBSession.add(membership)
    credential = UserCredential(user=user, auth_identifier=clamed_id, membership=membership)
    DBSession.add(user)
    return user

