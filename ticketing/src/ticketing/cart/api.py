# -*- coding: utf-8 -*-

import json
import urllib2
import logging
import contextlib
from zope.deprecation import deprecate

logger = logging.getLogger(__name__)
from pyramid.interfaces import IRoutesMapper, IRequest
from pyramid.security import effective_principals
from ..api.impl import get_communication_api
from ..api.impl import CMSCommunicationApi
from .interfaces import IPaymentMethodManager
from .interfaces import IPaymentPlugin, IDeliveryPlugin, IPaymentDeliveryPlugin
from .interfaces import IMobileRequest, IStocker, IReserving, ICartFactory, ICompleteMail
from .models import Cart, PaymentMethodManager, DBSession, CartedProductItem, CartedProduct
from ..users.models import User, UserCredential, Membership
    
def is_mobile(request):
    return IMobileRequest.providedBy(request)

def get_event_info_from_cms(request, event_id):
    communication_api = get_communication_api(request, CMSCommunicationApi)
    path = "/api/event/%(event_id)s/info" % {"event_id": event_id}
    req = communication_api.create_connection(path)
    try:
        with contextlib.closing(urllib2.urlopen(req)) as res:
            try:
                data = res.read()
                return json.loads(data)
            except urllib2.HTTPError, e:
                logging.warn("*api* HTTPError: url=%s errorno %s" % (communication_api.get_url(path), e))
    except urllib2.URLError, e:
        fmt = "*api* URLError: url=%s response status %s"
        logging.warn(fmt % (communication_api.get_url(path), e))
    return {"event": []}

def get_route_pattern(registry, name):
    mapper = registry.getUtility(IRoutesMapper)
    return mapper.get_route(name).pattern

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
    minute = max(int(request.registry.settings['altair_cart.expire_time']) - 1, 0)
    cart = get_cart(request)
    if cart is None:
        return False
    return not cart.is_expired(minutes)

def _maybe_encoded(s, encoding='utf-8'):
    if isinstance(s, unicode):
        return s
    return s.decode(encoding)

def get_item_name(request, performance):
    base_item_name = request.registry.settings['cart.item_name']
    return _maybe_encoded(base_item_name) + " " + str(performance.id)

def get_nickname(request, suffix=u'さん'):
    from .rakuten_auth.api import authenticated_user
    user = authenticated_user(request)
    nickname = user.get('nickname', '')
    if not nickname:
        return ""
    return nickname + suffix

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

def get_or_create_user(request, auth_identifier, membership='rakuten'):
    # TODO: 楽天OpenID以外にも対応できるフレームワークを...
    credential = UserCredential.query.filter(
        UserCredential.auth_identifier==auth_identifier
    ).filter(
        UserCredential.membership_id==Membership.id
    ).filter(
        Membership.name==membership
    ).first()
    if credential:
        return credential.user
    
    user = User()
    membership = Membership.query.filter(Membership.name=='rakuten').first()
    if membership is None:
        membership = Membership(name='rakuten')
        DBSession.add(membership)
    credential = UserCredential(user=user, auth_identifier=auth_identifier, membership=membership)
    DBSession.add(user)
    return user


@deprecate
def get_salessegment(request, event_id, salessegment_id, selected_date):
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

def get_payment_plugin(request, plugin_id):
    logger.debug("get_payment_plugin: %s" % plugin_id)
    registry = request.registry
    return registry.utilities.lookup([], IPaymentPlugin, name="payment-%s" % plugin_id)

def get_delivery_plugin(request, plugin_id):
    registry = request.registry
    return registry.utilities.lookup([], IDeliveryPlugin, name="delivery-%s" % plugin_id)

def get_payment_delivery_plugin(request, payment_plugin_id, delivery_plugin_id):
    registry = request.registry
    return registry.utilities.lookup([], IPaymentDeliveryPlugin, 
        "payment-%s:delivery-%s" % (payment_plugin_id, delivery_plugin_id))

def get_stocker(request):
    reg = request.registry
    stocker_cls = reg.adapters.lookup([IRequest], IStocker, "")
    return stocker_cls(request)

def get_reserving(request):
    reg = request.registry
    stocker_cls = reg.adapters.lookup([IRequest], IReserving, "")
    return stocker_cls(request)

def get_cart_factory(request):
    reg = request.registry
    stocker_cls = reg.adapters.lookup([IRequest], ICartFactory, "")
    return stocker_cls(request)

def get_complete_mail(request):
    cls = request.registry.adapters.lookup([IRequest], ICompleteMail, "")
    return cls(request)

def order_products(request, performance_id, product_requires, selected_seats=[]):
    stocker = get_stocker(request)
    reserving = get_reserving(request)
    cart_factory = get_cart_factory(request)

    stockstatuses = stocker.take_stock(performance_id, product_requires)

    logger.debug("stock %s" % stockstatuses)
    seats = []
    if selected_seats:
        logger.debug("seat selected by user")
        seats += reserving.reserve_selected_seats(stockstatuses, performance_id, selected_seats)
    else:
        logger.debug("selecting seat by system")
        for stockstatus, quantity in stockstatuses:
            if is_quantity_only(stockstatus.stock):
                logger.debug('stock %d quantity only' % stockstatus.stock.id)
                continue
            seats += reserving.reserve_seats(stockstatus.stock_id, quantity)        

    logger.debug(seats)
    cart = cart_factory.create_cart(performance_id, seats, product_requires)
    return cart

def is_quantity_only(stock):
    return stock.stock_type.quantity_only


def get_system_fee(request):
    return 380

def get_stock_holder(request, event_id):
    stocker = get_stocker(request)
    return stocker.get_stock_holder(event_id)

def get_valid_sales_url(request, event):
    principals = effective_principals(request)
    logger.debug(principals)
    for salessegment in event.sales_segments:
        membergroups = salessegment.membergroups
        for membergroup in membergroups:
            logger.debug("sales_segment:%s" % salessegment.name)
            logger.debug("membergroup:%s" % membergroup.name)
            if "membergroup:%s" % membergroup.name in principals:
                return request.route_url('cart.index.sales', event_id=event.id, sales_segment_id=salessegment.id)

