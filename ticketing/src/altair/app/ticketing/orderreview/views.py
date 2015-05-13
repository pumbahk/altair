# -*- coding:utf-8 -*-
import logging
import sqlahelper
import json
from datetime import datetime

from pyramid.view import view_defaults
from pyramid.request import Request
from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.decorator import reify
from pyramid.interfaces import IRouteRequest, IRequest

from altair.auth.api import get_who_api
from altair.mobile.api import is_mobile_request
from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.app.ticketing.core.api import get_default_contact_url
from altair.request.adapters import UnicodeMultiDictAdapter
from altair.now import get_now, is_now_set

from altair.app.ticketing.core.models import ShippingAddress
from altair.app.ticketing.core.utils import IssuedAtBubblingSetter
from altair.app.ticketing.mailmags.api import get_magazines_to_subscribe, multi_subscribe, multi_unsubscribe
from altair.app.ticketing.payments import plugins

from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.cart.rendering import selectable_renderer
from altair.app.ticketing.cart.view_support import filter_extra_form_schema, get_extra_form_schema, render_view_to_response_with_derived_request, render_display_value
from altair.app.ticketing.qr.image import qrdata_as_image_response
from altair.app.ticketing.qr.utils import build_qr_by_history_id
from altair.app.ticketing.qr.utils import build_qr_by_token_id, build_qr_by_orion, get_matched_token_from_token_id
from altair.app.ticketing.fc_auth.api import do_authenticate
from altair.app.ticketing.orders.models import Order, OrderedProduct, OrderedProductItem, OrderedProductItemToken
from altair.app.ticketing.orders.api import OrderAttributeIO
from altair.app.ticketing.lots.models import LotEntry

from .api import is_mypage_organization, is_rakuten_auth_organization
from . import schemas
from . import api
from . import helpers as h
from .exceptions import InvalidForm

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
        renderer=selectable_renderer("mypage/show.html")
        )
    def show(self):
        jump_maintenance_page_om_for_trouble(self.request.organization)
        authenticated_user = self.context.authenticated_user()
        user = cart_api.get_user(authenticated_user)
        per = 10

        if not user:
            raise HTTPNotFound()

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

        return dict(
            shipping_address=shipping_address,
            orders=orders,
            lot_entries=entries,
            mailmagazines_to_subscribe=magazines_to_subscribe,
            h=h,
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
        form = schemas.OrderReviewSchema(self.request.params)
        return {"form": form}

    @lbr_view_config(route_name='order_review.guest')
    def guest(self):
        jump_maintenance_page_om_for_trouble(self.request.organization)
        return HTTPFound(location=self.request.route_path("order_review.form"))


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

        # 抽選発表予定日のチェック
        if order is not None:
            lot_entry = LotEntry.query.filter_by(entry_no=order.order_no).first()
            if lot_entry is not None:
                announce_datetime = lot_entry.lot.lotting_announce_datetime
        if announce_datetime is not None:
            if announce_datetime > datetime.now():
                raise InvalidForm(form, [u'受付番号または電話番号が違います。'])

        if order is None or order.shipping_address is None:
            raise InvalidForm(form, [u'受付番号または電話番号が違います。'])
        return dict(order=order)

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
            for entry in OrderAttributeIO(for_='cart', mode=mode).marshal(self.request, order)
            }
        extra_form_field_descs = get_extra_form_schema(self.context, self.request, order.sales_segment, for_='cart')
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

        return dict(
            sign = sign,
            order = ticket.order,
            ticket = ticket,
            performance = ticket.performance,
            event = ticket.event,
            product = ticket.product,
            )

    @lbr_view_config(
        route_name='order_review.qr',
        renderer=selectable_renderer("order_review/qr.html"))
    def qr_html(self):
        ticket_id = int(self.request.matchdict.get('ticket_id', 0))
        sign = self.request.matchdict.get('sign', 0)

        ticket = build_qr_by_history_id(self.request, ticket_id)

        if ticket == None or ticket.sign != sign:
            raise HTTPNotFound()

        if ticket.seat is None:
            gate = None
        else:
            gate = ticket.seat.attributes.get("gate", None)

        return dict(
            token = ticket.item_token.id, # dummy
            serial = ticket_id,           # dummy
            sign = sign,
            order = ticket.order,
            ticket = ticket,
            performance = ticket.performance,
            event = ticket.event,
            product = ticket.product,
            gate = gate
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

        ticket = type('FakeTicketPrintHistory', (), {
            'id': serial,
            'performance': data.item.ordered_product.order.performance,
            'ordered_product_item': data.item,
            'order': data.item.ordered_product.order,
            'seat': data.seat,
        })
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
        token = get_matched_token_from_token_id(self.request.params['order_no'], self.request.params['token'])

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
                ticket = type('FakeTicketPrintHistory', (), {
                    'id': response['serial'],
                    'performance': token.item.ordered_product.order.performance,
                    'ordered_product_item': token.item,
                    'order': token.item.ordered_product.order,
                    'seat': token.seat,
                })
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
                gate = gate
            )
        elif token.item.ordered_product.order.payment_delivery_pair.delivery_method.delivery_plugin_id == plugins.QR_DELIVERY_PLUGIN_ID:
            # altair
            ticket = build_qr_by_token_id(self.request, self.request.params['order_no'], self.request.params['token'])

            return dict(
                token = token.id,    # dummy
                serial = ticket.id,  # dummy
                sign = ticket.qr[0:8],
                order = ticket.order,
                ticket = ticket,
                performance = ticket.performance,
                event = ticket.event,
                product = ticket.product,
                gate = gate
            )

    @lbr_view_config(
        route_name='order_review.qr_send',
        request_method="POST",
        renderer=selectable_renderer("order_review/send.html")
        )
    def send_mail(self):
        # TODO: validate mail address

        mail = self.request.params['mail']
        # send mail using template
        form = schemas.SendMailSchema(self.request.POST)

        if not form.validate():
            return dict(mail=mail,
                        message=u"Emailの形式が正しくありません")

        try:
            sender = self.context.organization.setting.default_mail_sender
            api.send_qr_mail(self.request, self.context, mail, sender)
        except Exception, e:
            logger.error(e.message, exc_info=1)
            ## この例外は違う...
            raise HTTPNotFound()

        message = u"%s宛にメールをお送りしました。" % mail
        return dict(
            mail = mail,
            message = message
            )

    @lbr_view_config(
        route_name='order_review.orion_send',
        request_method="POST",
        renderer=selectable_renderer("order_review/send.html"))
    def send_to_orion(self):
        # TODO: validate mail address

        mail = self.request.params['mail']
        # send mail using template
        form = schemas.SendMailSchema(self.request.POST)

        if not form.validate():
            return dict(mail=mail,
                        message=u"Emailの形式が正しくありません")

        result = []
        try:
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

            for data in data_list:
                if data.seat is None:
                    seat = data.item.ordered_product.product.name
                else:
                    seat = data.seat.name
                logger.info("token = %s" % data.id)
                response = api.send_to_orion(self.request, self.context, mail, data)
                if response == None:
                    result.append(dict(seat=seat, result=u"failure", reason=u"不明なエラー"))
                elif response['result'] != u"OK":
                    result.append(dict(seat=seat, result=u"failure", reason=response['message']))
                else:
                    result.append(dict(seat=seat, result=u"success"))
        except Exception, e:
            logger.error(e.message, exc_info=1)
            raise

        return dict(mail=mail,
                    result=result,
                    )


@lbr_view_config(
    name="render.mail",
    renderer=selectable_renderer("order_review/qr.txt")
    )
def render_qrmail_viewlet(context, request):
    ticket = build_qr_by_token_id(request, request.params['order_no'], request.params['token'])
    sign = ticket.qr[0:8]
    if ticket.order.shipping_address:
        name = ticket.order.shipping_address.last_name + ticket.order.shipping_address.first_name
    else:
        name = u''

    return dict(
        name=name,
        event=ticket.event,
        performance=ticket.performance,
        product=ticket.product,
        seat=ticket.seat,
        mail = request.params['mail'],
        url = request.route_url('order_review.qr_confirm', ticket_id=ticket.id, sign=sign),
        )
