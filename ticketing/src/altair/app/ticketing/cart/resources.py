# -*- coding:utf-8 -*-

import logging
import json
import requests
from datetime import datetime, date
import itertools
from sqlalchemy import sql
from pyramid.security import Everyone, Allow, DENY_ALL
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.orm import joinedload, joinedload_all
from sqlalchemy.orm.session import make_transient
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from zope.interface import implementer
from webob.multidict import MultiDict
from altair.sqlahelper import get_db_session
from altair.app.ticketing.temp_store import TemporaryStoreError
from altair.app.ticketing.payments.interfaces import IOrderPayment, IOrderDelivery
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.core import api as core_api
from altair.app.ticketing.orders import models as order_models
from altair.app.ticketing.core.interfaces import IOrderQueryable
from altair.app.ticketing.users import models as u_models
from altair.app.ticketing.utils import memoize
from ..discount_code.models import UsedDiscountCodeCart, DiscountCodeCode
from ..discount_code import api as discount_api
from . import models as m
from . import api as cart_api
from .exceptions import NoCartError, DeletedProductError, InvalidCSRFTokenException
from .interfaces import (
    ICartResource,
    ICartPayment,
    ICartDelivery,
    )
from .exceptions import (
    OutTermSalesException,
    NoSalesSegment,
    NoPerformanceError,
    OverOrderLimitException,
    OverQuantityLimitException,
    InvalidCartStatusError,
    DiscountCodeConfirmError,
    OAuthRequiredSettingError
)
from zope.deprecation import deprecate
from altair.now import get_now
import functools

logger = logging.getLogger(__name__)

def products_filter_by_salessegment(products, sales_segment):
    if sales_segment is None:
        logger.debug("debug: products_filter -- salessegment is none")
    if sales_segment:
        return products.filter_by(sales_segment=sales_segment)
    return products

class DefaultCartSetting(object):
    type = u'standard'
    text_for_product_name = u'商品'
    title = u''
    contact_url= u'mailto:info@tstar.jp'
    contact_tel = u''
    office_hours = u''
    contact_name = u''
    mobile_header_background_color = u'#000'
    mobile_marker_color = u'#000'
    mobile_required_marker_color = u'#f00'
    fc_announce_page_url = u''
    fc_announce_page_url_mobile = u''
    fc_announce_page_title = u''
    privacy_policy_page_url = u''
    privacy_policy_page_url_mobile = u''
    orderreview_page_url = u''
    mail_filter_domain_notice_template = None

default_cart_setting = DefaultCartSetting()

def get_default_cart_setting(request):
    return default_cart_setting

@implementer(ICartResource)
class TicketingCartResourceBase(object):
    def __init__(self, request, sales_segment_id=None):
        self.request = request
        self.now = get_now(request)
        self._sales_segment_id = sales_segment_id
        self._sales_segment = None
        self._cart = None
        self._read_only_cart = None
        self._populate_params()

    def _populate_params(self):
        if self.request.matchdict:
            self._populate_matchdict_params()

    def _populate_matchdict_params(self):
        try:
            self._sales_segment_id = long(self.request.matchdict.get('sales_segment_id'))
        except (ValueError, TypeError):
            pass

    @property
    def cart(self):
        return cart_api.get_cart_safe(self.request, for_update=True)

    @property
    def read_only_cart(self):
        return cart_api.get_cart_safe(self.request, for_update=False)

    @property
    def sales_segments(self):
        """現在のURLから決定できるすべての販売区分"""
        raise NotImplementedError()

    @property
    def event(self):
        raise NotImplementedError()

    @property
    def performance(self):
        raise NotImplementedError()

    @property
    def memberships(self):
        from altair.app.ticketing.models import DBSession as session
        organization = cart_api.get_organization(self.request)
        memberships = session.query(u_models.Membership).filter_by(organization_id=organization.id).all()
        logger.debug('organization %s' % organization.code)
        logger.debug('memberships %s' % memberships)
        return memberships

    @property
    def membershipinfo(self):
        return cart_api.get_membership(self.authenticated_user())

    @reify
    def membergroups(self):
        sales_segment = self.sales_segment
        if sales_segment is None:
            return []
        return sales_segment.membergroups

    @reify
    def asid(self):
        organization = cart_api.get_organization(self.request)
        asid =organization.setting.asid
        logger.debug('organization %s' % organization.code)
        logger.debug('asid %s' % asid)
        return asid

    @reify
    def asid_mobile(self):
        organization = cart_api.get_organization(self.request)
        asid_mobile =organization.setting.asid_mobile
        logger.debug('organization %s' % organization.code)
        logger.debug('asid %s' % asid_mobile)
        return asid_mobile

    @reify
    def asid_smartphone(self):
        organization = cart_api.get_organization(self.request)
        asid_smartphone =organization.setting.asid_smartphone
        logger.debug('organization %s' % organization.code)
        logger.debug('asid %s' % asid_smartphone)
        return asid_smartphone

    ## なぜ２つ?
    def available_payment_delivery_method_pairs(self, sales_segment):
        return sales_segment.available_payment_delivery_method_pairs(self.now) #xxx?
    ##

    def get_payment_delivery_method_pair(self, start_on=None):
        sales_segment = self.sales_segment
        q = c_models.PaymentDeliveryMethodPair.query.filter(
            c_models.PaymentDeliveryMethodPair.sales_segment_group_id==sales_segment.id
        ).filter(
            c_models.PaymentDeliveryMethodPair.public==1,
        ).order_by(
            c_models.PaymentDeliveryMethodPair.transaction_fee,
            c_models.PaymentDeliveryMethodPair.payment_method_id,
            c_models.PaymentDeliveryMethodPair.delivery_fee,
            c_models.PaymentDeliveryMethodPair.delivery_method_id,
        )
        if start_on:
            today = date.today()
            period_days = date(start_on.year, start_on.month, start_on.day) - today
            q = q.filter(
                c_models.PaymentDeliveryMethodPair.unavailable_period_days<=period_days.days
            )
        pairs = q.all()
        return pairs

    def authenticated_user(self):
        """現在認証中のユーザ"""
        return self.request.altair_auth_info

    def check_recaptch(self, recaptcha):
        url = "https://www.google.com/recaptcha/api/siteverify"
        param = dict(secret=self.recaptcha_secret, response=recaptcha)
        response = requests.post(url, param)
        if not response.content:
            return False
        return json.loads(response.content)['success']

    @reify
    def available_sales_segments(self):
        """現在認証済みのユーザが今買える全販売区分"""
        per_performance_sales_segments_dict = {}
        read_only_cart = None
        try:
            read_only_cart = self.read_only_cart
        except NoCartError as e:
            logger.info('cart is not created (%s)' % e)

        for sales_segment in self.sales_segments:
            if (read_only_cart and read_only_cart.sales_segment_id == sales_segment.id) \
               or (sales_segment.available_payment_delivery_method_pairs(self.now) and \
                   sales_segment.in_term(self.now)):
                per_performance_sales_segments = \
                    per_performance_sales_segments_dict.get(sales_segment.performance_id)
                if per_performance_sales_segments is None:
                    per_performance_sales_segments = per_performance_sales_segments_dict[sales_segment.performance_id] = ([], [])
                per_performance_sales_segments[sales_segment.sales_segment_group.has_guest and 1 or 0].append(sales_segment)

        # 何してるか意味不明だと思うんですけど
        # per_performance_sales_segment_dict = {
        #    1L: ([非guest用販売区分, ...], [guest用販売区分, ...]),
        #    2L: ([非guest用販売区分, ...], [guest用販売区分, ...]),
        #    ...
        # }
        # となっていて、(キーはパフォーマンスのid)
        # 各パフォーマンスで非guest用の販売区分があればそれを優先し
        # guest用の販売区分しかなければそれを使うということをする
        #
        # itertools.chain([[非guest用販売区分, ...], [guest用販売区分, ...], [guest用販売区分...]])
        #
        # ということ。
        # ここで performance の情報を捨ててしまうのがちょっともったいない。

        retval = list(itertools.chain(*((pair[0] or pair[1]) for pair in per_performance_sales_segments_dict.itervalues())))
        if not retval:
            # 公演が指定されてるなら販売区分を絞る
            sales_segments = self.sales_segments
            # 次の販売区分があるなら
            data = c_models.Event.find_next_and_last_sales_segment_period(
                sales_segments=sales_segments,
                now=self.now)
            if any(data):
                for datum in data:
                    if datum is not None:
                        datum['event'] = datum['performance'].event
                raise OutTermSalesException.from_resource(self, self.request, next=data[0], last=data[1], type_=self.__class__)
            else:
                raise HTTPNotFound()
        return retval

    @reify
    def sales_segment(self):
        """ 該当イベントのSalesSegment取得
        """
        if self._sales_segment_id is None:
            logger.info("sales_segment_id is not provided")
            raise NoSalesSegment.from_resource(self, self.request, sales_segment_id=None)

        # XXX: 件数少ないしリニアサーチでいいよね
        for sales_segment in self.available_sales_segments:
            if sales_segment.id == self._sales_segment_id:
                return sales_segment

        raise NoSalesSegment.from_resource(self, self.request, sales_segment_id=None)

    def get_sales_segment(self):
        return self.sales_segment

    @property
    def raw_sales_segment(self):
        if self._sales_segment is None:
            if self._sales_segment_id is None:
                return None
            organization = cart_api.get_organization(self.request)
            sales_segment = None
            try:
                sales_segment = c_models.SalesSegment.query \
                    .join(c_models.SalesSegment.sales_segment_group) \
                    .join(c_models.SalesSegmentGroup.event) \
                    .filter(c_models.Event.organization_id == organization.id) \
                    .filter(c_models.SalesSegment.id == self._sales_segment_id) \
                    .one()
            except:
                pass
            self._sales_segment = sales_segment
        return self._sales_segment

    @property
    def membership(self):
        user = self.authenticated_user()
        if user is None:
            return None
        if 'membership' not in user:
            return None

        membership = user['membership']
        return membership

    @reify
    def recaptcha_sitekey(self):
        return "6LdanyoUAAAAAOh3LNep4EtZaKV19dCE92gMCAcl"

    @reify
    def recaptcha_secret(self):
        return "6LdanyoUAAAAAACXpFL08qMlCUyMkaMFF5xwUPlZ"

    @reify
    def user_object(self):
        return cart_api.get_user(self.authenticated_user())

    @reify
    def host_base_url(self):
        return core_api.get_host_base_url(self.request)

    @reify
    def switch_pc_url(self):
        if self.event is None:
            return ''
        performance_id = self.request.GET.get('pid') or self.request.GET.get('performance')
        if performance_id is not None:
            return self.request.route_url('cart.switchpc', event_id=self.event.id, _query=dict(performance=performance_id))
        else:
            return self.request.route_url('cart.switchpc', event_id=self.event.id)

    @reify
    def switch_sp_url(self):
        if self.event is None:
            return ''
        performance_id = self.request.GET.get('pid') or self.request.GET.get('performance')
        if performance_id is not None:
            return self.request.route_url('cart.switchsp', event_id=self.event.id, _query=dict(performance=performance_id))
        else:
            return self.request.route_url('cart.switchsp', event_id=self.event.id)

    @memoize()
    def get_total_orders_and_quantities_per_user(self, sales_segment):
        """ユーザごとのこれまでの注文数や購入数を取得する"""
        setting = sales_segment.setting
        user = self.user_object
        mail_addresses = None
        try:
            mail_addresses = self.read_only_cart.shipping_address and self.read_only_cart.shipping_address.emails
        except NoCartError:
            pass
        retval = []
        if user or mail_addresses:
            while setting is not None:
                # 設定なしの場合は何度でも購入可能
                container = setting.container
                if IOrderQueryable.providedBy(container):
                    slave_session = get_db_session(self.request, name="slave")
                    query = slave_session.query(
                        sql.expression.func.count(sql.expression.distinct(order_models.Order.id)),
                        sql.expression.func.sum(order_models.OrderedProductItem.quantity)
                        ) \
                        .outerjoin(order_models.OrderedProduct, order_models.Order.items) \
                        .outerjoin(order_models.OrderedProductItem, order_models.OrderedProduct.elements)
                    if user:
                        query = container.query_orders_by_user(user, filter_canceled=True, filter_refunded=True, query=query)
                    elif mail_addresses:
                        query = container.query_orders_by_mailaddresses(mail_addresses, filter_canceled=True, filter_refunded=True, query=query)
                    order_count, total_quantity = query.one()
                    if order_count is None:
                        order_count = 0
                    if total_quantity is None:
                        total_quantity = 0
                    logger.info(
                        "%r(id=%d): order_limit=%r, max_quantity_per_user=%r, orders=%d, total_quantity=%d" % (
                            container.__class__,
                            container.id,
                            setting.order_limit,
                            setting.max_quantity_per_user,
                            order_count,
                            total_quantity
                            )
                        )
                    retval.append(
                        (
                            container,
                            dict(
                                order_count=order_count,
                                total_quantity=total_quantity,
                                order_limit=setting.order_limit,
                                max_quantity_per_user=setting.max_quantity_per_user
                                )
                            )
                        )
                else:
                    logger.info("%s does not implement IOrderQueryable. skip" % container.__class__)
                setting = setting.super
        return retval

    def check_order_limit(self):
        """ 購入回数および購入枚数制限チェック
        設定なしの場合は何度でも購入可能です。
        カウントするOrder数にcancelされたOrderは含まれません。
        """
        cart_total_quantity = sum(element.quantity for item in self.read_only_cart.items for element in item.elements)
        total_orders_and_quantities_per_user = self.get_total_orders_and_quantities_per_user(self.read_only_cart.sales_segment)
        for container, record in total_orders_and_quantities_per_user:
            order_limit = record['order_limit']
            max_quantity_per_user = record['max_quantity_per_user']
            order_count = record['order_count']
            total_quantity = record['total_quantity']
            # XXX: order_limit はかつて 0 が無効値だった...
            if order_limit and order_count >= order_limit:
                logger.info("order_limit exceeded: %d >= %d" % (order_count, order_limit))
                raise OverOrderLimitException.from_resource(self, self.request, order_limit=order_limit)
            if max_quantity_per_user is not None:
                if total_quantity + cart_total_quantity > max_quantity_per_user:
                    logger.info("order_limit exceeded: %d >= %d" % (total_quantity, max_quantity_per_user))
                    raise OverQuantityLimitException.from_resource(self, self.request, quantity_limit=max_quantity_per_user)

    def check_deleted_product(self, cart):
        # カートに紐付いた商品が消されていないか確認
        for carted_product in cart.products:
            if not carted_product.product:
                logger.info(u"Product is deleted. CartID = {0}".format(cart.id))
                raise DeletedProductError(u"こちらの商品は現在ご購入いただけません。")

    def _login_required(self, auth_type):
        if auth_type == 'fc_auth':
            """ 指定イベントがログイン画面を必要とするか """
            # 終了分もあわせて、このeventからひもづく sales_segment -> membergroupに1つでもnon-guestがあれば True
            q = u_models.MemberGroup.query \
                .filter(u_models.MemberGroup.is_guest==False) \
                .filter(u_models.MemberGroup.id == u_models.MemberGroup_SalesSegment.c.membergroup_id) \
                .filter(c_models.SalesSegment.id == u_models.MemberGroup_SalesSegment.c.sales_segment_id) \
                .filter(c_models.SalesSegment.public == True)

            while True:
                # まずは販売区分を見る
                sales_segment = None
                try:
                    sales_segment = self.sales_segment
                except:
                    pass
                if sales_segment is not None:
                    q = q.filter(c_models.SalesSegment.id == sales_segment.id)
                    break
                # 次にパフォーマンス
                performance = None
                try:
                    performance = self.performance
                except:
                    pass
                if performance is not None:
                    q = q.filter(c_models.SalesSegment.performance_id == performance.id)
                    break

                # 最後にイベントを見て
                event = None
                try:
                    event = self.event
                except:
                    pass
                if event is not None:
                    # XXX: SalesSegment.event_id は deprecated
                    q = q.filter(c_models.SalesSegment.event_id == event.id)
                    break

                # MemberGroup を特定できるものがなければ、エラーにする
                logger.info("could not determine an event, performance nor sales_segment from the request URI")
                return True

            return q.first() is not None
        else:
            return True

    @reify
    def __acl__(self):
        acl = []
        if self.cart_setting is not None:
            if any(self._login_required(auth_type) for auth_type in self.cart_setting.auth_types):
                acl.append((Allow, 'altair.auth.authenticator:%s' % '+'.join(sorted(self.cart_setting.auth_types)), 'buy'))
            else:
                acl.append((Allow, Everyone, 'buy'))
        acl.append(DENY_ALL)
        return acl

    @reify
    def cart_setting(self):
        cart_setting = (self.event and self.event.setting and self.event.setting.cart_setting) or cart_api.get_organization(self.request).setting.cart_setting
        if cart_setting is not None:
            make_transient(cart_setting)
        else:
            cart_setting = get_default_cart_setting(self.request)
        return cart_setting

    # 今後複数認証を並行で使うことも想定してリストで返すことにする
    @reify
    def oauth_service_providers(self):
        if self.cart_setting.auth_type == u'altair.oauth_auth.plugin.OAuthAuthPlugin':
            return [self.cart_setting.oauth_service_provider] or []
        return []

    def _validate_required_oauth_params(self, params):
        # 必須項目が不足している場合は、アラートをあげるようにする
        if self.cart_setting.auth_type == u'altair.oauth_auth.plugin.OAuthAuthPlugin':
            if not (params['client_id'] and
                        params['client_secret'] and
                        params['endpoint_api'] and
                        params['endpoint_token'] and
                        params['endpoint_token_revocation'] and
                        params['endpoint_authz']):
                raise OAuthRequiredSettingError('required oauth setting is not specified.')

    @reify
    def oauth_params(self):
        params = dict(
            client_id=self.cart_setting.oauth_client_id,
            client_secret=self.cart_setting.oauth_client_secret,
            endpoint_api=self.cart_setting.oauth_endpoint_api,
            endpoint_token=self.cart_setting.oauth_endpoint_token,
            endpoint_token_revocation=self.cart_setting.oauth_endpoint_token_revocation,
            scope=self.cart_setting.oauth_scope,
            openid_prompt=self.cart_setting.openid_prompt,
            endpoint_authz=self.cart_setting.oauth_endpoint_authz
        )
        try:
            self._validate_required_oauth_params(params)
        except OAuthRequiredSettingError as e:
            raise e
        return params


class EventOrientedTicketingCartResource(TicketingCartResourceBase):
    def __init__(self, request, event_id=None):
        self._event_id = event_id
        self._event = None
        super(EventOrientedTicketingCartResource, self).__init__(request)

    def _populate_matchdict_params(self):
        super(EventOrientedTicketingCartResource, self)._populate_matchdict_params()
        if self._event_id is None:
            try:
                self._event_id = long(self.request.matchdict.get('event_id'))
            except (ValueError, TypeError):
                pass

    @property
    def event(self):
        performance = self.performance
        if performance is not None:
            return performance.event

        if self._event is None:
            organization = cart_api.get_organization(self.request)
            event = None
            try:
                event = c_models.Event.query \
                    .options(joinedload(c_models.Event.setting)) \
                    .filter(c_models.Event.id==self._event_id) \
                    .filter(c_models.Event.organization_id==organization.id) \
                    .one()
            except NoResultFound:
                pass
            self._event = event
        return self._event

    @property
    def performance(self):
        sales_segment = self.raw_sales_segment
        if sales_segment is not None and sales_segment.sales_segment_group.event_id == self._event_id:
            return sales_segment.performance
        cart = None
        try:
            cart = self.read_only_cart
        except NoCartError:
            pass
        if cart is not None and (self._event_id is None or cart.performance.event_id == self._event_id):
            return cart.performance
        return None

    @reify
    def sales_segments(self):
        """現在認証済みのユーザとイベントに関連する全販売区分"""
        if self.event is None:
            raise HTTPNotFound()
        return self.event.query_sales_segments(
            user=self.authenticated_user(),
            type='all').all()

class PerformanceOrientedTicketingCartResource(TicketingCartResourceBase):
    def __init__(self, request, performance_id=None):
        self._performance_id = performance_id
        self._performance = None
        super(PerformanceOrientedTicketingCartResource, self).__init__(request)

    def _populate_matchdict_params(self):
        super(PerformanceOrientedTicketingCartResource, self)._populate_matchdict_params()
        if self._performance_id is None:
            try:
                self._performance_id = long(self.request.matchdict.get('performance_id'))
            except (ValueError, TypeError):
                pass

    @property
    def performance(self):
        if self._performance_id is None:
            cart = None
            try:
                cart = self.read_only_cart
            except NoCartError:
                pass
            if cart is not None:
                return cart.performance
        else:
            if self._performance is None:
                organization = cart_api.get_organization(self.request)
                performance = None
                try:
                    performance = c_models.Performance.query \
                        .options(joinedload_all(c_models.Performance.event, c_models.Event.setting)) \
                        .join(c_models.Performance.event) \
                        .filter(c_models.Performance.id == self._performance_id) \
                        .filter(c_models.Event.organization_id == organization.id) \
                        .one()
                except NoResultFound:
                    pass
                if performance is None:
                    raise NoPerformanceError('Performance (id=%d) not found' % self._performance_id)
                self._performance = performance
            return self._performance

    @property
    def event(self):
        return self.performance.event if self.performance else None

    @reify
    def sales_segments(self):
        """現在認証済みのユーザとパフォーマンスに関連する全販売区分"""
        if self.performance is None:
            raise HTTPNotFound()
        return self.performance.query_sales_segments(
            user=self.authenticated_user(),
            type='all').all()

    @reify
    def switch_pc_url(self):
        if self.performance is None:
            return ''
        return self.request.route_url('cart.switchpc.perf', performance_id=self.performance.id)

    @reify
    def switch_sp_url(self):
        if self.performance is None:
            return ''
        return self.request.route_url('cart.switchsp.perf', performance_id=self.performance.id)


class SalesSegmentOrientedTicketingCartResource(TicketingCartResourceBase):
    def __init__(self, request, sales_segment_id=None):
        super(SalesSegmentOrientedTicketingCartResource, self).__init__(request, sales_segment_id)

    @reify
    def sales_segment(self):
        if self.raw_sales_segment is None:
            raise NoSalesSegment(self.request, '', host_base_url=self.host_base_url)
        return self.raw_sales_segment

    @property
    def performance(self):
        return self.sales_segment.performance

    @property
    def event(self):
        return self.performance.event if self.performance else None

    @reify
    def sales_segments(self):
        """現在認証済みのユーザとパフォーマンスに関連する全販売区分"""
        return [self.sales_segment] if self.sales_segment.applicable(user=self.authenticated_user(), type='all') else []


class DiscountCodeTicketingCartResources(SalesSegmentOrientedTicketingCartResource):
    def __init__(self, request, sales_segment_id=None):
        super(DiscountCodeTicketingCartResources, self).__init__(request, sales_segment_id)
        self.session = get_db_session(self.request, name="slave")

    def sorted_carted_product_items(self):
        sorted_cart_product_items = list()
        for carted_product in self.read_only_cart.items:
            for carted_product_item in carted_product.elements:
                sorted_cart_product_items.append(carted_product_item)
        sorted_cart_product_items = [obj for obj in reversed(sorted(sorted_cart_product_items, key=lambda x:x.price))]
        return sorted_cart_product_items

    def create_discount_code_forms(self):
        from . import schemas
        cart = self.read_only_cart
        forms = []
        for _ in range(cart.carted_product_item_count):
            forms.append(schemas.DiscountCodeForm())
        return forms

    def create_validated_forms(self, code_dict_list):
        """
        バリデーションエラー発生時、入力されたコードを上に詰めて表示する。
        未入力だったフォーム分は下に配置されるようになっている。
        :param code_dict_list:
        :return:
        """
        from . import schemas
        forms = []
        for code_dict in code_dict_list:
            forms.append(code_dict['form'])

        cart = self.read_only_cart
        remaining_count = cart.carted_product_item_count - len(forms)
        if remaining_count > 0:
            for index in range(remaining_count):
                forms.append(schemas.DiscountCodeForm())
        return forms

    def upper_code(self):
        """POSTされたパラメータを大文字に変更"""
        if 'code' in self.request.POST:
            upper_list = []

            for item in self.request.POST.items():
                each_code_tuple = item[0], item[1].upper()
                upper_list.append(each_code_tuple)

            self.request.POST.clear()
            self.request.POST.extend(upper_list)

    def create_code_dict_list(self, code_str_list):
        """
        入力された割引コード数分のdictをリストで作成している
        :param code_str_list: 割引コード文字列のリスト。この情報をもとにdictで様々な情報を付加していっている
        :return code_dict_list: 割引コード文字列、紐づく商品、Formオブジェクトなどがまとめられたdict
        """
        from . import schemas
        code_dict_list = []
        num_used_codes = len(code_str_list)
        if num_used_codes == 0:
            return code_dict_list

        sorted_cart_product_items = self.sorted_carted_product_items()
        settings = self.read_only_cart.performance.find_available_target_settings(
            max_price=self.read_only_cart.highest_item_price,
            session=self.session,
            now=self.now)

        cnt = 0
        for carted_product_item in sorted_cart_product_items:
            for _ in range(carted_product_item.quantity):
                if cnt == num_used_codes:
                    break

                form = schemas.DiscountCodeForm(discount_code_settings=settings)
                form.code.data = code_str_list[cnt]
                code_dict_list.append({
                    'code': code_str_list[cnt],
                    'carted_product_item': carted_product_item,
                    'form': form,
                    'discount_code_setting': self.read_only_cart.performance.find_available_target_settings(
                        first_4_digits=code_str_list[cnt][:4],
                        now=self.now
                    )
                })
                cnt += 1

        return code_dict_list

    def is_discount_code_still_available(self):
        code_str_list = [code.code for code in discount_api.get_used_discount_codes(self.read_only_cart)]
        code_dict_list = self.create_code_dict_list(code_str_list)
        if code_dict_list:
            validated = self.validate_discount_codes(code_dict_list)
            if self.exist_validate_error(validated):
                raise DiscountCodeConfirmError('the code attempted to use was changed its status')

        return True

    def temporarily_save_discount_code(self, code_dict_list):
        organization = cart_api.get_organization(self.request)
        discount_api.temporarily_save_discount_code(code_dict_list, organization, self.session)

    def get_carted_product_item_ids(self):
        cart = self.read_only_cart
        carted_product_item_ids = list()
        for carted_product in cart.items:
            for carted_product_item in carted_product.elements:
                carted_product_item_ids.append(carted_product_item.id)
        return carted_product_item_ids

    @property
    def carted_product_item_count(self):
        # カートに入っている商品明細の総数
        cart = self.read_only_cart
        count = 0
        for carted_product in cart.items:
            for carted_product_item in carted_product.elements:
                for item in range(carted_product_item.quantity):
                    count = count + 1
        return count

    def delete_temporarily_save_discount_code(self):
        carted_product_item_ids = self.get_carted_product_item_ids()
        codes = UsedDiscountCodeCart.query.filter(UsedDiscountCodeCart.carted_product_item_id.in_(carted_product_item_ids)).all()
        for code in codes:
            code.deleted_at = datetime.now()
        return True

    def if_discount_code_available_for_seat_selection(self):
        """
        ユーザーが選択した席種とそのパフォーマンスが割引コード適用可能か判定。
        管理画面における組織設定での利用フラグ、割引設定、および販売単位をチェックしている。
        :return: Boolean
        """
        if (not self.read_only_cart.organization.enable_discount_code) or \
                (not self.performance.find_available_target_settings(max_price=self.read_only_cart.highest_item_price,
                                                                     session=self.session,
                                                                     now=self.now)) or \
                (not self.read_only_cart.is_product_item_quantity_one):
            return False
        else:
            return True

    def validate_discount_codes(self, code_dict_list):
        code_str_list = [code_dict['form'].code.data for code_dict in code_dict_list]
        sports_service_codes = []
        for code_dict in code_dict_list:
            form = code_dict['form']
            if not form.validate():
                continue

            code = form.code.data

            # 重複コードバリデーション
            if discount_api.is_exist_duplicate_codes(code, code_str_list):
                form.add_duplicate_code_error()
                continue

            # 使用済みコードバリデーション
            organization = cart_api.get_organization(self.request)
            if discount_api.check_used_discount_code(code, organization):
                form.add_used_discount_code_error()
                continue

            code_setting = self.read_only_cart.performance.find_available_target_settings(first_4_digits=code[:4],
                                                                                          now=self.now)

            # 存在する自社コードか確認するバリデーション
            if code_setting.issued_by == 'own' and not self._is_exist_own_discount_code(code):
                form.not_existed_own_discount_code_error()
                continue

            # ファンクラブ会員専用クーポンの誤利用を防ぐバリデーション
            if code_setting.issued_by == 'sports_service':
                if self._is_sports_service_code_used_by_eligible_user():
                    sports_service_codes.append(code_dict)
                else:
                    form.add_non_fanclub_member_discount_code_error()
                    continue

        # スポーツサービス開発のAPIにアクセスして、使用可能なコードか確認する
        if sports_service_codes:
            self.confirm_sports_service_code_status(sports_service_codes)

        return code_dict_list

    def _is_exist_own_discount_code(self, code_str):
        """
        入力されたコードが自社コードだった場合、データベースに存在しているか確認する。
        :param code_str: 入力されたコード
        :return: Boolean
        """
        organization = cart_api.get_organization(self.request)
        try:
            self.session.query(DiscountCodeCode).filter(
                DiscountCodeCode.code == code_str,
                DiscountCodeCode.organization_id == organization.id
            ).one()
        except NoResultFound:
            # データベースに登録のないコードが入力されている
            return False
        except MultipleResultsFound as err:
            logger.error(
                'found duplicate discount codes "{}". {}'.format(code_str, err.message))
            return False

        # 正常にレコードが見つかった場合
        return True

    def _is_sports_service_code_used_by_eligible_user(self):
        """
        ファンクラブ会員専用クーポンの誤利用を防ぐバリデーション

        'authz_identifier'の値はログイン方法によって変化する

        「ファンクラブの方」でログインすると文字列の数字
        「一般の方」でログインするとOpenIDの文字列
        「その他会員IDをお持ちの方」でログインすると「acct:」から始まるメールアドレスのような文字列（例：acct:000409140429+eagles@eagles.stg.altr.jp）

        :return: Boolean
        """

        # OAuth認証していないユーザをはじく
        if not self.is_authz_user:
            return False

        authz_identifier = self.request.altair_auth_info['authz_identifier']
        # 数字だけで構成されていない場合（「一般の方」「その他会員IDをお持ちの方」ログイン）をはじく
        if not authz_identifier.isdigit():
            return False

        return True

    def exist_validate_error(self, code_dict_list):
        for code_dict in code_dict_list:
            if code_dict['form'].code.errors:
                return True
        return False

    @property
    def is_authz_user(self):
        """
        OAuth認証しているユーザの場合はTrueを返す。
        :return: Boolean
        """
        return "authz_identifier" in self.request.altair_auth_info

    def confirm_sports_service_code_status(self, code_dict_list):
        """
        スポーツサービス開発のAPIにアクセスして、使用可能なコードか確認する
        :param code_dict_list: 入力されたコードに割引コードやFormオブジェクトが結び付けられたdict
        :return: エラーがある場合はerrorsに文言が入る
        """
        result = discount_api.confirm_discount_code_status(self.request, code_dict_list)

        # 通信エラーなど。1つ目のformにデータを埋め込み表示
        if not result or not result['status'] == u'OK':
            return code_dict_list[0].code_dict['form'].add_internal_error()

        coupons = result['coupons']
        error_list = {}
        for coupon in coupons:
            if coupon['reason_cd'] != u'1010' or coupon['available_flg'] != u'1':
                error_list[coupon['coupon_cd']] = coupon['reason_cd']

        error_keys = error_list.keys()
        for code_dict in code_dict_list:
            if code_dict['form'].code.data in error_keys:
                code_dict['form'].add_coupon_response_error(error_list[code_dict['form'].code.data])

        return code_dict_list

    def use_sports_service_discount_code(self):
        success = True

        code_str_list = [code.code for code in discount_api.get_used_discount_codes(self.read_only_cart) if
                         code.discount_code_setting.issued_by == u'sports_service']
        code_dict_list = self.create_code_dict_list(code_str_list)

        if code_dict_list:
            settings = self.read_only_cart.performance.find_available_target_settings(
                issued_by=u'sports_service',
                max_price=self.read_only_cart.highest_item_price,
                session=self.session,
                now=self.now
            )
            result = discount_api.use_discount_codes(self.request, code_dict_list, settings)

            if not result or not result['status'] == u'OK':
                raise DiscountCodeConfirmError()

            coupons = result['coupons']
            for coupon in coupons:
                if coupon['reason_cd'] != u'1010' or coupon['available_flg'] != u'1':
                    logger.error(
                        "[ The response for order_no: {}] the discount code is not available.".format(
                            self.read_only_cart.order_no))
                    success = False

        return success

    def check_csrf(self):
        from . import schemas
        try:
            csrf_form = schemas.CSRFSecureForm(formdata=self.request.params, csrf_context=self.request.session)
            if not csrf_form.validate():
                logger.info('invalid csrf token: {0}'.format(csrf_form.errors))
                raise InvalidCSRFTokenException

            # セッションからCSRFトークンを削除して再利用不可にしておく
            if 'csrf' in self.request.session:
                del self.request.session['csrf']
                if hasattr(self.request.session, 'persist'):
                    self.request.session.persist()

        except (InvalidCSRFTokenException, NoCartError):
            # 不正な画面遷移
            raise NoCartError()


class CartBoundTicketingCartResource(DiscountCodeTicketingCartResources):
    def __init__(self, request):
        super(CartBoundTicketingCartResource, self).__init__(request)

    @reify
    def sales_segment(self):
        cart = cart_api.get_cart(self.request, for_update=False)
        if cart is None:
            raise NoSalesSegment(self.request, '', host_base_url=self.host_base_url)
        return cart.sales_segment

    @reify
    def performance(self):
        return self.sales_segment.performance

    @reify
    def event(self):
        return self.performance.event if self.performance is not None else None

    @reify
    def sales_segments(self):
        """現在認証済みのユーザとパフォーマンスに関連する全販売区分"""
        return [self.sales_segment] if self.sales_segment.applicable(user=self.authenticated_user(), type='all') else []


class CompleteViewTicketingCartResource(CartBoundTicketingCartResource):
    def __init__(self, request):
        super(CompleteViewTicketingCartResource, self).__init__(request)

    @reify
    def order_like(self):
        try:
            cart = self.read_only_cart
            return cart
        except NoCartError:
            try:
                order_no = cart_api.get_temporary_store(self.request).get(self.request)
                return cart_api.get_order_for_read_by_order_no(self.request, order_no)
            except TemporaryStoreError:
                logger.debug("could not retrieve temporary store", exc_info=True)
        return None

    @property
    def sales_segment(self):
        return self.order_like and self.order_like.sales_segment

    @property
    def performance(self):
        return self.sales_segment and self.sales_segment.performance

    @property
    def event(self):
        return self.performance and self.performance.event

    @reify
    def sales_segments(self):
        """現在認証済みのユーザとパフォーマンスに関連する全販売区分"""
        return [self.sales_segment]


class SwitchUAResource(object):
    def __init__(self, request):
        self.request = request

compat_ticketing_cart_resource_factory = EventOrientedTicketingCartResource

@implementer(IOrderDelivery)
class OrderDelivery(object):
    def __init__(self, order):
        self.order = order

@implementer(ICartDelivery)
class CartDelivery(object):
    def __init__(self, cart):
        self.cart = cart

@implementer(IOrderPayment)
class OrderPayment(object):
    def __init__(self, order):
        self.order = order

@implementer(ICartPayment)
class CartPayment(object):
    def __init__(self, cart):
        self.cart = cart
