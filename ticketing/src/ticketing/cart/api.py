# -*- coding: utf-8 -*-

from datetime import datetime
import json
import urllib2
import logging
import contextlib

from zope.deprecation import deprecate
from sqlalchemy.sql.expression import or_, and_

from pyramid.interfaces import IRoutesMapper, IRequest
from pyramid.security import effective_principals, forget
from pyramid.httpexceptions import HTTPNotFound

from ticketing.api.impl import get_communication_api
from ticketing.api.impl import CMSCommunicationApi
from altair.mobile.interfaces import IMobileRequest
from ticketing.core import models as c_models
from ticketing.core import api as c_api
from ticketing.users.models import User, UserCredential, Membership, MemberGroup, MemberGroup_SalesSegment

from .interfaces import IPaymentMethodManager
from .interfaces import IStocker, IReserving, ICartFactory
from .interfaces import IPerformanceSelector

from .models import Cart, PaymentMethodManager, DBSession
from .exceptions import OutTermSalesException, NoSalesSegment, NoCartError

logger = logging.getLogger(__name__)

def is_multicheckout_payment(cart):
    if cart is None:
        return False
    if cart.payment_delivery_pair is None:
        return False
    if cart.payment_delivery_pair.payment_method is None:
        return False
    return cart.payment_delivery_pair.payment_method.payment_plugin_id == 1

def is_checkout_payment(cart):
    if cart is None:
        return False
    if cart.payment_delivery_pair is None:
        return False
    if cart.payment_delivery_pair.payment_method is None:
        return False
    return cart.payment_delivery_pair.payment_method.payment_plugin_id == 2

# こいつは users.apiあたりに移動すべきか
def is_login_required(request, event):
    if event.organization.setting.auth_type == "rakuten":
        return True

    """ 指定イベントがログイン画面を必要とするか """
    # 終了分もあわせて、このeventからひもづく sales_segment -> membergroupに1つでもguestがあれば True 
    q = MemberGroup.query.filter(
        MemberGroup.is_guest==False
    ).filter(
        MemberGroup.id==MemberGroup_SalesSegment.c.membergroup_id
    ).filter(
        c_models.SalesSegmentGroup.id==MemberGroup_SalesSegment.c.sales_segment_group_id
    ).filter(
        c_models.SalesSegmentGroup.event_id==event.id
    )
    return bool(q.count())

def check_sales_segment_term(request):
    now = get_now_from_request(request)
    cart = get_cart(request)
    if cart is not None:
        sales_segment = cart.sales_segment
    else:
        sales_segment = request.context.sales_segment
    if not sales_segment:
        raise NoSalesSegment

    if not sales_segment.in_term(now):
        data = request.context.event.get_next_and_last_sales_segment_period(
            now=now, user=request.context.authenticated_user())
        if any(data):
            for datum in data:
                if datum is not None:
                    datum['event'] = datum['performance'].event
            raise OutTermSalesException(*data)
        else:
            raise HTTPNotFound()

def get_event(request):
    event_id = request.matchdict.get('event_id')
    if not event_id:
        return None
    return c_models.Event.query.filter(c_models.Event.id==event_id).first()

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
    request.session.persist()
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
    if request.session.get("ticketing.cart_id"):
        del request.session['ticketing.cart_id']

@deprecate
def has_cart(request):
    try:
        get_cart_safe(request)
        return True
    except NoCartError:
        return False

def get_now_from_request(request):
    if hasattr(request.context, "now"):
        return request.context.now
    else:
        return datetime.now() # XXX

def get_cart_safe(request):
    now = get_now_from_request(request) # XXX
    minutes = max(int(request.registry.settings['altair_cart.expire_time']) - 1, 0)
    cart = get_cart(request)
    if cart is None:
        raise NoCartError('Cart is not associated to the request')
    expired = cart.is_expired(minutes, now) or cart.finished_at
    if expired:
        remove_cart(request)
        raise NoCartError('Cart is expired')
    return cart

def recover_cart(request):
    cart = get_cart_safe(request)
    new_cart = Cart.create_from(cart)
    DBSession.flush()
    set_cart(request, new_cart)
    return cart

def _maybe_encoded(s, encoding='utf-8'):
    if isinstance(s, unicode):
        return s
    return s.decode(encoding)

def get_item_name(request, cart_name):
    organization = c_api.get_organization(request)
    base_item_name = organization.setting.cart_item_name
    return _maybe_encoded(base_item_name) + " " + str(cart_name)

def get_nickname(request, suffix=u'さん'):
    from altair.rakuten_auth.api import authenticated_user
    user = authenticated_user(request) or {}
    nickname = user.get('nickname', '')
    if not nickname:
        return ""
    return unicode(nickname, 'utf-8') + suffix

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

@deprecate
def get_salessegment(request, event_id, salessegment_id, selected_date):
    ## 販売条件は必ず一つに絞られるはず
    if salessegment_id:
        return c_models.SalesSegment.filter_by(id=salessegment_id).first()
    elif selected_date:
        qs = DBSession.query(c_models.SalesSegment).filter(c_models.SalesSegment.event_id==event_id)
        qs = qs.filter(c_models.SalesSegment.start_at<=selected_date)
        qs = qs.filter(c_models.SalesSegment.end_at >= selected_date)
        return qs.first()
    else:
        return None


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

def get_valid_sales_url(request, event):
    principals = effective_principals(request)
    logger.debug(principals)
    for sales_segment_group in event.sales_segment_groups:
        membergroups = sales_segment_group.membergroups
        for membergroup in membergroups:
            logger.debug("sales_segment:%s" % sales_segment_group.name)
            logger.debug("membergroup:%s" % membergroup.name)
            if "membergroup:%s" % membergroup.name in principals:
                return request.route_url('cart.index.sales', event_id=event.id, sales_segment_group_id=sales_segment_group.id)

def logout(request, response=None):
    headers = forget(request)
    if response is None:
        response = request.response
    response.headerlist.extend(headers)

class JSONEncoder(json.JSONEncoder):
    def __init__(self, datetime_format, *args, **kwargs):
        super(JSONEncoder, self).__init__(*args, **kwargs)
        self.datetime_format = datetime_format

    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime(self.datetime_format)
        return super(JSONEncoder, self).default(o)

def new_order_session(request, **kw):
    request.session['order'] = kw
    return request.session['order']

def update_order_session(request, **kw):
    request.session['order'].update(kw)
    return request.session['order']

def get_performance_selector(request, name):
    reg = request.registry
    performance_selector = reg.adapters.lookup([IRequest], IPerformanceSelector, name)(request)
    return performance_selector
