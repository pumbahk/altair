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
from ..core.models import FeeTypeEnum, SalesSegment
import logging
from .plugins.resources import OrderDelivery, CartDelivery, OrderPayment, CartPayment
logger = logging.getLogger(__name__)

def performance_date(performance):
    s = performance.start_on
    return u'{0.month}月{0.day}日 {0.hour:02}:{0.minute:02}'.format(s)
def get_nickname(request):
    from .rakuten_auth.api import authenticated_user
    user = authenticated_user(request)
    return user['nickname']

def render_delivery_confirm_viewlet(request, cart):
    logger.debug("*" * 80)
    plugin_id = cart.payment_delivery_pair.delivery_method.delivery_plugin_id
    logger.debug("plugin_id:%d" % plugin_id)

    cart = CartDelivery(cart)
    response = render_view_to_response(cart, request, name="delivery-%d" % plugin_id, secure=False)
    if response is None:
        raise ValueError
    return Markup(response.text)

def error_list(request, form, name):
    errors = form[name].errors
    if not errors:
        return ""
    
    html = '<ul class="error-list">'
    html += "".join(['<li>%s</li>' % e for e in errors])
    html += '</ul>'
    return Markup(html)

def render_payment_confirm_viewlet(request, cart):
    logger.debug("*" * 80)
    plugin_id = cart.payment_delivery_pair.payment_method.payment_plugin_id
    logger.debug("plugin_id:%d" % plugin_id)

    cart = CartPayment(cart)
    response = render_view_to_response(cart, request, name="payment-%d" % plugin_id, secure=False)
    if response is None:
        raise ValueError
    return Markup(response.text)

def render_delivery_finished_viewlet(request, order):
    logger.debug("*" * 80)
    plugin_id = order.payment_delivery_pair.delivery_method.delivery_plugin_id
    logger.debug("plugin_id:%d" % plugin_id)

    order = OrderDelivery(order)
    response = render_view_to_response(order, request, name="delivery-%d" % plugin_id, secure=False)
    if response is None:
        raise ValueError
    return Markup(response.text)

def render_payment_finished_viewlet(request, order):
    logger.debug("*" * 80)
    plugin_id = order.payment_delivery_pair.payment_method.payment_plugin_id
    logger.debug("plugin_id:%d" % plugin_id)

    order = OrderPayment(order)
    response = render_view_to_response(order, request, name="payment-%d" % plugin_id, secure=False)
    if response is None:
        raise ValueError
    return Markup(response.text)

def fee_type(type_enum):
    if type_enum == int(FeeTypeEnum.Once.v[0]):
        return u"1回ごと"
    if type_enum == int(FeeTypeEnum.PerUnit.v[0]):
        return u"1枚ごと"

def format_number(num, thousands=","):
    return _format_number(int(num), thousands)

def format_currency(num, thousands=","):
    return u"￥" + format_number(num, thousands)

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

def get_salessegment(event_id, salessegment_id, selected_date):
    ## 販売条件は必ず一つに絞られるはず
    if salessegment_id:
        return SalesSegment.filter_by(id=salessegment_id).first()
    elif selected_date:
        qs = DBSession.query(SalesSegment).filter(SalesSegment.event_id==event_id)
        qs = qs.filter(SalesSegment.start_at<=selected_date)
        qs = qs.filter(SalesSegment.end_at >= selected_date)
        return qs.first()
    else:
        return None

def products_filter_by_salessegment(products, sales_segment):
    if sales_segment is None:
        logger.debug("debug: products_filter -- salessegment is none")
    if sales_segment:
        return products.filter_by(sales_segment=sales_segment)
    return products

