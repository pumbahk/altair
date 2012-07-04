# -*- coding: utf-8 -*-

import json
import urllib2
import logging
import contextlib
from zope.deprecation import deprecate

logger = logging.getLogger(__file__)
from pyramid.interfaces import IRoutesMapper
from ..api.impl import get_communication_api
from ..api.impl import CMSCommunicationApi
from .interfaces import IPaymentMethodManager
from .interfaces import IPaymentPlugin, IDeliveryPlugin, IPaymentDeliveryPlugin
from .models import Cart, PaymentMethodManager, DBSession
from ..users.models import User, UserCredential, MemberShip
    
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
    return 'ticketing.cart_id' in request.session or hasattr(request, '_cart')

def _maybe_encoded(s, encoding='utf-8'):
    if isinstance(s, unicode):
        return s
    return s.decode(encoding)

def get_item_name(request, performance):
    base_item_name = request.registry.settings['cart.item_name']
    return _maybe_encoded(base_item_name) + " " + str(performance.id)

def get_nickname(request):
    from .rakuten_auth.api import authenticated_user
    user = authenticated_user(request)
    return user['nickname']

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
    # TODO: 楽天OpenID以外にも対応できるフレームワークを...
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
