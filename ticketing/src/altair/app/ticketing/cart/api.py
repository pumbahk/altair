# -*- coding: utf-8 -*-

from datetime import datetime
import json
import urllib2
import logging
import contextlib
import re

from zope.deprecation import deprecate
from sqlalchemy.sql.expression import or_, and_
from sqlalchemy.orm.session import make_transient
from sqlalchemy.orm.attributes import instance_state
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from pyramid.interfaces import IRoutesMapper, IRequest
from pyramid.security import effective_principals, forget, authenticated_userid
from pyramid.httpexceptions import HTTPNotFound

from altair.app.ticketing.api.impl import get_communication_api
from altair.app.ticketing.api.impl import CMSCommunicationApi
from altair.mobile.interfaces import IMobileRequest, ISmartphoneRequest
from altair.mobile.api import detect_from_ip_address
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.core import api as c_api
from altair.app.ticketing.users import models as u_models
from altair.app.ticketing.orders import models as order_models
from altair.app.ticketing.interfaces import ITemporaryStore
from altair.app.ticketing.security import get_extra_auth_info_from_principals
from altair.mq import get_publisher
from altair.sqlahelper import get_db_session

from .interfaces import IPaymentMethodManager
from .interfaces import IStocker, IReserving, ICartFactory
from .interfaces import IPerformanceSelector

from .models import Cart, PaymentMethodManager, DBSession
from .exceptions import NoCartError
from altair.preview.api import set_rendered_target

logger = logging.getLogger(__name__)

ENV_ORGANIZATION_ID_KEY = 'altair.app.ticketing.cart.organization_id'
ENV_ORGANIZATION_PATH_KEY = 'altair.app.ticketing.cart.organization_path'

def set_rendered_event(request, event):
    set_rendered_target(request, "event", event)


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

def is_mobile(request):
    return IMobileRequest.providedBy(request)

def is_smartphone(request):
    return ISmartphoneRequest.providedBy(request)

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
    request.session['altair.app.ticketing.cart_id'] = cart.id
    # pyramid.testing.DummySession には persist がない
    if hasattr(request.session, 'persist'):
        request.session.persist()

def get_cart(request, for_update=True):
    cart_id = request.session.get('altair.app.ticketing.cart_id')
    if cart_id is None:
        return None

    q = Cart.query.filter(Cart.id==cart_id)
    if for_update:
        q = q.with_lockmode('update')

    return q.first()

def remove_cart(request):
    if request.session.get("altair.app.ticketing.cart_id"):
        del request.session['altair.app.ticketing.cart_id']

def release_cart(request, cart, async=True):
    if async:
        try:
            get_publisher(request, 'cart').publish(
                body=json.dumps(dict(cart_id=cart.id)),
                routing_key='cart',
                properties=dict(content_type="application/json")
                )
        except Exception as e:
            import sys
            logger.warning("ignored exception", exc_info=sys.exc_info())
    else:
        cart.release()

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

def get_cart_safe(request, for_update=True):
    now = datetime.now() ##cartのexpireの計算はcart.created_atで行われるので。ここはdatetime.nowが正しい
    minutes = max(int(request.registry.settings['altair_cart.expire_time']) - 1, 0)
    cart = get_cart(request, for_update)
    if cart is None:
        raise NoCartError('Cart is not associated to the request')
    expired = cart.is_expired(minutes, now) or cart.finished_at
    if expired:
        raise NoCartError('Cart is expired')
    return cart

def recover_cart(request):
    cart = get_cart_safe(request, True)
    new_cart = Cart.create_from(request, cart)
    DBSession.flush()
    set_cart(request, new_cart)
    return cart

def _maybe_encoded(s, encoding='utf-8'):
    if isinstance(s, unicode):
        return s
    return s.decode(encoding)

def get_item_name(request, cart_name):
    organization = get_organization(request)
    base_item_name = organization.setting.cart_item_name
    return _maybe_encoded(base_item_name) + " " + str(cart_name)

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


def get_stocker(request, session=None):
    if session is None:
        from altair.app.ticketing.models import DBSession
        session = DBSession
    reg = request.registry
    stocker_cls = reg.adapters.lookup([IRequest], IStocker, "")
    return stocker_cls(request, session)

def get_reserving(request, session=None):
    if session is None:
        from altair.app.ticketing.models import DBSession
        session = DBSession
    reg = request.registry
    stocker_cls = reg.adapters.lookup([IRequest], IReserving, "")
    return stocker_cls(request, session)

def get_cart_factory(request):
    reg = request.registry
    stocker_cls = reg.adapters.lookup([IRequest], ICartFactory, "")
    return stocker_cls(request)

def order_products(request, sales_segment_id, product_requires, selected_seats=[], separate_seats=False):
    stocker = get_stocker(request)
    reserving = get_reserving(request)
    cart_factory = get_cart_factory(request)

    performance_id = c_models.SalesSegment.filter_by(id=sales_segment_id).one().performance_id

    logger.debug("sales_segment_id=%d, performance_id=%s" % (sales_segment_id, performance_id))

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
            seats += reserving.reserve_seats(stockstatus.stock_id, quantity, separate_seats=separate_seats)

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

def get_cart_user_identifiers(request):
    from altair.browserid import get_browserid

    retval = []

    auth_info = get_auth_info(request)
    # is_guest は None である場合があり、その場合は guest であるとみなす
    if auth_info['is_guest'] is not None and not auth_info['is_guest']:
        retval.append((auth_info['user_id'], 'strong'))

    # browserid is decent
    browserid = get_browserid(request)
    if browserid:
        retval.append((browserid, 'decent'))

    remote_addr = request.remote_addr
    if remote_addr:
        carrier = detect_from_ip_address(request.registry, remote_addr)
        logger.debug('carrier=%s' % carrier.name)
        if (not carrier.is_nonmobile) and IMobileRequest.providedBy(request):
            unique_opaque = request.mobile_ua.unique_opaque
            if unique_opaque is not None:
                # subscriber ID is decent, in my opinion
                retval.append((unique_opaque, 'decent'))
        else:
            # remote address is *weakest*
            retval.append((remote_addr, 'weak'))
    return retval

def is_point_input_organization(context, request):
    organization = get_organization(request)
    return organization.id == 24

def is_fc_auth_organization(context, request):
    organization = get_organization(request)
    return bool(organization.settings[0].auth_type == "fc_auth")

def enable_auto_input_form(user):
    from altair.app.ticketing.users.models import User
    if not isinstance(user, User):
        return False

    if user.member is None:
        # 楽天認証
        return True

    if user.member.membergroup.enable_auto_input_form:
        return True

    return False

def get_temporary_store(request):
    return request.registry.queryUtility(ITemporaryStore)

def get_order_for_read_by_order_no(request, order_no):
    orders = getattr(request, '_cached_readonly_orders', None)
    if orders is None:
        orders = request._cached_readonly_orders = {}
    order = orders.get(order_no)
    if order is not None:
        return order
    order = get_db_session(request, name="slave") \
        .query(order_models.Order) \
        .filter_by(order_no=order_no) \
        .first()
    orders[order_no] = order
    return order

def get_organization(request):
    override_organization_id = request.environ.get(ENV_ORGANIZATION_ID_KEY)

    if hasattr(request, 'organization'):
        assert instance_state(request.organization).session_id is None
        if override_organization_id is None or request.organization.id == override_organization_id:
            return request.organization

    session = get_db_session(request, 'slave')
    try:
        if override_organization_id is not None:
            organization = session.query(c_models.Organization) \
                .options(joinedload(c_models.Organization.settings)) \
                .filter(c_models.Organization.id == override_organization_id) \
                .one()
        else:
            organization = session.query(c_models.Organization) \
                .options(joinedload(c_models.Organization.settings)) \
                .join(c_models.Organization.hosts) \
                .filter(c_models.Host.host_name == unicode(request.host)) \
                .one()
    except NoResultFound as e:
        raise Exception("Host that named %s is not Found" % request.host)
    make_transient(organization)
    if override_organization_id is None:
        request.organization = organization
        request.environ[ENV_ORGANIZATION_ID_KEY] = request.organization.id
    return organization

def get_auth_info(request):
    retval = {}
    user_id = authenticated_userid(request)
    principals = effective_principals(request)
    if principals:
        extra = get_extra_auth_info_from_principals(principals)
        retval.update(extra)
        retval['user_id'] = user_id
        if extra['auth_type'] == 'rakuten':
            retval['claimed_id'] = user_id
        elif extra['auth_type']:
            retval['username'] = user_id
        else:
            # auth_type が無いときは guest と見なす
            retval['is_guest'] = True
    else:
        retval['is_guest'] = True
        retval['user_id'] = None
    retval['organization_id'] = get_organization(request).id
    return retval

def get_auth_identifier_membership(info):
    if 'claimed_id' in info:
        auth_identifier = info['claimed_id']
        membership_name = 'rakuten'
    elif 'username' in info:
        auth_identifier = info['username']
        membership_name = info['membership']
    elif info.get('is_guest', False):
        auth_identifier = None
        membership_name = None
    else:
        raise ValueError('claimed_id, username not in %s' % info)
    return dict(
        organization_id=info['organization_id'],
        auth_identifier=auth_identifier,
        membership_name=membership_name
        )

def lookup_user_credential(d):
    q = u_models.UserCredential.query \
        .filter(u_models.UserCredential.auth_identifier==d['auth_identifier']) \
        .filter(u_models.UserCredential.membership_id==u_models.Membership.id) \
        .filter(u_models.Membership.name==d['membership_name'])
    if d['membership_name'] != 'rakuten':
        q = q.filter(u_models.Membership.organization_id == d['organization_id'])
    credential = q.first()
    if credential:
        return credential.user
    else:
        return None

def get_user(info):
    d = get_auth_identifier_membership(info)
    return lookup_user_credential(d)

def get_or_create_user(info):
    d = get_auth_identifier_membership(info)
    user = lookup_user_credential(d)
    if user is not None:
        return user

    if info.get('is_guest', False):
        # ゲストのときはユーザを作らない
        return None

    logger.info('creating user account for %r %r' % (d, info))

    user = u_models.User()
    membership = u_models.Membership.query.filter(
        u_models.Membership.organization_id == d['organization_id'],
        u_models.Membership.name == d['membership_name']) \
        .order_by(u_models.Membership.id.desc()) \
        .first()
    # [暫定] 楽天OpenID認証の場合は、oragnization_id の条件を外したものでも調べる
    # TODO: あとでちゃんとデータ移行する
    if membership is None and info['auth_type'] == 'rakuten':
        membership = u_models.Membership.query.filter(
            u_models.Membership.name == d['membership_name']) \
            .order_by(u_models.Membership.id.desc()) \
            .first()

    if membership is None:
        logger.error("could not found membership %s" % d['membership_name'])
        return None

    credential = u_models.UserCredential(
        user=user,
        auth_identifier=d['auth_identifier'],
        membership=membership
        )
    DBSession.add(credential)
    DBSession.add(user)
    return user

def get_or_create_user_from_point_no(point):
    if not point:
        return None

    credential = u_models.UserCredential.query.filter(
        u_models.UserCredential.auth_identifier==point
    ).filter(
        u_models.UserCredential.membership_id==u_models.Membership.id
    ).filter(
        u_models.Membership.name=='rakuten'
    ).first()
    if credential:
        return credential.user

    user = u_models.User()
    membership = u_models.Membership.query.filter(u_models.Membership.name=='rakuten').first()
    if membership is None:
        membership = u_models.Membership(name='rakuten')
        DBSession.add(membership)
    credential = u_models.UserCredential(user=user, auth_identifier=point, membership=membership)
    DBSession.add(user)

    credential = u_models.UserCredential.query.filter(
        u_models.UserCredential.auth_identifier==point
    ).first()
    return credential.user

def create_user_point_account_from_point_no(user_id, type, account_number):
    assert account_number is not None and account_number != ""

    if int(type) == int(u_models.UserPointAccountTypeEnum.Rakuten.v) and \
       not re.match(r'^\d{4}-\d{4}-\d{4}-\d{4}$', account_number):
        raise ValueError('invalid account number format; %s' % account_number)

    acc = u_models.UserPointAccount.query.filter(
        u_models.UserPointAccount.user_id==user_id
    ).first()

    if not acc:
        acc = u_models.UserPointAccount()

    acc.user_id = user_id
    acc.account_number = account_number
    acc.type = int(type)
    acc.status = u_models.UserPointAccountStatusEnum.Valid.v
    DBSession.add(acc)
    return acc

def get_user_point_account(user_id):
    acc = u_models.UserPointAccount.query.filter(
        u_models.UserPointAccount.user_id==user_id
    ).first()
    return acc

def get_or_create_user_profile(user, data):
    profile = None
    if user.user_profile:
        profile = user.user_profile

    if not profile:
        profile = u_models.UserProfile()

    profile.first_name=data['first_name'],
    profile.last_name=data['last_name'],
    profile.first_name_kana=data['first_name_kana'],
    profile.last_name_kana=data['last_name_kana'],
    profile.zip=data['zip'],
    profile.prefecture=data['prefecture'],
    profile.city=data['city'],
    profile.address_1=data['address_1'],
    profile.address_2=data['address_2'],
    profile.email_1=data['email_1'],
    profile.tel_1=data['tel_1'],

    user.user_profile = profile
    DBSession.add(user)
    return user.user_profile
