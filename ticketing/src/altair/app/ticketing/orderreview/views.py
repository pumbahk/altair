# -*- coding:utf-8 -*-
import logging
import sqlahelper
import webhelpers.paginate as paginate
import json
import StringIO
import hashlib
from datetime import datetime
from collections import namedtuple

from wtforms.validators import ValidationError
from altair.oauth_auth.exceptions import OAuthAPICommunicationError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.sql.expression import or_, and_

from pyramid.view import view_defaults
from pyramid.request import Request
from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.decorator import reify
from pyramid.interfaces import IRouteRequest, IRequest
from pyramid.security import forget
from pyramid.renderers import render_to_response
from pyramid.session import check_csrf_token

from altair.auth.api import get_who_api
from altair.rakuten_auth.api import get_rakuten_id_api2_factory
from altair.mobile.api import is_mobile_request
from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.app.ticketing.core.api import get_default_contact_url
from altair.request.adapters import UnicodeMultiDictAdapter
from altair.sqlahelper import get_db_session
from altair.now import get_now, is_now_set

from altair.app.ticketing.core.models import ShippingAddress, OrderreviewIndexEnum, OrionTicketPhone
from altair.app.ticketing.core.utils import IssuedAtBubblingSetter
from altair.app.ticketing.mailmags.api import get_magazines_to_subscribe, multi_subscribe, multi_unsubscribe
from altair.app.ticketing.payments import plugins

from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.cart.rendering import selectable_renderer
from altair.app.ticketing.cart.view_support import filter_extra_form_schema, get_extra_form_schema, render_view_to_response_with_derived_request, render_display_value
from altair.app.ticketing.api.impl import CMSCommunicationApi
from altair.app.ticketing.qr.image import qrdata_as_image_response
from altair.app.ticketing.qr.utils import build_qr_by_history_id, build_qr_by_token_id, build_qr_by_orion, get_matched_token_from_token_id, build_qr_by_order
from altair.app.ticketing.fc_auth.api import do_authenticate
from altair.app.ticketing.orders.models import Order, OrderedProduct, OrderedProductItem, OrderedProductItemToken, OrderReceipt
from altair.app.ticketing.orders.api import OrderAttributeIO, get_extra_form_fields_for_order, get_order_by_order_no
from altair.app.ticketing.lots.models import LotEntry
from altair.app.ticketing.users.models import User, WordSubscription, UserProfile
from altair.app.ticketing.users.word import get_word

from altair.app.ticketing.skidata.models import SkidataBarcode, SkidataBarcodeEmailHistory
from altair.app.ticketing.skidata.utils import write_qr_image_to_stream, get_hash_from_barcode_data

from altair.app.ticketing.payments.plugins import SKIDATA_QR_DELIVERY_PLUGIN_ID
from altair.app.ticketing.skidata.utils import write_qr_image_to_stream

from .api import is_mypage_organization, is_rakuten_auth_organization
from . import schemas
from . import api
from . import helpers as h
from .exceptions import InvalidForm, QRTicketUnpaidException, QRTicketOutOfIssuingStartException, QRTicketCanceledException, QRTicketRefundedException
from .models import ReviewAuthorizationTypeEnum
from pyramid.settings import aslist

import urllib
import urllib2
import contextlib
import re
from functools import partial

from altair.app.ticketing.i18n import custom_locale_negotiator

import altair.pgw.api as pgw_api


def jump_maintenance_page_om_for_trouble(organization):
    """https://redmine.ticketstar.jp/issues/10878
    誤表示問題の時に使用していたコード
    有効にしたら、指定したORGだけ公開し、それ以外をメンテナンス画面に飛ばす
    """
    return
    #if organization is None or organization.code not in ['KE', 'RT', 'CR', 'KT', 'TH', 'TC', 'PC', 'SC', 'YT', 'OG', 'JC', 'NH', '89', 'VS', 'IB', 'FC', 'TG', 'BT', 'LS', 'BA', 'VV', 'KH', 'VK', 'RE','TS', 'RK']:
    #    raise HTTPFound('/maintenance.html')


logger = logging.getLogger(__name__)

DBSession = sqlahelper.get_session()


suspicious_start_dt = datetime(2015, 2, 14, 20, 30)  # https://redmine.ticketstar.jp/issues/10873 で問題が発生しだしたと思われる30分前
suspicious_end_dt = datetime(2015, 2, 15, 2, 0)  # https://redmine.ticketstar.jp/issues/10873 で問題が収束したと思われる1時間

FakeTicketPrintHistory = namedtuple('FakeTicketPrintHistory', ['id', 'item_token', 'item_token_id', 'performance', 'order', 'order_no', 'ordered_product_item', 'ordered_product_item_id', 'order_id', 'seat'])


def is_suspicious_order(orderlike):
    """https://redmine.ticketstar.jp/issues/10873 の問題の影響を受けている可能性があるかを判定
    https://redmine.ticketstar.jp/issues/10883
    """
    return suspicious_start_dt <= orderlike.created_at <= suspicious_end_dt


def unsuspicious_order_filter(orderlikes):
    """https://redmine.ticketstar.jp/issues/10873 の問題の影響を受けている可能性があるもを取り除く
    https://redmine.ticketstar.jp/issues/10883
    """
    return [orderlike for orderlike in orderlikes if not is_suspicious_order(orderlike)]


def jump_infomation_page_om_for_10873(orderlike):
    """https://redmine.ticketstar.jp/issues/10873 の問題の影響を受けている可能性があるもはinfomationページにリダイレクトさせる
    """
    if is_suspicious_order(orderlike):
        raise HTTPFound('/orderreview/information')

@lbr_view_config(
    route_name='mypage.autologin',
    request_method="POST"
    )
def autologin(request):
    from altair.auth.api import get_auth_api
    auth_api = get_auth_api(request)
    #identities, auth_factors, metadata = auth_api.login(
    #    request,
    #    request.response,
    #    credentials={ },
    #    auth_factor_provider_name="rakuten"
    #    )
    #identity = identities.get("rakuten")
    access_token = request.params.get("access_token", "")
    if access_token != "":
        idapi = get_rakuten_id_api2_factory(request)(request, access_token)
        open_id = idapi.get_open_id()
        auth_factors = {'pyramid_session:altair.auth.pyramid': {'claimed_id': open_id, 'oauth2_access_token': access_token}}
        auth_api.remember(request, request.response, auth_factors)

        authenticated_user = request.altair_auth_info
        user = cart_api.get_or_create_user(authenticated_user)

        if user is not None:
            path = request.params.get("next", "/orderreview/mypage")
            # nextのチェックがad hocky...
            if ':' in path or '//' in path:
                path = "/orderreview/mypage"
            return HTTPFound(path)


def override_auth_type(context, request):
    if 'auth_type' in request.params:
        request.session['orderreview_auth_type_override'] = request.params['auth_type']
    return True


@view_defaults(
    custom_predicates=(is_mypage_organization, ),
    permission='*'
    )
class MypageView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    # これは UserProfile であるべきではないのか??
    def get_shipping_address(self, user):
        shipping_address = self.context.session.query(ShippingAddress).filter(
            ShippingAddress.user_id==user.id
        ).order_by(ShippingAddress.updated_at.desc()).first()
        return shipping_address

    @lbr_view_config(
        route_name='mypage.show',
        request_method="GET",
        custom_predicates=(override_auth_type,),
        renderer=selectable_renderer("mypage/show.html")
        )
    def show(self):
        jump_maintenance_page_om_for_trouble(self.request.organization)

        authenticated_user = self.context.authenticated_user()
        user = cart_api.get_or_create_user(authenticated_user)

        DBSession.flush()
        DBSession.refresh(user)

        if user is None or user.id is None:
            raise Exception("get_or_create_user() failed in orderreview")

        per = 10

        shipping_address = self.get_shipping_address(user)

        page = self.request.params.get("page", 1)
        orders = self.context.get_orders(user, page, per)
        entries = self.context.get_lots_entries(user, page, per)

        magazines_to_subscribe = None
        if shipping_address:
            magazines_to_subscribe = get_magazines_to_subscribe(
                cart_api.get_organization(self.request),
                shipping_address.emails
                )

        word_enabled = self.request.organization.setting.enable_word == 1
        subscribe_word = False
        if word_enabled:
            profile = UserProfile.query.filter(UserProfile.user_id==user.id).first()
            if profile is not None and profile.subscribe_word:
                subscribe_word = True

        return dict(
            shipping_address=shipping_address,
            orders=orders,
            lot_entries=entries,
            mailmagazines_to_subscribe=magazines_to_subscribe,
            h=h,
            word_enabled=word_enabled,
            subscribe=subscribe_word,
        )

    @lbr_view_config(
        route_name='mypage.order.show',
        renderer=selectable_renderer("mypage/order_show.html"),
        permission='*'
        )
    def order_show(self):
        order = self.context.order
        jump_infomation_page_om_for_10873(order)  # refs 10883
        return dict(order=self.context.order)

    @lbr_view_config(
        route_name='mypage.mailmag.confirm',
        request_method="POST",
        renderer=selectable_renderer("mypage/mailmag_confirm.html")
        )
    def mailmag_confirm(self):
        authenticated_user = self.context.authenticated_user()
        user = cart_api.get_user(authenticated_user)

        if not user:
            raise HTTPNotFound()

        shipping_address = self.get_shipping_address(user)
        magazines_to_subscribe = get_magazines_to_subscribe(
            cart_api.get_organization(self.request),
            shipping_address.emails
            )
        subscribe_ids = self.request.params.getall('mailmagazine')

        return dict(
            mails=shipping_address.emails,
            mailmagazines_to_subscribe=magazines_to_subscribe,
            subscribe_ids=subscribe_ids,
            h=h,
        )

    @lbr_view_config(
        route_name='mypage.mailmag.complete',
        request_method="POST",
        renderer=selectable_renderer("mypage/mailmag_complete.html")
        )
    def mailmag_complete(self):
        authenticated_user = self.context.authenticated_user()
        user = cart_api.get_user(authenticated_user)

        if not user:
            raise HTTPNotFound()

        shipping_address = self.get_shipping_address(user)
        magazines_to_subscribe = get_magazines_to_subscribe(
            cart_api.get_organization(self.request),
            shipping_address.emails
            )
        emails = shipping_address.emails
        subscribe_ids = self.request.params.getall('mailmagazine')

        unsubscribe_ids = []
        for mailmagazine, subscribed in magazines_to_subscribe:
            if not str(mailmagazine.id) in subscribe_ids:
                unsubscribe_ids.append(mailmagazine.id)

        multi_subscribe(user, emails, subscribe_ids)
        multi_unsubscribe(user, emails, unsubscribe_ids)

        return dict(
        )

    @lbr_view_config(route_name="mypage.logout")
    def logout(self):
        return_to = self.request.params.get('return_to', '')
        if not return_to.startswith('/'):
            return_to = None
        if return_to is None:
            return_to = self.request.route_path('order_review.index')
        try:
            headers = forget(self.request)
        except OAuthAPICommunicationError:
            logger.info('Access token has been already revoked.')
            headers = [('Content-Type', 'text/html; charset=UTF-8')]
        return HTTPFound(location=return_to, headers=headers)


class OrderReviewView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(
        route_name='order_review.index',
        renderer=selectable_renderer("order_review/index.html")
        )
    def index(self):

        jump_maintenance_page_om_for_trouble(self.request.organization)
        orderreview_index = self.request.organization.setting.orderreview_index
        form = schemas.OrderReviewSchema(self.request.params)

        # orderreview_indexがindex.html以外を指定している場合はそれぞれのログイン画面を表示する
        # /orderreviewのHTTPレスポンスは200で返す必要があるのでリダイレクトはNG (監視要件)
        if orderreview_index == OrderreviewIndexEnum.OrderNo.v[0]:
            form_template = self.request.view_context.get_template_path("order_review/form.html")
            return render_to_response(form_template, {"form": form, "view_context": self.request.view_context}, request = self.request)

        elif orderreview_index == OrderreviewIndexEnum.FcAuth.v[0]:
            # 認証方法がfc_authの場合のみ、fc_authログイン画面を表示する。
            # fc_auth以外のケースはorderreview_indexの値がfc_authを指していてもindex.htmlを表示する
            if cart_api.is_fc_auth_organization(self.context, self.request):
                fc_auth_template = self.request.view_context.get_fc_login_template()

                # fc_auth_templateがない場合もindex.htmlを表示する
                if fc_auth_template is not None:
                    return render_to_response(fc_auth_template, dict(view_context=self.request.view_context), request=self.request)

        return {"form": form}

    @lbr_view_config(route_name='order_review.guest')
    def guest(self):
        jump_maintenance_page_om_for_trouble(self.request.organization)
        return HTTPFound(location=self.request.route_path("order_review.form"))

    @lbr_view_config(
        route_name='order_review.login',
        renderer=selectable_renderer("order_review/login.html")
    )
    def login(self):
        jump_maintenance_page_om_for_trouble(self.request.organization)
        form = schemas.OrderReviewSchema(self.request.params)

        return {"form": form}


@view_defaults(renderer=selectable_renderer("order_review/form.html"))
class OrderReviewFormView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(route_name='order_review.form')
    def form(self):
        jump_maintenance_page_om_for_trouble(self.request.organization)
        form = schemas.OrderReviewSchema(self.request.params)
        return {"form": form}

    @lbr_view_config(route_name='order_review.form2')
    def form2(self):
        return HTTPFound(self.request.route_path('order_review.form'))

    @lbr_view_config(context=InvalidForm)
    def exc(self):
        form = self.context.form
        order_no_errors = list(form.order_no.errors)
        order_no_errors.extend(self.context.errors)
        form.order_no.errors = order_no_errors
        return {"form": form}


@view_defaults(route_name='order_review.show', renderer=selectable_renderer("order_review/show.html"), request_method='POST')
class OrderReviewShowView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._message = partial(h._message, request=self.request)

    @lbr_view_config(
        route_name='order_review.show',
        request_method="POST",
        renderer=selectable_renderer("order_review/show.html")
        )
    def post(self):
        form = schemas.OrderReviewSchema(self.request.params)
        if not form.validate():
            raise InvalidForm(form)
        order = self.context.order
        jump_infomation_page_om_for_10873(order)  # refs 10873
        announce_datetime = None

        now = get_now(self.request)

        # 抽選発表予定日のチェック
        if order is not None:
            lot_entry = LotEntry.query.filter_by(entry_no=order.order_no).first()
            if lot_entry is not None:
                announce_datetime = lot_entry.lot.lotting_announce_datetime
        if announce_datetime is not None:
            if announce_datetime > now:
                raise InvalidForm(form, [self._message(u'受付番号または電話番号が違います。')])

        if order is None or order.shipping_address is None:
            raise InvalidForm(form, [self._message(u'受付番号または電話番号が違います。')])

        return dict(order=order,
                    locale=custom_locale_negotiator(self.request) if self.request.organization.setting.i18n else "", )


@view_defaults(renderer=selectable_renderer("order_review/edit_order_attributes.html"), request_method='POST')
class OrderAttributesEditView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @reify
    def _predefined_symbols(self):
        performance = self.context.order.performance
        if performance is not None:
            performance_start_on = performance.start_on
            performance_end_on = performance.end_on or performance.start_on
        else:
            performance_start_on = None
            performance_end_on = None
        retval = {
            'PERFORMANCE_START': performance_start_on,
            'PERFORMANCE_END': performance_end_on,
            'ORDERED': self.context.order.created_at,
            'ISSUED': self.context.order.issued_at,
            'PAID': self.context.order.paid_at,
            'CANCELED': self.context.order.canceled_at,
            'REFUNDED': self.context.order.refunded_at,
            }

        if is_now_set(self.request):
            from altair.dynpredicate.core import Node
            now = get_now(self.request)
            retval['NOW'] = Node(
                type='CALL',
                line=0,
                column=0,
                children=(
                    Node(
                        type='SYM',
                        line=0,
                        column=0,
                        value='DATE',
                        ),
                    Node(
                        type='TUPLE',
                        line=0,
                        column=0,
                        children=(
                            Node(type='NUM', line=0, column=0, value=now.year),
                            Node(type='NUM', line=0, column=0, value=now.month),
                            Node(type='NUM', line=0, column=0, value=now.day),
                            Node(type='NUM', line=0, column=0, value=now.hour),
                            Node(type='NUM', line=0, column=0, value=now.minute),
                            Node(type='NUM', line=0, column=0, value=now.second)
                            )
                        )
                    )
                )
        return retval

    def create_form(self, formdata=None, data=None):
        mode = ['orderreview', 'editable']
        order = self.context.order
        data = {
            entry[0]: entry[2]
            for entry in OrderAttributeIO(mode=mode).marshal(self.request, order)
            }
        extra_form_field_descs = get_extra_form_fields_for_order(self.request, order)
        form, form_fields = schemas.build_dynamic_form(
            self.request,
            filter_extra_form_schema(extra_form_field_descs, mode=mode),
            _dynswitch_predefined_symbols=self._predefined_symbols,
            formdata=formdata,
            _data=data,
            csrf_context=self.request
            )
        # retouch form_fields
        for form_field in form_fields:
            field_desc = form_field['descriptor']
            form_field['old_display_value'] = render_display_value(self.request, field_desc, data.get(field_desc['name'])) if data is not None else u''
        return form, form_fields

    @lbr_view_config(route_name='order_review.edit_order_attributes.form')
    def form(self):
        # 抽選から当選処理で作られた予約についてサポートできていないので修正しないといけない
        form, form_fields = self.create_form(formdata=None)
        return dict(order=self.context.order, form=form, form_fields=form_fields)

    def render_show_view(self):
        return render_view_to_response_with_derived_request(
            context_factory=lambda request:self.context,
            request=self.request,
            route=('order_review.show', {})
            )

    @lbr_view_config(route_name='order_review.edit_order_attributes.update', request_param='do_cancel')
    def cancel(self):
        return self.render_show_view()

    @lbr_view_config(route_name='order_review.edit_order_attributes.update', request_param='do_update')
    def update(self):
        form, form_fields = self.create_form(formdata=UnicodeMultiDictAdapter(self.request.params, 'utf-8', 'replace'))
        if not form.validate():
            if len(form.csrf.errors) > 0:
                return self.cancel()
            else:
                return dict(order=self.context.order, form=form, form_fields=form_fields)
        # context.order は slave のやつなので書き込みできない
        from altair.app.ticketing.models import DBSession
        writable_order = DBSession.query(Order).filter_by(id=self.context.order.id).one()
        updated_attributes = {
            k: form.data[k]
            for k in (form_field['descriptor']['name'] for form_field in form_fields if form_field['descriptor'].get('edit_in_orderreview', False))
            }
        writable_order.attributes.update(cart_api.coerce_extra_form_data(self.request, updated_attributes))
        # writable_order と self.context.order は別セッションのため、このタイミングでは同期していない。
        # 強制的に上書きして render_show_view() に備える
        self.context.order = writable_order
        return self.render_show_view()


@lbr_view_config(
    context=StandardError,
    renderer=selectable_renderer("errors/error.html")
    )
def exception_view(context, request):
    logger.error("The error was: %s" % context, exc_info=request.exc_info)
    return dict()


@lbr_view_config(
    context=HTTPNotFound,
    renderer=selectable_renderer("errors/not_found.html")
    )
def notfound_view(context, request):
    return dict()


@lbr_view_config(
    route_name='rakuten_auth.error',
    renderer=selectable_renderer("errors/error.html")
    )
def rakuten_auth_error(context, request):
    return dict()


@lbr_view_config(
    context=QRTicketUnpaidException,
    renderer=selectable_renderer("errors/unpaid_qr_ticket.html")
    )
def qr_ticket_unpaid_view(context, request):
    """
    QRチケット表示画面にて未入金の場合のエラー画面を表示

    :param context: resourceオブジェクト
    :param request: リクエストオブジェクト
    :return: 空dict(templateへのデータなし)
    """
    return dict()

@lbr_view_config(
    context=QRTicketOutOfIssuingStartException,
    renderer=selectable_renderer("errors/out_of_issuing_start_qr_ticket.html")
    )
def qr_ticket_out_of_issuing_start_view(context, request):
    """
    QRチケット表示画面にて発券開始前の場合のエラー画面を表示

    :param context: resourceオブジェクト
    :param request: リクエストオブジェクト
    :return: 空dict(templateへのデータなし)
    """
    return dict()


@lbr_view_config(
    context=QRTicketCanceledException,
    renderer=selectable_renderer("errors/canceled_qr_ticket.html")
    )
def qr_ticket_canceled_view(context, request):
    """
    QRチケット表示画面にて予約がキャンセルされた場合のエラー画面を表示

    :param context: resourceオブジェクト
    :param request: リクエストオブジェクト
    :return: 空dict(templateへのデータなし)
    """
    return dict()


@lbr_view_config(
    context=QRTicketRefundedException,
    renderer=selectable_renderer("errors/refunded_qr_ticket.html")
    )
def qr_ticket_refunded_view(context, request):
    """
    QRチケット表示画面にて予約が払戻済の場合のエラー画面を表示

    :param context: resourceオブジェクト
    :param request: リクエストオブジェクト
    :return: 空dict(templateへのデータなし)
    """
    return dict()


@lbr_view_config(
    route_name="contact",
    renderer=selectable_renderer("contact.html")
    )
def contact_view(context, request):
    return HTTPFound(cart_api.safe_get_contact_url(request, default=request.route_path("order_review.form")))


@lbr_view_config(
    route_name="order_review.information",
    renderer=selectable_renderer("information.html")
    )
def information_view(context, request):
    """お問い合わせページ
    https://redmine.ticketstar.jp/issues/10883
    """
    infomation_tel = '0800-808-0010'
    return dict(
        request=request,
        infomation_tel=infomation_tel,
        )

@lbr_view_config(
    route_name="order_review.receipt",
    renderer=selectable_renderer("order_review/receipt.html")
    )
def receipt_view(context, request):
    now = datetime.now()
    order = context.order
    receipt_address = request.params.get('receipt_address', '')
    receipt_provision = request.params.get('receipt_provision', '')

    try:
        receipt = DBSession.query(OrderReceipt).filter_by(order_id=order.id).one()
    except NoResultFound:
        receipt = None
    except MultipleResultsFound:
        raise HTTPNotFound()

    if not receipt:
        receipt = OrderReceipt()
        receipt.order_id = order.id
        receipt.updated_at = now
        receipt.created_at = now
        DBSession.add(receipt)

    issuable = receipt.is_issuable
    if issuable:
        receipt.issued_at = now
        DBSession.merge(receipt)

    DBSession.flush()
    return dict(
        issuable=issuable,
        now=now,
        order=order,
        receipt_address=receipt_address,
        receipt_provision=receipt_provision
        )

class QRView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(
        route_name='order_review.qr_confirm',
        renderer=selectable_renderer("order_review/qr_confirm.html"))
    def qr_confirm(self):
        ticket_id = int(self.request.matchdict.get('ticket_id', 0))
        sign = self.request.matchdict.get('sign', 0)

        ticket = build_qr_by_history_id(self.request, ticket_id)

        if ticket == None or ticket.sign != sign:
            raise HTTPNotFound()

        ordered_product_items = None
        # 一括の場合はticketがproductの情報を持たない。
        if not ticket.product:
            ordered_product_items = [element for item in ticket.order.items for element in item.elements]

        return dict(
            sign = sign,
            order = ticket.order,
            ticket = ticket,
            performance = ticket.performance,
            event = ticket.event,
            product = ticket.product,
            ordered_product_items = ordered_product_items,
            locale=custom_locale_negotiator(self.request) if self.request.organization.setting.i18n else ""
            )

    @lbr_view_config(
        route_name='order_review.qr',
        renderer=selectable_renderer("order_review/qr.html"))
    def qr_html(self):
        ticket_id = int(self.request.matchdict.get('ticket_id', 0))
        sign = self.request.matchdict.get('sign', 0)

        ticket = build_qr_by_history_id(self.request, ticket_id)

        ordered_product_items = None

        if ticket is None or ticket.sign != sign:
            raise HTTPNotFound()

        # 一括の場合はticketがproductの情報を持たない。
        if not ticket.product:
            ordered_product_items = [element for item in ticket.order.items for element in item.elements]

        if ticket.seat is None:
            gate = None
        else:
            gate = ticket.seat.attributes.get("gate", None)

        return dict(
            token = ticket.item_token and ticket.item_token.id, # dummy
            serial = ticket_id,           # dummy
            sign = sign,
            order = ticket.order,
            ticket = ticket,
            performance = ticket.performance,
            event = ticket.event,
            product = ticket.product,
            ordered_product_items = ordered_product_items,
            gate = gate,
            locale=custom_locale_negotiator(self.request) if self.request.organization.setting.i18n else ""
        )


    @lbr_view_config(
        route_name='order_review.orion_draw',
        xhr=False
        )
    def orion_image(self):
        token = int(self.request.matchdict.get('token', 0))
        serial = self.request.matchdict.get('serial', 0)
        sign = self.request.matchdict.get('sign', 0)

        data = OrderedProductItemToken.filter_by(id = token).first()
        if data is None:
            return HTTPNotFound()

        ticket = FakeTicketPrintHistory(
            id=serial,
            item_token=data,
            item_token_id=data.id,
            performance=data.item.ordered_product.order.performance,
            ordered_product_item=data.item,
            ordered_product_item_id=data.item.id,
            order=data.item.ordered_product.order,
            order_no=data.item.ordered_product.order.order_no,
            order_id=data.item.ordered_product.order.id,
            seat=data.seat
            )
        qr = build_qr_by_orion(self.request, ticket, serial)

        if sign == qr.sign:
            return qrdata_as_image_response(qr)
        else:
            return HTTPNotFound()

    @lbr_view_config(
        route_name='order_review.qrdraw',
        xhr=False
        )
    def qr_image(self):
        ticket_id = int(self.request.matchdict.get('ticket_id', 0))
        sign = self.request.matchdict.get('sign', 0)

        ticket = build_qr_by_history_id(self.request, ticket_id)
        if ticket is None:
            raise HTTPNotFound()

        if ticket.order.payment_delivery_pair.delivery_method.delivery_plugin_id == plugins.ORION_DELIVERY_PLUGIN_ID:
            # this block is not used, to be deleted.
            # orion
            try:
                response = api.send_to_orion(self.request, self.context, None, ticket.item_token)
                if response['result'] == u"OK" and response.has_key('serial'):
                    qr = build_qr_by_orion(self.request, ticket, response['serial'])
                    return qrdata_as_image_response(qr)

                ## エラーメッセージ
                if response.has_key('message'):
                    r = Response(status=500, content_type="text/html; charset=UTF-8")
                    r.text = response['message']
                    return r
            except Exception, e:
                logger.error(e.message, exc_info=1)
                raise e

        else:
            if ticket == None or ticket.sign != sign:
                raise HTTPNotFound()
            return qrdata_as_image_response(ticket)

    @lbr_view_config(
        route_name='order_review.qr_print',
        request_method='POST',
        renderer=selectable_renderer("order_review/qr.html")
        )
    def order_review_qr_print(self):
        if 'order_no' not in self.request.params:
            return HTTPFound(self.request.route_path("order_review.index"))
        if 'token' not in self.request.params:
            return HTTPFound(self.request.route_path("order_review.index"))

        order_no = self.request.params['order_no']
        token_id = self.request.params['token']
        if token_id:
            token = get_matched_token_from_token_id(order_no, token_id)

            if token.seat is None:
                gate = None
            else:
                gate = token.seat.attributes.get("gate", None)

            if token.item.ordered_product.order.payment_delivery_pair.delivery_method.delivery_plugin_id == plugins.ORION_DELIVERY_PLUGIN_ID:
                # orion
                try:
                    if token.item.ordered_product.order.order_no != self.request.params['order_no']:
                        raise Exception(u"Wrong order number or token: (%s, %s)" % (self.request.params['order_no'], self.request.params['token']))
                    response = api.send_to_orion(self.request, self.context, None, token)
                except Exception, e:
                    logger.exception(e)
                    ## この例外は違う...
                    raise HTTPNotFound()

                if response['result'] == u"OK" and response.has_key('serial'):
                    ticket = FakeTicketPrintHistory(
                        id=response['serial'],
                        item_token=token,
                        item_token_id=token.id,
                        performance=token.item.ordered_product.order.performance,
                        ordered_product_item=token.item,
                        ordered_product_item_id=token.item.id,
                        order=token.item.ordered_product.order,
                        order_no=token.item.ordered_product.order.order_no,
                        order_id=token.item.ordered_product.order_id,
                        seat=token.seat
                        )
                    qr = build_qr_by_orion(self.request, ticket, response['serial'])
                else:
                    if response.has_key('message'):
                        #return dict(
                        #    event = ticket.order.performance.event,
                        #    performance = ticket.order.performance,
                        #    message = response['message']
                        #)
                        r = Response(status=500, content_type="text/html; charset=UTF-8")
                        r.text = response['message']
                        return r
                    raise Exception()

                return dict(
                    _overwrite_generate_qrimage_route_name = 'order_review.orion_draw',
                    token = token.id,
                    serial = response['serial'],
                    sign = qr.sign,
                    order = token.item.ordered_product.order,
                    ticket = ticket,
                    performance = token.item.ordered_product.order.performance,
                    event = token.item.ordered_product.order.performance.event,
                    product = token.item.ordered_product.product,
                    gate = gate,
                    locale=custom_locale_negotiator(self.request) if self.request.organization.setting.i18n else ""
                )
            elif token.item.ordered_product.order.payment_delivery_pair.delivery_method.delivery_plugin_id == plugins.QR_DELIVERY_PLUGIN_ID:
                # altair
                ticket = build_qr_by_token_id(self.request, self.request.params['order_no'], self.request.params['token'])

                return dict(
                    token = token.id,    # dummy
                    serial = ticket.id,  # dummy
                    sign = ticket.sign,
                    order = ticket.order,
                    ticket = ticket,
                    performance = ticket.performance,
                    event = ticket.event,
                    product = ticket.product,
                    gate = gate,
                    locale=custom_locale_negotiator(self.request) if self.request.organization.setting.i18n else ""
                )
        else:
            order = get_order_by_order_no(self.request, order_no)
            tel = self.request.POST['tel']
            if tel not in order.shipping_address.tels:
                raise HTTPNotFound
            if order.payment_delivery_pair.delivery_method.delivery_plugin_id == plugins.QR_DELIVERY_PLUGIN_ID:
                # altair
                ticket = build_qr_by_order(self.request, order)

                return dict(
                    token=None,
                    serial=None,
                    sign=ticket.qr[0:8],
                    order=ticket.order,
                    ticket=ticket,
                    performance=ticket.performance,
                    event=ticket.event,
                    product=None,
                    gate=None
                )

    @lbr_view_config(
        route_name='order_review.qr_send',
        request_method="POST",
        renderer=selectable_renderer("order_review/send.html")
        )
    def send_mail(self):
        # TODO: validate mail address

        if 'mail' in self.request.params:
            mail = self.request.params['mail']
            # send mail using template
            form = schemas.SendMailSchema(self.request.POST)
            subject = self.request.params.get('subject', u"QRチケットに関しまして")

            if not form.validate():
                return dict(mail=mail,
                            message=u"Emailの形式が正しくありません")

            try:
                sender = self.context.organization.setting.default_mail_sender
                api.send_qr_mail(self.request, self.context, mail, sender, subject)
            except Exception, e:
                logger.error(e.message, exc_info=1)
                ## この例外は違う...
                raise HTTPNotFound()

            message = u"%s宛にメールをお送りしました。" % mail
            return dict(
                mail = mail,
                message = message
                )
        else:
            message = u"メールが見つかりませんでした。"
            return dict(
                message = message
                )

    @lbr_view_config(
        route_name='order_review.orion_send',
        request_method="POST",
        renderer=selectable_renderer("order_review/send.html"))
    def send_to_orion(self):
        # TODO: validate mail address

        mail = self.request.params.get('mail', None)
        if not mail:
            logger.info(u"Email address is not provided.")
            return dict(mail=mail,
                        message=u"Emailの形式が正しくありません")

        # send mail using template
        form = schemas.SendMailSchema(self.request.POST)

        if not form.validate():
            return dict(mail=mail,
                        message=u"Emailの形式が正しくありません")

        result = []
        try:
            # send_to_orionの時間をorion_ticket_phoneに記録する
            orion_ticket_phone = OrionTicketPhone.query.filter(OrionTicketPhone.order_no == self.request.params['order_no']).first()
            # send_to_orionは成功予定する
            orion_ticket_phone.sent = True
            if 'multi' in self.request.params and self.request.params['multi']!="":
                data_list = OrderedProductItemToken.query\
                    .join(OrderedProductItem)\
                    .join(OrderedProduct)\
                    .join(Order)\
                    .filter(Order.order_no==self.request.params['order_no'])
            else:
                # tokenで検索してorder_noを照合する
                data = OrderedProductItemToken.filter_by(id = self.request.params['token']).one()
                if data.item.ordered_product.order.order_no != self.request.params['order_no']:
                    raise Exception(u"Wrong order number or token: (%s, %s)" % (self.request.params['order_no'], self.request.params['token']))
                data_list = [data]

            free_seat_count = 0
            free_seat_name = ''
            for data in data_list:
                if data.seat is None:
                    seat = data.item.ordered_product.product.name
                    free_seat_count = free_seat_count + 1
                    free_seat_name = seat
                else:
                    seat = data.seat.name
                logger.info("token = %s" % data.id)
                response = api.send_to_orion(self.request, self.context, mail, data)
                if response == None:
                    result.append(dict(seat=seat, result=u"failure", reason=u"不明なエラー"))
                    # 一件だけ失敗したら、sentをFalseにする
                    orion_ticket_phone.sent = False
                    logger.info("failed to send order: {0}, token: {1}...".format(self.request.params['order_no'], data.id))
                elif response['result'] != u"OK":
                    result.append(dict(seat=seat, result=u"failure", reason=response['message']))
                    # 一件だけ失敗したら、sentをFalseにする
                    orion_ticket_phone.sent = False
                    logger.info("failed to send order: {0}, token: {1}...".format(self.request.params['order_no'], data.id))
                else:
                    result.append(dict(seat=seat, result=u"success"))

            # send_to_orionの時間をorion_ticket_phoneに記録する
            orion_ticket_phone.sent_at = datetime.now()
            orion_ticket_phone.update()

        except Exception, e:
            logger.error(e.message, exc_info=1)
            raise

        return dict(mail=mail,
                    result=result,
                    data_list=data_list,
                    free_seat_count=free_seat_count,
                    free_seat_name=free_seat_name
                    )


class QRTicketView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(
        route_name='order_review.qr_ticket.show',
        request_method='POST',
        renderer=selectable_renderer("order_review/qr_skidata.html"))
    def show_qr_ticket(self):
        self._validate_skidata_barcode(check_csrf=True)
        page_data = self._make_qr_ticket_page_base_data()
        page_data['sorted_email_histories'] = self.context.skidata_barcode_email_history_list_sorted
        return page_data

    @lbr_view_config(
        route_name='order_review.qr_ticket.show.not_owner',
        request_method='GET',
        renderer=selectable_renderer("order_review/qr_skidata.html"))
    def show_qr_ticket_not_owner(self):
        """
        非所有者向けQRチケット表示画面(メール送信などからの遷移)の描画処理を実施する
        :return: templateへのデータ
        """
        self._validate_skidata_barcode()
        return self._make_qr_ticket_page_base_data()

    @lbr_view_config(
        route_name='order_review.qr_ticket.qrdraw',
        xhr=False
    )
    def qr_draw(self):
        """
        QR画像バイナリを返却する
        :return: HTTPレスポンス(QR画像バイナリ入り)
        """
        self._validate_skidata_barcode()
        response = Response(status=200, content_type='image/gif')
        output_stream = StringIO.StringIO()
        write_qr_image_to_stream(self.context.skidata_barcode.data, output_stream, 'GIF')
        response.body = output_stream.getvalue()
        return response

    @lbr_view_config(
        route_name='order_review.qr_ticket.qr_send',
        request_method='POST',
        renderer=selectable_renderer('order_review/send.html')
        )
    def send_mail(self):
        self._validate_skidata_barcode(check_csrf=True)

        if self.context.organization.code == 'VK':
            form_template = self.request.view_context.get_template_path("order_review/qr_send.html")
        else:
            form_template = self.request.view_context.get_template_path("order_review/send.html")

        f = schemas.QRTicketSendMailSchema(self.request.POST)
        if not f.validate():
            error_msgs = [msg for _, msgs in f.errors.items() for msg in msgs]
            return render_to_response(form_template,
                                      dict(mail=f.email.data, message=u'\n'.join(error_msgs), view_context=self.request.view_context),
                                      request=self.request)

        try:
            sender = self.context.organization.setting.default_mail_sender
            api.send_qr_ticket_mail(self.request, self.context, f.email.data, sender)
        except Exception as e:
            logger.warn(e.message, exc_info=1)
            return render_to_response(form_template,
                                      dict(mail=f.email.data, message=u'メール送信に失敗しました', view_context=self.request.view_context),
                                      request=self.request)
        else:
            SkidataBarcodeEmailHistory.insert_new_history(self.context.skidata_barcode.id, f.email.data, datetime.now())

        if self.context.organization.code == 'VK':
            send_dict = dict(mail=f.email.data, message=u'{}宛にメールをお送りしました。'.format(f.email.data), view_context=self.request.view_context, result='success')
        else:
            send_dict = dict(mail=f.email.data, message=u'{}宛にメールをお送りしました。'.format(f.email.data), view_context=self.request.view_context)

        return render_to_response(form_template, send_dict, request=self.request)


    def _make_qr_ticket_page_base_data(self):
        resale_segment = self.context.resale_segment
        is_enable_discount_code = self.context.is_enable_discount_code
        is_enable_resale = self.context.is_enable_resale
        resale_status = False
        resale_segment_reception_date = False
        if resale_segment and is_enable_resale and not is_enable_discount_code:
            if resale_segment.reception_start_at < datetime.now() and resale_segment.reception_end_at > datetime.now():
                resale_status = True
            resale_segment_reception_date = True if resale_segment and resale_segment.reception_end_at < datetime.now() else False

        return dict(
            skidata_barcode=self.context.skidata_barcode,
            performance=self.context.performance,
            order=self.context.order,
            product_item=self.context.product_item,
            ordered_product_item = self.context.ordered_product_item,
            seat=self.context.seat,
            stock_type=self.context.stock_type,
            resale_status=resale_status,
            resale_segment_reception_date=resale_segment_reception_date,
            resale_request=self.context.resale_request,
            qr_url=self.request.route_path(u'order_review.qr_ticket.qrdraw', barcode_id=self.context.barcode_id,
                                           hash=self.context.hash)
        )

    @lbr_view_config(
        route_name='order_review.resale_request.orion',
        xhr=False
    )
    def orion_resale_request(self):
        order_no = self.request.matchdict.get('order_no')
        token_id = int(self.request.matchdict.get('token_id', 0))

        if order_no and token_id:
            token = get_matched_token_from_token_id(order_no, token_id)
            token_dp_id = token.item.ordered_product.order.payment_delivery_pair.delivery_method.delivery_plugin_id
            if token_dp_id == plugins.SKIDATA_QR_DELIVERY_PLUGIN_ID:
                try:
                    if token.item.ordered_product.order.order_no != order_no:
                        raise Exception(u"Wrong order number or token: (%s, %s)" % (order_no, token_id))
                    response = api.send_to_orion(self.request, self.context, None, token)
                except Exception, e:
                    logger.exception(e.message)
                    raise HTTPNotFound()

                if response['result'] == u"OK" and 'serial' in response:
                    if response['deeplink']:
                        return HTTPFound(location=response['deeplink'])
                    else:
                        raise Exception(u"Invalid Deeplink.")
                if 'message' in response:
                    r = Response(status=500, content_type="text/html; charset=UTF-8")
                    r.text = response['message']
                    return r
            else:
                raise Exception(u"Non-target delivery plugin ID: (%s)" % (token_dp_id))
        else:
            raise Exception(u"Wrong order number or token: (%s, %s)" % (order_no, token_id))
        return HTTPNotFound()


    def _validate_skidata_barcode(self, check_csrf=False):
        if self.context.skidata_barcode is None:
            logger.warn('Not found SkidataBarcode[id=%s].', self.context.barcode_id)
            raise HTTPNotFound()
        if self.context.hash != get_hash_from_barcode_data(self.context.skidata_barcode.data):
            logger.warn('Mismatch occurred between specified hash(%s) and SkidataBarcode[id=%s]', self.context.hash,
                        self.context.barcode_id)
            raise HTTPNotFound()
        if self.context.order.organization.id != self.context.organization.id:
            logger.warn('The SkidataBarcode[id=%s] is not in this organization.', self.context.barcode_id)
            raise HTTPNotFound()
        if self.context.order.paid_at is None:
            raise QRTicketUnpaidException()
        if self.context.order.issuing_start_at > datetime.now():
            raise QRTicketOutOfIssuingStartException()
        if self.context.order.canceled_at:
            raise QRTicketCanceledException()
        if self.context.order.refunded_at:
            raise QRTicketRefundedException()
        if check_csrf and not check_csrf_token(self.request, raises=False):
            logger.warn('Bad csrf token to access SkidataBarcode[id=%s].', self.context.barcode_id)
            raise HTTPNotFound()


class OrionEventGateView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(route_name='order_review.orion_ticket_list',
                     request_method="GET",
                     renderer="json")
    def orion_ticket_list(self):
        phone_number = self.request.params.get('phone_number', None)
        mail = self.request.params.get('mail', None)
        if not phone_number:
            return {"success": False, "errcode": "4000", "errmsg": "phone_number is required."}

        orion_ticket_phones = OrionTicketPhone.query \
            .join(Order, and_(OrionTicketPhone.order_no == Order.order_no))\
            .filter(OrionTicketPhone.owner_phone_number == phone_number)\
            .filter(OrionTicketPhone.sent == False) \
            .filter(Order.issuing_start_at <= datetime.now()) \
            .filter(Order.canceled_at == None) \
            .filter(Order.refunded_at == None) \
            .filter(Order.paid_at != None)

        fail_order = []

        for orion_ticket_phone in orion_ticket_phones:
            logger.info("sending order: {} to orion...".format(orion_ticket_phone.order_no))
            data_list = self.context.session.query(OrderedProductItemToken) \
                .join(OrderedProductItem) \
                .join(OrderedProduct) \
                .join(Order) \
                .filter(Order.order_no == orion_ticket_phone.order_no)

            for data in data_list:
                try:
                    response = api.send_to_orion(self.request, self.context, mail, data)
                except Exception as e:
                    # TKT9941 send_to_orionが、AttributeErrorと、Exceptionを返す
                    response = {'result': 'NG'}
                if not response or response['result'] != u"OK":
                    fail_order.append(orion_ticket_phone.order_no)
                    logger.info("fail to send order: {0}, token: {1} to orion for phone number: {2}...".format(
                        orion_ticket_phone.order_no,
                        data.id,
                        phone_number))
                    orion_ticket_phone.sent = False
                else:
                    orion_ticket_phone.sent = True

            orion_ticket_phone.sent_at = datetime.now()
            orion_ticket_phone.update()

        if fail_order:
            success = False
            errcode = "4000"
            errmsg = "fail to send order: {0} to orion for phone number: {1} ".format(','.join(fail_order), phone_number)
        else:
            success = True
            errcode = ""
            errmsg = ""

        return {"success": success, "errcode": errcode, "errmsg": errmsg}

class QRAESView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(
        route_name='order_review.qr_aes_confirm',
        renderer=selectable_renderer("order_review/qr_aes_confirm.html"))
    def qr_aes_confirm(self):
        sign = self.request.matchdict.get('sign', '')
        if not self.context.qr_aes_plugin:
            # AES_QR使用できないORG
            raise HTTPNotFound()

        ticket = self.context.qr_aes_plugin.build_qr_by_sign(sign)

        if ticket == None:
            raise HTTPNotFound()

        output_to_template = self.context.qr_aes_plugin.output_to_template(ticket)
        locale = custom_locale_negotiator(self.request) if self.request.organization.setting.i18n else u"ja"
        output_to_template.update({"locale": locale})

        return output_to_template

    @lbr_view_config(
        route_name='order_review.qr_aes',
        renderer=selectable_renderer("order_review/qr_aes.html"))
    def qr_aes_html(self):
        sign = self.request.matchdict.get('sign', '')
        ticket = self.context.qr_aes_plugin.build_qr_by_sign(sign)

        if ticket is None:
            raise HTTPNotFound()

        output_to_template = self.context.qr_aes_plugin.output_to_template(ticket)
        locale = custom_locale_negotiator(self.request) if self.request.organization.setting.i18n else u"ja"
        output_to_template.update({"locale": locale})

        return output_to_template

    @lbr_view_config(
        route_name='order_review.qr_aes_draw',
        xhr=False
        )
    def qr_aes_image(self):
        sign = self.request.matchdict.get('sign', '')
        ticket = self.context.qr_aes_plugin.build_qr_by_sign(sign)
        if ticket is None:
            raise HTTPNotFound()

        return qrdata_as_image_response(ticket)

    @lbr_view_config(
        route_name='order_review.qr_aes_print',
        request_method='POST',
        renderer=selectable_renderer("order_review/qr_aes.html")
        )
    def order_review_qr_aes_print(self):
        if 'order_no' not in self.request.params:
            return HTTPFound(self.request.route_path("order_review.index"))
        if 'token' not in self.request.params:
            return HTTPFound(self.request.route_path("order_review.index"))

        order_no = self.request.params['order_no']
        token_id = self.request.params['token']

        if token_id:
            ticket = self.context.qr_aes_plugin.build_qr_by_token_id(order_no=order_no, token_id=token_id)
        else:
            ticket = self.context.qr_aes_plugin.build_qr_by_order_no(self.request, order_no)

        output_to_template = self.context.qr_aes_plugin.output_to_template(ticket)
        locale = custom_locale_negotiator(self.request) if self.request.organization.setting.i18n else u"ja"
        output_to_template.update({"locale": locale, "disable_lang_link": True})

        return output_to_template

    @lbr_view_config(
        route_name='order_review.qr_aes_send',
        request_method="POST",
        renderer=selectable_renderer("order_review/send.html")
        )
    def send_mail(self):
        # TODO: validate mail address

        if 'mail' in self.request.params:
            mail = self.request.params['mail']
            # send mail using template
            form = schemas.SendMailSchema(self.request.POST)

            if not form.validate():
                return dict(mail=mail,
                            message=u"Emailの形式が正しくありません")

            try:
                sender = self.context.organization.setting.default_mail_sender
                api.send_qr_aes_mail(self.request, self.context, mail, sender)
            except Exception, e:
                logger.error(e.message, exc_info=1)
                ## この例外は違う...
                raise HTTPNotFound()

            message = u"%s宛にメールをお送りしました。" % mail
            return dict(
                mail = mail,
                message = message
                )
        else:
            message = u"メールが見つかりませんでした。"
            return dict(
                message = message
                )


class ReviewPasswordView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._message = partial(h._message, request=self.request)

    @lbr_view_config(
        route_name='review_password.search_form',
        request_method="GET",
        renderer=selectable_renderer("review_password/search_form.html")
        )
    def get(self):
        form = schemas.ReviewPasswordSchema(self.request.params)
        return dict(form=form)

    @lbr_view_config(
        route_name='review_password.search_form',
        request_method="POST",
        renderer=selectable_renderer("review_password/search_form.html")
        )
    def post(self):
        form = schemas.ReviewPasswordSchema(self.request.params)
        try:
            if not form.validate():
                raise ValidationError()
            type = self.request.params.get('type')
            valid_err = True
            if int(type) in [ReviewAuthorizationTypeEnum.CART.v, ReviewAuthorizationTypeEnum.LOTS.v]:
                review_password = form.data['review_password']
                email = form.data['email']
                query = self.context.get_review_authorization(email, review_password, type)
                if query.count():
                    valid_err = False
                    self.request.session['review_password_form'] = form
            if valid_err:
                form.email.errors.append(self._message(u'{0}または{1}が違います').format(form.email.label.text, form.review_password.label.text))
                raise ValidationError()

        except ValidationError:
            return dict(form=form)

        return HTTPFound(self.request.route_path('review_password.password_show'))

    @lbr_view_config(
        route_name='review_password.password_show',
        renderer=selectable_renderer("review_password/password_show.html")
    )
    def password_show(self):
        if 'review_password_form' not in self.request.session:
            return HTTPFound(location=self.request.route_url('review_password.search_form'))

        review_password_form = self.request.session['review_password_form']
        review_password = review_password_form.data['review_password']
        email = review_password_form.data['email']
        type = review_password_form.data['type']
        page = self.request.params.get("page", 1)
        paginate_by = 10
        orders = None
        lot_entries = None

        query = self.context.get_review_authorization(email, review_password, type)
        in_order_no=()
        for order_no in query.all():
            in_order_no = in_order_no + order_no

        if int(type) == ReviewAuthorizationTypeEnum.CART.v:
            # 購入確認
            orders = self.context.get_review_password_orders(in_order_no, page, paginate_by)
        else:
            # 抽選受付確認
            lot_entries = self.context.get_review_password_lots_entries(in_order_no, page, paginate_by)

        return dict(
            orders=orders,
            lot_entries=lot_entries
        )


@lbr_view_config(
    name="render.mail",
    renderer=selectable_renderer("order_review/qr.txt")
    )
def render_qrmail_viewlet(context, request):
    token = request.params['token']
    order_no = request.params['order_no']
    if token:
        ticket = build_qr_by_token_id(request, order_no, token)
    else:
        order = get_order_by_order_no(request, order_no)
        ticket = build_qr_by_order(request, order)

    if ticket is None:
        raise HTTPNotFound

    name = u''
    if ticket.order.shipping_address:
        name = ticket.order.shipping_address.last_name + ticket.order.shipping_address.first_name
    sign = ticket.qr[0:8]

    return dict(
        h=h,
        name=name,
        event=ticket.event,
        performance=ticket.performance,
        product=ticket.product,
        seat=ticket.seat,
        mail=request.params['mail'],
        url=request.route_url('order_review.qr_confirm', ticket_id=ticket.id, sign=sign),
        )

@lbr_view_config(
    name="render.mail_aes",
    renderer=selectable_renderer("order_review/qr_aes.txt")
    )
def render_qr_aes_mail_viewlet(context, request):
    token = request.params['token']
    order_no = request.params['order_no']
    if token:
        ticket = context.qr_aes_plugin.build_qr_by_token_id(order_no, token)
    else:
        order = get_order_by_order_no(request, order_no)
        ticket = context.qr_aes_plugin.build_qr_by_order(order)

    if ticket is None:
        raise HTTPNotFound

    name = u''
    if ticket.order.shipping_address:
        name = ticket.order.shipping_address.last_name + ticket.order.shipping_address.first_name

    return dict(
        h=h,
        name=name,
        event=ticket.event,
        performance=ticket.performance,
        product=ticket.product,
        seat=ticket.seat,
        mail=request.params['mail'],
        url=request.route_url('order_review.qr_aes_confirm', sign=ticket.sign),
        )


@lbr_view_config(
    name="render.mail_qr_ticket",
    renderer=selectable_renderer("order_review/qr_skidata.txt")
    )
def render_qr_ticket_mail_viewlet(context, request):
    name = u'{}{}'.format(context.order.shipping_address.last_name, context.order.shipping_address.first_name) \
        if context.order.shipping_address else u''
    return dict(
        h=h,
        name=name,
        event=context.performance.event,
        performance=context.performance,
        product=context.product,
        seat=context.seat,
        mail=request.params['email'],
        url=request.route_url(u'order_review.qr_ticket.show.not_owner',
                              barcode_id=context.barcode_id, hash=context.hash)
        )


@view_defaults(custom_predicates=(is_mypage_organization, ),
               permission='*')
class MypageWordView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        authenticated_user = self.context.authenticated_user()
        user = cart_api.get_user(authenticated_user)
        if not user:
            raise HTTPNotFound()
        self.user = user

    def _get_word(self, id=None, q=None):
        if id is not None and len(id) == 0 and q is None:
            return [ ]
        return get_word(self.request, id, q)

    def auto_update(self, req, res):
        if req != res:
            if len(res) == 0:
                # api errorかもしれない場合に全部消えたら嫌なので...
                return

            to_delete = [ x for x in list(set(req) - set(res)) ]
            to_register = [ x for x in list(set(res) - set(req)) ]

            logger.info("auto_update: delete(%s), register(%s)" % (to_delete, to_register))

            for word_id in to_register:
                DBSession.add(WordSubscription(user_id=self.user.id, word_id=word_id))
            if 0 < len(to_delete):
                to_delete_query = DBSession.query(WordSubscription)\
                    .filter(WordSubscription.user_id==self.user.id)\
                    .filter(WordSubscription.word_id.in_(to_delete))
                for ws in to_delete_query.all():
                    ws.delete()

            DBSession.flush()

    @lbr_view_config(route_name='mypage.word.show',
        request_method="GET",
        custom_predicates=(override_auth_type,),
        renderer=selectable_renderer("mypage/word.html"),)
    def form(self):
        word_enabled = self.request.organization.setting.enable_word == 1
        if not word_enabled:
            return { }

        subscriptions = WordSubscription.query.filter(WordSubscription.user_id==self.user.id).all()
        words = self._get_word(id=' '.join([ str(s.word_id) for s in subscriptions ]))

        self.auto_update(sorted([s.word_id for s in subscriptions]), [w["id"] for w in words])

        return { "enabled": True, "words": words }

    @lbr_view_config(route_name='mypage.word.search',
        request_method="GET",
        custom_predicates=(override_auth_type,),
        renderer="json")
    def search(self):
        words = None
        q = self.request.params.get('q')
        if q is not None and 0 < len(q):
            words = self._get_word(q=q.encode('utf-8'))
        else:
            id = self.request.params.get('id')
            if id is not None and 0 < len(id) and re.match("[\d ]+", id):
                words = self._get_word(id=id)
        return { "data": words }

    @lbr_view_config(route_name='mypage.word.configure',
        request_method="POST",
        custom_predicates=(override_auth_type,),
        renderer="json")
    def configure(self):
        authenticated_user = self.context.authenticated_user()
        user = cart_api.get_user(authenticated_user)
        subscribe = self.request.params.get('subscribe')
        profile = UserProfile.query.filter(UserProfile.user_id==user.id).first()
        if profile is None:
            profile = UserProfile(user_id=user.id)
            profile.subscribe_word = 1 if subscribe=="1" else 0
            DBSession.add(profile)
        else:
            profile.subscribe_word = 1 if subscribe=="1" else 0
            profile.update()
            DBSession.flush()
        return { "result": "OK" }

    @lbr_view_config(route_name='mypage.word.subscribe',
        request_method="POST",
        custom_predicates=(override_auth_type,),
        renderer="json")
    def subscribe(self):
        word_id = self.request.params.get('word')
        words = self._get_word(id=word_id)
        if words is not None and len(words) != 1:
            return { }

        word_id = words[0]['id']
        if WordSubscription.query.filter(WordSubscription.user_id==self.user.id, WordSubscription.word_id==word_id).first() != None:
            # already registered
            return { }

        WordSubscription.add(WordSubscription(user_id=self.user.id, word_id=word_id))
        return { "result": "OK", "data": words }

    @lbr_view_config(route_name='mypage.word.unsubscribe',
        request_method="POST",
        custom_predicates=(override_auth_type,),
        renderer="json")
    def unsubscribe(self):
        word_id = self.request.params.get('word')
        words = self._get_word(id=word_id)
        if len(words) != 1:
            return { }
        word_id = words[0]['id']
        ws = WordSubscription.query.filter(WordSubscription.user_id==self.user.id, WordSubscription.word_id==word_id).first()
        if ws != None:

            ws.delete()
            DBSession.flush()
            return { "result": "OK", "data": words }

        return { }


class LiveStreamingView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(
        route_name='order_review.live',
        request_method='POST',
        renderer=selectable_renderer("PC/live_streaming/abstract_live.html")
    )
    def live_post(self):
        if not self.context.check_post_data():
            # 不正な遷移
            raise HTTPNotFound()

        if not self.context.can_watch_video:
            # 予約に紐付かないビデオを見ようとしている
            raise HTTPNotFound()

        return render_to_response('templates/RT/pc/live_streaming/{}/live.html'
                                  .format(self.context.live_performance_setting.template_type),
                                  {'watching_permission_error': self.context.watching_permission_error,
                                   'live_performance_setting': self.context.live_performance_setting},
                                  request=self.request)


@lbr_view_config(
    route_name="pgw.authorize",
    renderer='json'
    )
def pgw_authorize(context, request):
    pgw_request = json.loads(request.POST['pgw_request'])
    pgw_api_response = pgw_api.authorize(
        request=request,
        pgw_request=pgw_request,
        is_three_d_secure_authentication_result=request.POST['is_three_d_secure_authentication_result']
    )
    return pgw_api_response


@lbr_view_config(
    route_name="pgw.capture",
    renderer='json'
    )
def pgw_capture(context, request):

    pgw_api_response = pgw_api.capture(
        request=request,
        payment_id=request.POST['payment_id'],
        capture_amount=request.POST['capture_amount']
    )
    return pgw_api_response


@lbr_view_config(
    route_name="pgw.authorize_and_capture",
    renderer='json'
    )
def pgw_authorize_and_capture(context, request):
    pgw_request = json.loads(request.POST['pgw_request'])
    pgw_api_response = pgw_api.authorize_and_capture(
        request=request,
        pgw_request=pgw_request,
        is_three_d_secure_authentication_result=request.POST['is_three_d_secure_authentication_result']
    )
    return pgw_api_response


@lbr_view_config(
    route_name="pgw.find",
    renderer='json'
    )
def pgw_find(context, request):
    pgw_api_response = pgw_api.find(
        request=request,
        payment_ids=request.POST['payment_ids'],
        search_type=request.POST['search_type']
    )
    return pgw_api_response


@lbr_view_config(
    route_name="pgw.cancel_or_refund",
    renderer='json'
    )
def pgw_cancel_or_refund(context, request):
    pgw_api_response = pgw_api.cancel_or_refund(
        request=request,
        payment_id=request.POST['payment_id']
    )
    return pgw_api_response


@lbr_view_config(
    route_name="pgw.modify",
    renderer='json'
    )
def pgw_modify(context, request):
    pgw_api_response = pgw_api.modify(
        request=request,
        payment_id=request.POST['payment_id'],
        modified_amount=request.POST['modified_amount']
    )
    return pgw_api_response


@lbr_view_config(
    route_name="pgw.three_d_secure_enrollment_check",
    renderer='json'
    )
def pgw_three_d_secure_enrollment_check(context, request):
    pgw_api_response = pgw_api.three_d_secure_enrollment_check(
        request=request,
        sub_service_id=request.POST['sub_service_id'],
        enrollment_id=request.POST['enrollment_id'],
        callback_url=request.POST['callback_url'],
        amount=request.POST['gross_amount'],
        card_token=request.POST['card_token']
    )
    return pgw_api_response
