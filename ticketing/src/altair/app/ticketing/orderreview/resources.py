# -*- coding:utf-8 -*-

import logging
import hashlib
from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta
from pyramid.decorator import reify
from pyramid.security import effective_principals, Allow, Authenticated, Deny, DENY_ALL
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import or_
import webhelpers.paginate as paginate
from altair.now import get_now
from altair.sqlahelper import get_db_session
from altair.app.ticketing.cart.api import get_auth_info
from altair.app.ticketing.payments import plugins
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.orders.models import Order
from altair.app.ticketing.core.models import SalesSegment, SalesSegmentSetting, ShippingAddress, Organization
from altair.app.ticketing.lots.models import LotEntry, Lot
from altair.app.ticketing.qr.lookup import lookup_qr_aes_plugin
from altair.app.ticketing.users.models import User, UserCredential, Membership, UserProfile
from altair.app.ticketing.resale.models import ResaleSegment
from altair.app.ticketing.discount_code.models import UsedDiscountCodeOrder
from altair.app.ticketing.core import api as core_api
from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.skidata.models import SkidataBarcode, SkidataBarcodeEmailHistory
from .views import unsuspicious_order_filter
from .schemas import OrderReviewSchema
from .exceptions import InvalidForm, OAuthRequiredSettingError
from .models import ReviewAuthorization
from . import helpers as h
from functools import partial
from operator import attrgetter

logger = logging.getLogger(__name__)


class DefaultResource(object):
    def __init__(self, request):
        self.request = request


class OrderReviewResourceBase(object):
    __acl__ = [
        (Deny, 'altair_guest', '*'),
        (Allow, Authenticated, '*'),
        DENY_ALL,
        ]

    def __init__(self, request):
        self.request = request
        self.session = get_db_session(request, name="slave")

    @reify
    def organization(self):
        return cart_api.get_organization(self.request)

    @reify
    def primary_membership(self):
        return self.session.query(Membership) \
            .filter_by(organization_id=self.organization.id) \
            .first()

    @reify
    def available_memberships(self):
        return self.session.query(Membership) \
            .filter_by(organization_id=self.organization.id) \
            .all()

    @reify
    def user_point_accounts(self):
        if not self.order:
            return None
        return self.order.user_point_accounts

    def authenticated_user(self):
        """現在認証中のユーザ"""
        return self.request.altair_auth_info

    @property
    def cart_setting(self):
        return self.organization.setting.cart_setting

    @property
    def request_auth_type(self):
        return self.request.params.get('auth_type') or self.cart_setting.auth_type

    # 今後複数認証を並行で使うことも想定してリストで返すことにする
    @property
    def oauth_service_providers(self):
        if 'oauth_service_provider' in self.request.params.keys():
            return [self.request.params['oauth_service_provider']]
        elif self.organization.setting.oauth_service_provider:
            return [self.organization.setting.oauth_service_provider]
        elif self.cart_setting.auth_type == u'altair.oauth_auth.plugin.OAuthAuthPlugin':
            return [self.cart_setting.oauth_service_provider]
        return []

    def _validate_required_oauth_params(self, params):
        # 必須項目が不足している場合は、アラートをあげるようにする
        if self.request_auth_type == u'altair.oauth_auth.plugin.OAuthAuthPlugin':
            if not (params['client_id'] and
                        params['client_secret'] and
                        params['endpoint_api'] and
                        params['endpoint_token'] and
                        params['endpoint_token_revocation'] and
                        params['endpoint_authz']):
                raise OAuthRequiredSettingError('required oauth setting is not specified.')

    @property
    def oauth_params(self):
        prompt = self.organization.setting.openid_prompt or self.cart_setting.openid_prompt
        # XXX: polluxの時はどの会員資格かは関係ないので会員資格選択画面を見せずに行きたい
        if self.organization.setting.oauth_service_provider == 'pollux':
            if 'select_account' in prompt:
                # XXX: prompt.removeを使うとDB updateが走ってしまう...
                prompt = [p for p in prompt if p != 'select_acount']
        # 基本的にはOrg設定から取ることを想定。fallbackとしてカート設定の値を使うようにしたけど...
        params = dict(
            client_id=self.organization.setting.oauth_client_id or self.cart_setting.oauth_client_id,
            client_secret=self.organization.setting.oauth_client_secret or self.cart_setting.oauth_client_secret,
            endpoint_api=self.organization.setting.oauth_endpoint_api or self.cart_setting.oauth_endpoint_api,
            endpoint_token=self.organization.setting.oauth_endpoint_token or self.cart_setting.oauth_endpoint_token,
            endpoint_token_revocation=self.organization.setting.oauth_endpoint_token_revocation or self.cart_setting.oauth_endpoint_token_revocation,
            scope=self.organization.setting.oauth_scope or self.cart_setting.oauth_scope,
            openid_prompt=prompt,
            endpoint_authz=self.organization.setting.oauth_endpoint_authz or self.cart_setting.oauth_endpoint_authz
        )
        try:
            self._validate_required_oauth_params(params)
        except OAuthRequiredSettingError as e:
            raise e
        return params


class LandingViewResource(OrderReviewResourceBase):
    pass


class MyPageListViewResource(OrderReviewResourceBase):
    def get_orders(self, user, page, per):
        if not user:
            return None

        if user.id is None:
            return None

        now = get_now(self.request)
        #disp_orderreviewは、マイページに表示するかしないかのフラグとなった
        orders = self.session.query(Order).join(SalesSegment, Order.sales_segment_id==SalesSegment.id). \
            join(SalesSegmentSetting, SalesSegment.id == SalesSegmentSetting.sales_segment_id). \
            outerjoin(LotEntry, Order.order_no == LotEntry.entry_no). \
            outerjoin(Lot, LotEntry.lot_id == Lot.id). \
            filter(Order.organization_id==self.organization.id). \
            filter(Order.user_id==user.id). \
            filter(SalesSegmentSetting.disp_orderreview==True). \
            filter(or_(Lot.lotting_announce_datetime <= now, Lot.lotting_announce_datetime == None)). \
            order_by(Order.updated_at.desc())
        orders = unsuspicious_order_filter(orders)  # refs 10883
        orders = paginate.Page(orders, page, per, url=paginate.PageURL_WebOb(self.request))
        return orders

    def get_lots_entries(self, user, page, per):
        if not user:
            return None

        entries = LotEntry.query.filter(
            LotEntry.user_id==user.id
        ).order_by(LotEntry.updated_at.desc())

        entries = unsuspicious_order_filter(entries)  # refs 10883
        entries = paginate.Page(entries, page, per, url=paginate.PageURL_WebOb(self.request))

        return entries


class OrderReviewResource(OrderReviewResourceBase):
    def __init__(self, request):
        super(OrderReviewResource, self).__init__(request)
        form = OrderReviewSchema(self.request.POST)
        _message = partial(h._message, request=request)
        if not form.validate():
            raise InvalidForm(form)
        order_no = form.order_no.data
        order = self.session.query(Order).join(SalesSegment, Order.sales_segment_id==SalesSegment.id). \
            join(SalesSegmentSetting, SalesSegment.id == SalesSegmentSetting.sales_segment_id). \
            filter(Order.organization_id==self.organization.id). \
            filter(Order.order_no==order_no).first()
        logger.info("organization_id=%s, order_no=%s, order=%s" % (self.organization.id, order_no, order))
        if order is None:
            raise InvalidForm(form, errors=[_message(u'受付番号または電話番号が違います。')])
        tel = form.tel.data
        if not order.shipping_address or tel not in [_tel.replace('-', '') for _tel in order.shipping_address.tels]:
            raise InvalidForm(form, errors=[_message(u'受付番号または電話番号が違います。')])
        if order.payment_delivery_pair.delivery_method.delivery_plugin_id == plugins.ORION_DELIVERY_PLUGIN_ID and \
           (order.performance is None or order.performance.orion is None):
            logger.warn("Performance %s has not OrionPerformance." % order.performance.code)
        self.form = form
        self.order = order

    @reify
    def cart_setting(self):
        return self.order.cart_setting

    def order_detail_panel(self, order, locale=None):
        if self.request.organization.setting.enable_skidata and \
                order.delivery_plugin_id == plugins.SKIDATA_QR_DELIVERY_PLUGIN_ID:
            panel_name = 'order_detail.qr_ticket'
        else:
            panel_name = 'order_detail.%s' % self.cart_setting.type
        return self.request.layout_manager.render_panel(panel_name, self.order, self.user_point_accounts, locale)


class MyPageOrderReviewResource(OrderReviewResourceBase):
    def __init__(self, request):
        super(MyPageOrderReviewResource, self).__init__(request)
        order_no = self.request.params.get('order_no', None)
        order = self.session.query(Order).join(SalesSegment, Order.sales_segment_id==SalesSegment.id). \
            join(SalesSegmentSetting, SalesSegment.id == SalesSegmentSetting.sales_segment_id). \
            filter(Order.organization_id==self.organization.id). \
            filter(Order.order_no==order_no).first()
        logger.info("organization_id=%s, order_no=%s, order=%s" % (self.organization.id, order_no, order))
        if order is None:
            raise HTTPFound(location=self.request.route_url('mypage.show'))
        if order.payment_delivery_pair.delivery_method.delivery_plugin_id == plugins.ORION_DELIVERY_PLUGIN_ID and \
           (order.performance is None or order.performance.orion is None):
            logger.warn("Performance %s has not OrionPerformance." % order.performance.code)
        self.order = order
        authenticated_user = self.authenticated_user()
        user = cart_api.get_user(authenticated_user)
        if user is None or self.order.user_id != user.id:
            raise HTTPNotFound()

    @reify
    def cart_setting(self):
        return self.order.cart_setting

    def order_detail_panel(self, order, locale=None):
        if self.request.organization.setting.enable_skidata and \
                order.delivery_plugin_id == plugins.SKIDATA_QR_DELIVERY_PLUGIN_ID:
            panel_name = 'order_detail.qr_ticket'
        else:
            panel_name = 'order_detail.%s' % self.cart_setting.type
        return self.request.layout_manager.render_panel(panel_name, self.order, self.user_point_accounts, locale)


class MyPageResource(OrderReviewResourceBase):
    pass


class QRViewResource(OrderReviewResourceBase):
    pass


class EventGateViewResource(OrderReviewResourceBase):
    pass


class ContactViewResource(OrderReviewResourceBase):
    pass


class ReviewPasswordInfoViewResource(OrderReviewResourceBase):
    def get_review_authorization(self, email, review_password, type):
        query = ReviewAuthorization.query \
            .with_entities(ReviewAuthorization.order_no) \
            .filter(ReviewAuthorization.email == email) \
            .filter(ReviewAuthorization.review_password == hashlib.md5(review_password).hexdigest()) \
            .filter(ReviewAuthorization.type == type) \
            .filter(ReviewAuthorization.deleted_at == None)

        return query

    def get_review_password_orders(self, order_no, page, paginate_by):
        now = get_now(self.request)
        orders = self.session.query(Order) \
            .join(ShippingAddress, ShippingAddress.id == Order.shipping_address_id) \
            .filter(Order.order_no.in_(order_no)) \
            .filter(Order.created_at >= (now + relativedelta(years=-1))) \
            .filter(Order.deleted_at == None) \
            .order_by(Order.created_at.desc())

        orders = unsuspicious_order_filter(orders)  # refs 10883
        orders = paginate.Page(orders, page, paginate_by, url=paginate.PageURL_WebOb(self.request))
        return orders

    def get_review_password_lots_entries(self, entry_no, page, paginate_by):
        now = get_now(self.request)
        entries = self.session.query(LotEntry) \
            .join(ShippingAddress, ShippingAddress.id == LotEntry.shipping_address_id) \
            .filter(LotEntry.entry_no.in_(entry_no)) \
            .filter(LotEntry.created_at >= (now + relativedelta(years=-1))) \
            .filter(LotEntry.deleted_at == None) \
            .order_by(LotEntry.created_at.desc())

        entries = unsuspicious_order_filter(entries)  # refs 10883
        entries = paginate.Page(entries, page, paginate_by, url=paginate.PageURL_WebOb(self.request))
        return entries


class ReceiptViewResource(OrderReviewResourceBase):
    def __init__(self, request):
        super(ReceiptViewResource, self).__init__(request)
        order_no = request.params.get('order_no', None)
        self.order = self.session.query(Order). \
            filter(Order.organization_id == self.organization.id). \
            filter(Order.deleted_at.is_(None)). \
            filter(Order.canceled_at.is_(None)). \
            filter(Order.order_no == order_no).first()
        logger.info("organization_id=%s, order_no=%s, order=%s obtained in ReceiptViewResource." % (self.organization.id, order_no, self.order))
        if not self.order:
            raise HTTPNotFound()


class QRAESViewResource(OrderReviewResourceBase):
    def __init__(self, request):
        super(QRAESViewResource, self).__init__(request)
        self.qr_aes_plugin = lookup_qr_aes_plugin(request, self.organization.code)


class QRTicketViewResource(OrderReviewResourceBase):
    def __init__(self, request):
        super(QRTicketViewResource, self).__init__(request)
        self.session = get_db_session(request, name="slave")
        self.barcode_id = self.request.matchdict.get('barcode_id')
        if self.barcode_id is None:  # Noneの場合はPOSTのとき
            self.barcode_id = self.request.POST.get('barcode_id')
        self.hash = self.request.matchdict.get('hash')
        if self.hash is None:  # Noneの場合はPOSTのとき
            self.hash = self.request.POST.get('hash')
        if self.request.POST.get('barcode_and_hash'):  # チケット一覧からリクエストされたパターン
            _barcode_id, _hash = self.request.POST.get('barcode_and_hash').split('_')
            self.barcode_id = _barcode_id
            self.hash = _hash

    @reify
    def skidata_barcode(self):
        return SkidataBarcode.find_by_id(self.barcode_id, self.session)

    @reify
    def order(self):
        return self.skidata_barcode.ordered_product_item_token.item.ordered_product.order

    @reify
    def performance(self):
        return self.order.performance

    @reify
    def product_item(self):
        return self.skidata_barcode.ordered_product_item_token.item.product_item

    @reify
    def seat(self):
        return self.skidata_barcode.ordered_product_item_token.seat

    @reify
    def stock_type(self):
        return self.skidata_barcode.ordered_product_item_token.item.ordered_product.product.seat_stock_type

    @reify
    def skidata_barcode_email_history_list_sorted(self):
        return self.skidata_barcode.emails

    @reify
    def resale_request(self):
        return self.skidata_barcode.ordered_product_item_token.resale_request

    @reify
    def product(self):
        return self.product_item.product

    @reify
    def resale_segment(self):
        return self.session.query(ResaleSegment)\
            .filter(ResaleSegment.performance_id == self.performance.id)\
            .filter(ResaleSegment.deleted_at.is_(None)).first()

    @reify
    def is_enable_resale(self):
        if self.order.sales_segment.setting.use_default_enable_resale:
            # 販売区分グループの設定値を使用する場合
            return self.organization.setting.enable_resale and \
                   self.order.sales_segment.sales_segment_group.setting.enable_resale
        else:
            # 販売区分の設定値を使用する場合
            return self.organization.setting.enable_resale and \
                   self.order.sales_segment.setting.enable_resale

    @reify
    def is_enable_discount_code(self):
        if self.organization.setting.enable_discount_code:
            sb_token_id = self.skidata_barcode.ordered_product_item_token.id
            return self.session.query(UsedDiscountCodeOrder) \
                .filter(UsedDiscountCodeOrder.ordered_product_item_token_id == sb_token_id)\
                .filter(UsedDiscountCodeOrder.canceled_at.is_(None))\
                .filter(UsedDiscountCodeOrder.refunded_at.is_(None))\
                .filter(UsedDiscountCodeOrder.deleted_at.is_(None)).first()
        return None


class MyPageQRTicketResource(QRTicketViewResource):
    def __init__(self, request):
        super(MyPageQRTicketResource, self).__init__(request)

        authenticated_user = self.authenticated_user()
        user = cart_api.get_user(authenticated_user)
        if user is None or self.order.user_id != user.id:
            raise HTTPNotFound()
