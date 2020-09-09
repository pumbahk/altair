# -*- coding: utf-8 -*-

from datetime import datetime, date, time
from time import time as calc_time
import json
import urllib2
import logging
import contextlib
import re
import sys

from zope.deprecation import deprecate
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.exc import NO_STATE

from altair.app.ticketing.orders.models import ExternalSerialCodeOrder, ExternalSerialCode

try:
    from sqlalchemy.orm.utils import object_state
except ImportError:
    from sqlalchemy.orm.attributes import instance_state as object_state

from pyramid.interfaces import IRoutesMapper, IRequest
from pyramid.security import effective_principals, forget, authenticated_userid
from pyramid.httpexceptions import HTTPNotFound

from altair.app.ticketing.api.impl import get_communication_api
from altair.app.ticketing.api.impl import CMSCommunicationApi, SiriusCommunicationApi
from altair.mobile.interfaces import IMobileRequest, ISmartphoneRequest
from altair.mobile.api import detect_from_ip_address, is_mobile_request
from altair.app.ticketing.authentication.plugins.externalmember import EXTERNALMEMBER_AUTH_IDENTIFIER_NAME, \
    EXTERNALMEMBER_EMAIL_ADDRESS_POLICY_NAME
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.core import api as c_api
from altair.app.ticketing.users import models as u_models
from altair.app.ticketing.orders import models as order_models
from altair.app.ticketing.discount_code import util as dc_util
from altair.app.ticketing.interfaces import ITemporaryStore
from altair.app.ticketing.payments import api as payments_api
from altair.app.ticketing.payments.payment import Payment
from altair.app.ticketing.payments.exceptions import PointSecureApprovalFailureError
from altair.app.ticketing.payments.exceptions import PaymentDeliveryMethodPairNotFound, OrderLikeValidationFailure
from altair.mq import get_publisher
from altair.sqlahelper import get_db_session
from . import SPA_COOKIE

from .interfaces import (
    IPaymentMethodManager,
    IStocker,
    IReserving,
    ICartFactory,
    IPerformanceSelector,
    )
from .models import Cart, PaymentMethodManager, DBSession, CartSetting
from .exceptions import NoCartError, PaymentError
from .events import notify_order_completed
from altair.preview.api import set_rendered_target

from altair.convert_openid.exceptions import ConverterAPIError, EasyIDNotFoundError
from altair.point.exceptions import PointAPIError

import altair.convert_openid.api as openid_converter_client
import altair.point.api as point_client
import altair.app.ticketing.point.api as point_api

logger = logging.getLogger(__name__)

def set_rendered_event(request, event):
    set_rendered_target(request, "event", event)

def is_mobile(request):
    return IMobileRequest.providedBy(request)

def is_smartphone(request):
    return ISmartphoneRequest.providedBy(request)


def get_event_info_from_cms(request, event_id):
    if request.organization.setting.migrate_to_sirius:
        # Siriusからイベント情報を取得する。Siriusが安定するまではSirius APIが失敗したら旧CMS APIを実行する
        # Siriusが安定したらSiriusのみに通信するよう修正すること。
        # 本処理ブロックを削除し、communication_apiをSirius向けに生成すれば良い
        sirius_communication_api = get_communication_api(request, SiriusCommunicationApi)
        sirius_api_path = '/api/event/{}/info'.format(event_id)
        sirius_req = sirius_communication_api.create_connection(sirius_api_path)
        try:
            with contextlib.closing(urllib2.urlopen(sirius_req)) as sirius_res:
                data = sirius_res.read()
                return json.loads(data)
        except Exception as e:  # Sirius APIが失敗した場合、以降の旧CMS APIのレスポンスを採用
            logging.error('*sirius api* failed: url=%s, reason=%s', sirius_communication_api.get_url(sirius_api_path),
                          e, exc_info=1)

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


def get_keywords_from_cms(request, performance_id):
    if request.organization.setting.migrate_to_sirius:
        # Siriusからお気に入りワードを取得する。Siriusが安定するまではSirius APIが失敗したら旧CMS APIを実行する
        # Siriusが安定したらSiriusのみに通信するよう修正すること。
        # 本処理ブロックを削除し、communication_apiをSirius向けに生成すれば良い
        sirius_communication_api = get_communication_api(request, SiriusCommunicationApi)
        sirius_api_path = '/api/word/?backend_performance_id={}'.format(performance_id)
        sirius_req = sirius_communication_api.create_connection(sirius_api_path)
        try:
            with contextlib.closing(urllib2.urlopen(sirius_req)) as sirius_res:
                data = sirius_res.read()
                return json.loads(data)
        except Exception as e:  # Sirius APIが失敗した場合、以降の旧CMS APIのレスポンスを採用
            logging.error('*sirius api* failed: url=%s, reason=%s', sirius_communication_api.get_url(sirius_api_path),
                          e, exc_info=1)

    communication_api = get_communication_api(request, CMSCommunicationApi)
    path = "/api/word/?backend_performance_id=%(performance_id)s" % {"performance_id": performance_id}
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
    return {"words": []}


def get_route_pattern(registry, name):
    mapper = registry.getUtility(IRoutesMapper)
    pattern = mapper.get_route(name).pattern
    if not pattern.startswith('/'):
        pattern = '/' + pattern
    return pattern

def set_cart(request, cart):
    request.session['altair.app.ticketing.cart_id'] = cart.id
    # pyramid.testing.DummySession には persist がない
    if hasattr(request.session, 'persist'):
        request.session.persist()

def get_cart(request, for_update=True):
    cart_id = request.session.get('altair.app.ticketing.cart_id')
    if cart_id is None:
        return None

    if for_update:
        cart = request.environ.get('altair.app.ticketing.cart')
        if cart is not None:
            try:
                state = object_state(cart)
            except NO_STATE:
                state = None
            if state and state.session_id is not None:
                return cart
        cart = Cart.query.filter(Cart.id==cart_id).with_lockmode('update').first()
        request.environ['altair.app.ticketing.cart'] = cart
    else:
        cart = request.environ.get('altair.app.ticketing.read_only_cart')
        if cart is not None:
            try:
                state = object_state(cart)
            except NO_STATE:
                state = None
            if state and state.session_id is not None:
                return cart
        cart = request.environ.get('altair.app.ticketing.cart')
        if cart is not None:
            try:
                state = object_state(cart)
            except NO_STATE:
                state = None
            if state and state.session_id is not None:
                return cart
        cart = Cart.query.filter(Cart.id==cart_id).first()
        request.environ['altair.app.ticketing.read_only_cart'] = cart
    return cart

def get_cart_by_order_no(request, order_no, for_update=True):
    q = Cart.query.filter(Cart.order_no == order_no)
    if for_update:
        q = q.with_lockmode('update')

    return q.first()

def disassociate_cart_from_session(request):
    try:
        del request.session['altair.app.ticketing.cart_id']
    except KeyError:
        pass

def remove_cart(request, release=True, async=True):
    cart = get_cart(request, for_update=(not async))
    disassociate_cart_from_session(request)
    if cart is not None and cart.finished_at is None:
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

@deprecate("deprecated")
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

def get_cart_expire_time(request_or_registry):
    if hasattr(request_or_registry, 'registry'):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    expire_time_str = registry.settings.get('altair.cart.expire_time')
    if expire_time_str is None:
        logger.warning("altair.cart.expire_time does not exist. using deprecated altair_cart.expire_time instead")
        expire_time_str = registry.settings.get('altair_cart.expire_time')
        if expire_time_str is None:
            logger.warning("neither altair.cart.expire_time nor altair_cart.expire_time exists")
    expire_time = None
    if expire_time_str is not None:
        expire_time = int(expire_time_str)
    return expire_time

def validate_cart(request, cart):
    """カートが利用可能かどうか調べる。利用可能であれば True を返す"""
    # カートが finished の状態になっているときは、カートはもう使うことができない
    if cart.finished_at:
        return False

    expire_time = get_cart_expire_time(request)

    # expire_time が指定されていないときは、カートの期限切れは発生しない
    if expire_time is not None:
        now = datetime.now() ##cartのexpireの計算はcart.created_atで行われるので。ここはdatetime.nowが正しい
        minutes = max(expire_time - 1, 0) # XXX:この -1 は一体?
        if cart.is_expired(minutes, now):
            return False

    return True

def get_cart_safe(request, for_update=True):
    cart = get_cart(request, for_update)
    if cart is None:
        raise NoCartError('Cart is not associated to the request')
    if not validate_cart(request, cart):
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
    organization = request.organization
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

@deprecate("deprecated")
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

def order_products(request, sales_segment, product_requires, selected_seats=[], separate_seats=False):
    stocker = get_stocker(request)
    reserving = get_reserving(request)
    cart_factory = get_cart_factory(request)

    performance_id = sales_segment.performance_id

    logger.info("[%s] sales_segment_id=%d, performance_id=%s" % (sys._getframe().f_code.co_name,
                                                                  sales_segment.id, performance_id))
    take_stock_start = calc_time()
    stockstatuses = stocker.take_stock(performance_id, product_requires)
    logger.info("[%s] stocker.take_stock finished in %g sec. performance_id=%s" % (sys._getframe().f_code.co_name,
                                                                                   (calc_time() - take_stock_start),
                                                                                   performance_id))
    seats = []
    selecting_seat_start = calc_time()
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

    logger.info("[%s] selecting seat finished in %g sec. performance_id=%s" % (sys._getframe().f_code.co_name,
                                                                               (calc_time() - selecting_seat_start),
                                                                               performance_id))
    cart = cart_factory.create_cart(sales_segment, seats, product_requires)
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
    try:
        headers = forget(request)
        if response is None:
            response = request.response
        response.headerlist.extend(headers)
    except:
        logger.info('failed to logout; will invalidate session to minimize the side effect', exc_info=True)
        request.session.invalidate()

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

    externalmember_user_id = \
        request.registry.settings.get('altair.ticketing.authentication.externalmember.username')

    auth_info = request.altair_auth_info
    # is_guest は None である場合があり、その場合は guest であるとみなす。
    # 外部会員番号取得キーワード認証は altair_auth_info.user_id (auth_identifier) に
    # 固定の設定値が入っており、ユーザーを特定する要素にできないのでスキップします。
    if auth_info['is_guest'] is not None and not auth_info['is_guest'] \
            and auth_info['user_id'] != externalmember_user_id:
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

def is_point_account_no_input_organization(context, request):
    organization = get_organization(request)
    code = organization.code
    return code == 'RE' or code == 'KT' or code == 'VK' or code == 'RL' or code == 'RT' or code == 'OD'

def is_point_account_no_input_required(context, request):
    if not is_point_account_no_input_organization(context, request):
        return False

    # cart
    if hasattr(context, "asid"):
        if not context.asid:
            return False
    # lot
    else:
        if not context.lot_asid:
            return False

    info = request.altair_auth_info
    membership = get_membership(info)

    _enable_point_input = True
    if membership is not None:
        _enable_point_input = membership.enable_point_input
    return _enable_point_input


def is_point_use_accepted(context):
    """
    カートにある情報が楽天ポイント利用可能条件を全て満たしているかどうかを判定する。
    ・楽天会員認証済、もしくは Oauth 認可 API を使った認証済である
    ・販売区分がポイント充当可能に設定されている
    ・楽天ポイントを使用することができる支払方法である
    ・easy_idを持っている
    ・easy_idが持っていなければ、open_idを持っている

    本処理実行時点でCartにPDMPが紐づいていない場合、複数タブやウィンドウを使った操作による異常な状態であるためエラーとする
    """
    if context.cart.payment_delivery_pair is None:
        logger.warn('The Cart(%s) has no payment_delivery_method_pair. That is mandatory.', context.cart.order_no)
        raise NoCartError()

    return (context.cart_setting.is_rakuten_auth_type() or context.cart_setting.is_oauth_auth_type()) and \
        context.sales_segment.is_point_allocation_enable() and \
        context.cart.payment_delivery_pair.is_payment_method_compatible_with_point_use() and \
        _is_authenticated_to_use_rakuten_point(context)


def _is_authenticated_to_use_rakuten_point(context):
    user_credential = None
    try:
        auth_info = context.authenticated_user()
        if auth_info is not None:
            # 楽天認証かextauthならUserCredentialが存在する想定
            user_credential = lookup_user_credential(auth_info)
    except KeyError:
        # auth_info(dict型)にUserCredentialを特定するデータがないときに発生(詳細はlookup_user_credentialを参照)
        logger.warn('The cart %s does not have enough credentials to get an UserCredential.', context.cart.order_no)
    finally:
        if user_credential is None:
            return False

    # easy_idがある(過去にポイント利用可能orgで楽天認証済)かopen_idがある(初めてポイント利用可能orgで楽天認証した)
    return user_credential.easy_id is not None or user_credential.has_rakuten_open_id


def is_fc_auth_organization(context, request):
    return context.cart_setting.auth_type == "fc_auth"

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
    if order is None:
        order = DBSession.query(order_models.Order) \
            .filter_by(order_no=order_no) \
            .first()
    orders[order_no] = order
    return order

@deprecate("use request.organization")
def get_organization(request):
    return request.organization

@deprecate("use request.altair_auth_info")
def get_auth_info(request):
    return request.altair_auth_info

def get_membership(d):
    membership_name = d.get('membership') if d is not None else None
    if membership_name is None:
        # XXX: membership の名前が与えられていないときは
        # primary key が一番若いものを使う
        # ここのロジックを fc_auth と同じくする必要がある
        q = u_models.Membership.query \
            .filter_by(organization_id=d['organization_id']) \
            .order_by(u_models.Membership.id)
    else:
        q = u_models.Membership.query \
            .filter(u_models.Membership.name==d['membership']) \
            .filter(u_models.Membership.organization_id == d['organization_id'])
    return q.first()

def get_member_group(request, info):
    membership_name = info.get('membership')
    member_group_name = info.get('membergroup')
    if membership_name is None or member_group_name is None:
        return None
    q = u_models.MemberGroup.query \
        .join(u_models.MemberGroup.membership) \
        .filter(u_models.MemberGroup.name == member_group_name) \
        .filter(
            u_models.Membership.name == membership_name,
            u_models.Membership.organization_id == request.organization.id
            )
    return q.one()


def lookup_user_credential(d):
    q = u_models.UserCredential.query \
        .filter(u_models.UserCredential.auth_identifier==d['auth_identifier']) \
        .filter(u_models.UserCredential.authz_identifier==d['authz_identifier']) \
        .filter(u_models.UserCredential.membership_id==u_models.Membership.id) \
        .filter(u_models.Membership.name==d['membership']) \
        .filter(u_models.Membership.organization_id == d['organization_id'])
    return q.first()

def get_user(info):
    if info.get('is_guest', False):
        return None

    user_credential = lookup_user_credential(info)
    return getattr(user_credential, 'user', None)

def get_or_create_user(info):
    if info.get('is_guest', False):
        # ゲストのときはユーザを作らない
        return None

    user_credential = lookup_user_credential(info)
    user = getattr(user_credential, 'user', None)
    if user is not None:
        return user

    logger.info('creating user account for %r' % info)

    user = u_models.User()
    membership = u_models.Membership.query.filter(
        u_models.Membership.organization_id == info['organization_id'],
        u_models.Membership.name == info['membership']) \
        .order_by(u_models.Membership.id.desc()) \
        .first()
    # [暫定] 楽天OpenID認証の場合は、organization_id の条件を外したものでも調べる
    # TODO: あとでちゃんとデータ移行する
    if membership is None and info['membership_source'] == 'rakuten':
        membership = u_models.Membership.query.filter(
            u_models.Membership.name == info['membership']) \
            .order_by(u_models.Membership.id.desc()) \
            .first()

    if membership is None:
        logger.error("could not find membership %s" % info['membership'])
        return None

    credential = u_models.UserCredential(
        user=user,
        auth_identifier=info['auth_identifier'],
        authz_identifier=info['authz_identifier'],
        membership=membership
        )
    DBSession.add(credential)
    DBSession.add(user)
    return user

def create_user_point_account_from_point_no(user_id, type, account_number):
    assert account_number is not None and account_number != ""

    if int(type) == int(u_models.UserPointAccountTypeEnum.Rakuten.v) and \
       not re.match(r'^\d{4}-\d{4}-\d{4}-\d{4}$', account_number):
        raise ValueError('invalid account number format; %s' % account_number)

    if user_id is not None:
        q = u_models.UserPointAccount.query \
            .filter(
                u_models.UserPointAccount.user_id == user_id,
                u_models.UserPointAccount.type == int(type),
                u_models.UserPointAccount.account_number == account_number
                )
        acc = q.first()
    else:
        acc = None

    if not acc:
        acc = u_models.UserPointAccount(
            user_id=user_id,
            type=int(type),
            account_number=account_number,
            status=u_models.UserPointAccountStatusEnum.Valid.v
            )
        DBSession.add(acc)
        DBSession.flush()

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


def get_easy_id(request, auth_info):
    """
    easy_id を取得する。
    UserCredential テーブルに easy_id が存在する場合はその値を返却し、
    存在しない場合は openid から変換する。
    """
    user_credential = lookup_user_credential(auth_info)
    easy_id = getattr(user_credential, 'easy_id', None)
    openid = getattr(user_credential, 'auth_identifier', None)
    if easy_id:
        return easy_id
    elif openid:
        # easyid が UserCredential に無いが、openid を持っている場合は easyid に変換する
        try:
            easy_id = openid_converter_client.convert_openid_to_easyid(request, openid)
            # openid から easyid に変換できた場合は次回から使い回せるように保存する。
            user_credential.easy_id = easy_id
        except EasyIDNotFoundError as e:
            # openid に対応する easyid が存在しなかった
            logger.error(e, exc_info=1)
        except ConverterAPIError as e:
            # openid を easyid に返却する API のコール失敗。stack trace は altair.convert_openid で出力されている
            logger.error(e.message)
        except Exception as e:
            logger.error('Unexpected Error occurred while converting openid. : %s', e, exc_info=1)
    else:
        logger.error("This user doesn't have enough authorization data. : %s", auth_info)
    return easy_id


def get_point_api_response(request, easy_id):
    """ Point API get-stdonly の XML レスポンスを返却する。 """
    point_api_response = None
    if easy_id:
        try:
            group_id = request.organization.setting.point_group_id
            reason_id = request.organization.setting.point_reason_id
            point_api_response = point_client.get_stdonly(request, easy_id, group_id, reason_id)
        except PointAPIError as e:
            # Point API のコール失敗。stack trace は altair.point で出力されている
            logger.error(e.message)
        except Exception as e:
            logger.error('Unexpected Error occurred while calling Point API get-stdonly. : %s', e, exc_info=1)
    return point_api_response


def get_all_result_code(point_api_response):
    """ Point API レスポンスから全ての result_code をリストで返却する。 """
    try:
        if point_api_response:
            return point_api.get_result_code(point_api_response)
    except Exception as e:
        # Point API のレスポンスが正しい XML 形式でない
        logger.error('Point API response is invalid format. : %s', e, exc_info=1)
    return list()


def convert_point_element_to_dict(point_element):
    """ Point API の XML 形式のレスポンスからポイント情報を取得し dictionary にして返却する。 """
    return {
        'fix_point': int(point_api.get_point_element(point_element, 'fix_point')),  # 通常ポイント
        'sec_able_point': int(point_api.get_point_element(point_element, 'sec_able_point')),  # 充当可能ポイント
        'order_max_point': int(point_api.get_point_element(point_element, 'order_max_point')),  # 1回あたり利用できる最大ポイント数
        'min_point': int(point_api.get_point_element(point_element, 'min_point'))  # 利用するポイント数の下限値
    }


def get_externalmember_email_address(user_authenticated_policy):
    """ユーザーの認証ポリシーから外部会員のメールアドレスを取得します"""
    policy = user_authenticated_policy.get(EXTERNALMEMBER_AUTH_IDENTIFIER_NAME)
    email_address = None
    if policy:
        email_address = policy.get(EXTERNALMEMBER_EMAIL_ADDRESS_POLICY_NAME)
    return email_address


def get_contact_url(request, fail_exc=ValueError):
    organization = request.organization
    if organization is None:
        raise fail_exc("organization is not found")
    retval = c_api.get_default_contact_url(request, organization, request.mobile_ua.carrier)
    if retval is None:
        raise fail_exc("no contact url")
    return retval

def safe_get_contact_url(request, default=""):
    try:
        return get_contact_url(request, Exception)
    except Exception as e:
        logger.warn(str(e))
        return default

def store_extra_form_data(request, data):
    request.session['extra_form'] = data

def load_extra_form_data(request):
    return request.session.get('extra_form')

def clear_extra_form_data(request):
    if 'extra_form' in request.session:
        del request.session['extra_form']

def get_cart_setting(request, cart_setting_id, session=None):
    if session is None:
        if request is not None:
            session = get_db_session(request, 'slave')
        else:
            raise ValueError('either request or session must be non-null')
    return session.query(CartSetting).filter_by(id=cart_setting_id).first()

def get_cart_setting_by_name(request, name, organization_id=None, session=None):
    if session is None:
        if request is not None:
            session = get_db_session(request, 'slave')
        else:
            raise ValueError('either request or session must be non-null')
    if organization_id is None:
        organization_id = request.organization.id
    return session.query(CartSetting).filter(CartSetting.organization_id == organization_id, CartSetting.name == name).one()

def get_cart_setting_from_order_like(request, order_like):
    session = get_db_session(request, 'slave')
    cart_setting_id = order_like.cart_setting_id
    if cart_setting_id is None:
        cart_setting = session.query(CartSetting) \
            .join(c_models.OrganizationSetting.cart_setting) \
            .join(c_models.OrganizationSetting.organization) \
            .filter(c_models.Organization.id == order_like.organization_id) \
            .one()
        return cart_setting
    else:
        return session.query(CartSetting) \
            .filter_by(id=cart_setting_id) \
            .one()


def is_booster_cart(cart_setting):
    return cart_setting.type == "booster" if cart_setting else False


def is_booster_or_fc_cart(cart_setting):
    return cart_setting.type == "booster" or cart_setting.type == "fc" if cart_setting else False


def is_fc_cart(cart_setting):
    return cart_setting.type == "fc" if cart_setting else False


def is_passport_cart(cart_setting):
    return cart_setting.type == "passport" if cart_setting else False


def is_goods_cart(cart_setting):
    return cart_setting.goods_cart if cart_setting else False


class _DummyCart(c_models.CartMixin):
    order_no = u'ZZ0000000000'

    def __init__(self, organization_id, created_at, items, sales_segment, payment_delivery_pair):
        self.organization_id = organization_id
        self.created_at = created_at
        self.items = items
        self.sales_segment = sales_segment
        self.payment_delivery_pair = payment_delivery_pair

    @property
    def performance(self):
        return self.sales_segment.performance

    @property
    def shipping_address(self):
        return None

    @property
    def discount_amount(self):
        return dc_util.get_discount_amount(self)

    @property
    def total_amount(self):
        return c_api.calculate_total_amount(self)

    @property
    def payment_amount(self):
        # payment_amountはポイント利用額を除いた支払額を意味するが、_DummyCartはポイント入力画面よりも前の画面で使われるため、
        # この時点では常にポイント利用額は0となる。よってtotal_amountと同じ値となるため、total_amountと同じ定義にしている
        return c_api.calculate_total_amount(self)

    @property
    def point_use_type(self):
        # point_use_typeはポイント利用タイプを返却するが、_DummyCartはポイント入力画面よりも前の画面で使われるため、
        # この時点では常にポイント利用額は0となる。よってPointUseTypeEnum.NoUse(ポイント利用無)を常に返却する
        return c_models.PointUseTypeEnum.NoUse

    @property
    def delivery_fee(self):
        return self.sales_segment.get_delivery_fee(
            self.payment_delivery_pair,
            [(p.product, p.quantity) for p in self.items])

    @property
    def transaction_fee(self):
        return self.sales_segment.get_transaction_fee(
            self.payment_delivery_pair,
            [(p.product, p.quantity) for p in self.items])

    @property
    def system_fee(self):
        return self.sales_segment.get_system_fee(
            self.payment_delivery_pair,
            [(p.product, p.quantity) for p in self.items])

    @property
    def special_fee(self):
        return self.sales_segment.get_special_fee(
            self.payment_delivery_pair,
            [(p.product, p.quantity) for p in self.items])


def check_if_payment_delivery_method_pair_is_applicable(request, cart, payment_delivery_pair):
    dummy_cart = _DummyCart(
        organization_id=request.organization.id,
        created_at=cart.created_at,
        items=cart.items,
        sales_segment=cart.sales_segment,
        payment_delivery_pair=payment_delivery_pair
        )
    try:
        payment_delivery_plugin, payment_plugin, delivery_plugin = payments_api.lookup_plugin(request, payment_delivery_pair)
    except PaymentDeliveryMethodPairNotFound:
        return False
    try:
        if payment_delivery_plugin is not None:
            payment_delivery_plugin.validate_order(request, dummy_cart)
        else:
            if payment_plugin is not None:
                payment_plugin.validate_order(request, dummy_cart)
            if delivery_plugin is not None:
                delivery_plugin.validate_order(request, dummy_cart)
    except OrderLikeValidationFailure as e:
        logger.debug(e.message)
        return False
    return True

def coerce_extra_form_data(request, extra_form_data):
    attributes = {}
    for k, v in extra_form_data.items():
        if isinstance(v, list):
            v = ','.join(v)
        elif isinstance(v, datetime):
            v = v.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(v, date):
            v = v.strftime("%Y-%m-%d")
        elif isinstance(v, time):
            v = v.strftime("%H:%M:%S")
        attributes[k] = v
    return attributes


def make_order_from_cart(request, context, cart):
    """
    カートからオーダーの作成処理を行う。
    楽天PAY決済時と通常の購入方法でチェック処理が二重管理にならないよう、こちらに処理を組み込んで共有(TKT-6237)。
    :param Request request: リクエスト
    :param CartBoundTicketingCartResource context: コンテキスト
    :param Cart cart: カート
    :return: オーダー
    """

    context.check_deleted_product(cart)
    context.check_order_limit(cart)

    # クーポン・割引コードの利用がある場合
    # 再バリデーションおよび、スポーツサービス開発のコードの場合はここでAPIアクセスして使用
    # 自社発行コードの使用は「altair.app.ticketing.orders.models.Order#create_from_cart」の中で行われている
    if cart.used_discount_codes:
        validated = context.is_discount_code_still_available(cart)
        context.use_sports_service_discount_code(validated, cart=cart)

    if cart.point_use_type is c_models.PointUseTypeEnum.NoUse:
        payment = Payment(cart, request)
    else:
        # ポイント利用がある場合は easyid を取得して Payment にセットする
        user_credential = lookup_user_credential(context.authenticated_user())
        easy_id = getattr(user_credential, 'easy_id', None)
        if not easy_id:
            logger.error("This user doesn't have easy_id although cart's point_amount is {}.".format(cart.point_amount))
            raise PaymentError(context, request, cause=None)
        # Point 利用確定処理は Point API の記録をステータスとして PointRedeem に書き込みます。
        # Exception が raise された場合でも PointRedeem のレコードはロールバックの影響を受けることなく,
        # 残されないといけないので autocommit される別セッションで行います。
        autocommit_point_scoped_session = scoped_session(sessionmaker(autocommit=True))
        payment = Payment(cart, request, session=autocommit_point_scoped_session, easy_id=easy_id)

    try:
        # オーダー作成
        order = payment.call_payment()
        create_external_serial_order(order)
    except PointSecureApprovalFailureError as e:
        # ブラウザバックで購入確認画面に戻り再度購入処理を行うと, PointRedeem への Insert 処理で重複が発生し
        # エラーが繰り返されるので, ここでカートを切り離します。
        disassociate_cart_from_session(request)
        raise PaymentError(context, request, point_result_code=e.result_code, cause=e)

    extra_form_data = load_extra_form_data(request)
    if extra_form_data is not None:
        order.attributes = coerce_extra_form_data(request, extra_form_data)

    notify_order_completed(request, order)
    clear_extra_form_data(request)
    return order


def create_external_serial_order(order):
    """
    対象のProductItemがExternalSerialCodeSettingと連携している場合はシリアルコードを割り当てます
    ExternalSerialCodeSettingに紐づくExternalSerialCodeの未使用レコードを割り当てて
    ExternalSerialOrderテーブルを作成します
    :param order: カート
    :return: なし
    """

    for order_product in order.ordered_products:
        ordered_product_items = [order_product_item for order_product_item in order_product.ordered_product_items if
                                 order_product_item.product_item.external_serial_code_product_item_pair.setting.id]
        for order_product_item in ordered_product_items:
            external_serial_code_setting_id = order_product_item.product_item. \
                external_serial_code_product_item_pair.setting.id
            now = datetime.now()
            for token in order_product_item.tokens:
                external_serial_code = ExternalSerialCode.query \
                    .filter(ExternalSerialCode.external_serial_code_setting_id == external_serial_code_setting_id) \
                    .filter(ExternalSerialCode.used_at == None) \
                    .filter(ExternalSerialCode.deleted_at == None).with_lockmode('update').first()
                external_serial_code_order = ExternalSerialCodeOrder()
                external_serial_code_order.external_serial_code_id = external_serial_code.id
                external_serial_code_order.ordered_product_item_token_id = token.id
                external_serial_code_order.save()
                external_serial_code.used_at = now
                external_serial_code.save()


def is_spa_mode(request):
    if request.cookies.get(SPA_COOKIE):
        return True
    return False


def set_spa_access(response):
    response.set_cookie(SPA_COOKIE, str(datetime.now()))
    return response


def delete_spa_access(response):
    response.delete_cookie(SPA_COOKIE)
    return response

def log_extra_form_fields(order_no, extra_data):
    out_extra_field = u''
    if order_no:
        out_extra_field = u'order_no:'+order_no
    for key, value in extra_data.iteritems():
        if isinstance(value, (dict, list)):
            out_extra_field += u' ' + key + ':' + value[0] if value else u''
        elif isinstance(value, date):
            out_extra_field += u' ' + key + ':' + value.strftime('%Y-%m-%d') if value else u''
        elif isinstance(value, (int, float)):
            out_extra_field += u' ' + key + ':' + str(value) if value else u''
        else:
            out_extra_field += u' ' + key + ':' + value if value else u''
    logger.info('extra fields:%s' % out_extra_field)

def is_spa_or_mobile_mode(request):
    if is_mobile_request(request) or is_spa_mode(request):
        return True
    return False
