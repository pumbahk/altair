# -*- coding:utf-8 -*-
import mock
import logging
logger = logging.getLogger(__name__)
from functools import wraps
from datetime import datetime

from pyramid.view import view_config
from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.app.ticketing.cart.request import ENV_ORGANIZATION_ID_KEY
from altair.app.ticketing.cart.rendering import selectable_renderer
from altair.app.ticketing.core.models import (
    Organization,
    Host,
    TicketPrintHistory
)
from altair.app.ticketing.qr.image import qrdata_as_image_response
from altair.app.ticketing.qr.utils import build_qr_by_history


def overwrite_request_organization(fn):
    @wraps(fn)
    def wrapped(context, request):
        if "organization_id" in request.params:
            organization_id = request.params["organization_id"]
            logger.info("* dummy overwrite organization: organization_id = {0}".format(organization_id))
            organization = Organization.query.filter_by(id=organization_id).first()
            if organization:
                request.environ[ENV_ORGANIZATION_ID_KEY] = organization.id
        return fn(context, request)
    return wrapped

from altair.app.ticketing.qr.builder import qr

class DummyQRMaker(qr):
    def __init__(self, request):
        self.request = request

    def make(self, params):
        return "qr image"
    key = "k"

class DummyModels:
    @staticmethod
    def ticket(request):
        ticket = mock.MagicMock("*QRSeed*")
        ticket.id = -10000
        ticket.mock_add_spec(TicketPrintHistory)
        with mock.patch("altair.app.ticketing.qr.utils.get_qrdata_builder", new=DummyQRMaker):
            ticket = build_qr_by_history(request, ticket)

        ticket.ordered_product_item.product_item.performance.event.title = u"ダミーイベント"
        ticket.ordered_product_item.product_item.performance.name = u'ダミー公演'

        ticket.ordered_product_item.ordered_product.order.order_no = "DM01010101"
        ticket.ordered_product_item.product_item.performance.code = "DMCODE"
        ticket.ordered_product_item.ordered_product.product.name = u"ダミー商品"
        ticket.ordered_product_item.ordered_product.product.id = -1000
        ticket.seat.name = u"ダミー：座席"
        ticket.seat.l0_id = -123
        ticket.ordered_product_item.product_item.performance.start_on = datetime(2000, 1, 1)
        return ticket

@lbr_view_config(route_name="dummy.orderreview.index", renderer="altair.app.ticketing.orderreview:templates/dummy/index.html")
def dummy_index(context, request):
    organizations = Organization.query.filter_by(deleted_at=None).filter(Host.organization_id==Organization.id).all()
    return {"organizations": organizations}

@lbr_view_config(route_name="dummy.orderreview.qrdraw", xhr=False, permission="view")
def dummy_qr_draw(context, request):
    ## qr builderを一時的に切り替えられれば不要
    ticket = DummyModels.ticket(request)
    return qrdata_as_image_response(ticket)

def get_dummy_order():
    order = mock.Mock()
    order.created_at = datetime.now()
    order.performance.name = u'パフォーマンス名'
    order.performance.venue.name = u'会場名'
    order.performance.event.title = u'イベント名'
    order.performance.start_on = datetime.now()
    order.items = []
    order.transaction_fee = 1
    order.delivery_fee = 2
    order.system_fee = 3
    order.special_fee = 4
    order.total_amount = 5
    order.payment_delivery_pair.payment_method.payment_plugin_id = 1
    order.payment_delivery_pair.delivery_method.delivery_plugin_id = 1
    order.payment_delivery_pair.special_fee_name = u'特別手数料名'
    order.shipping_address = mock.Mock(
        zip=u'000-0000',
        prefecture=u'神奈川県',
        city=u'横浜市',
        address_1=u'戸塚区',
        address_2=u'レジデンスロングネーム1020',
        last_name=u'名字',
        last_name_kana=u'ミョウジ',
        first_name=u'名前',
        first_name_kana=u'ナマエ',
        tel_1=u'045-000-0000',
        tel_2=u'090-0000-0000'
        )
    order.attributes = { u'テスト': u'テスト' }
    order.get_order_attribute_pair_pairs.return_value = [
        ((u'test', u'test'), (u'テスト', u'テスト'))
        ]
    return order

@lbr_view_config(route_name='dummy.orderreview.show.guest', request_type='altair.mobile.interfaces.IMobileRequest', request_method="GET", decorator=overwrite_request_organization,
                    renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review_mobile_guest/show.html"))
@lbr_view_config(route_name='dummy.orderreview.show.guest', request_method="GET", decorator=overwrite_request_organization,
             renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review_guest/show.html"))
def dummy_show_guest(context, request):
    order = get_dummy_order()
    sej_order = mock.Mock()
    return dict(order=order, sej_order=sej_order, shipping_address=order.shipping_address)

@lbr_view_config(route_name='dummy.orderreview.show', request_type='altair.mobile.interfaces.IMobileRequest', request_method="GET", decorator=overwrite_request_organization,
                    renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review_mobile/show.html"))
@lbr_view_config(route_name='dummy.orderreview.show', request_method="GET", decorator=overwrite_request_organization,
             renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review/show.html"))
def dummy_show(context, request):
    order = get_dummy_order()
    sej_order = mock.Mock()
    return dict(order=order, sej_order=sej_order, shipping_address=order.shipping_address)

@lbr_view_config(route_name='dummy.orderreview.qr', request_type='altair.mobile.interfaces.IMobileRequest', decorator=overwrite_request_organization, renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review/qr.html"))
@lbr_view_config(route_name='dummy.orderreview.qr', decorator=overwrite_request_organization, renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review/qr.html"))
def dummy_qr(context, request):
    ticket = DummyModels.ticket(request)

    ## historical reason. ticket variable is one of TicketPrintHistory object.
    gate = u"*ゲート名*"
    return dict(
        sign=ticket.sign,
        order=ticket.order,
        ticket=ticket,
        performance=ticket.performance,
        event=ticket.event,
        product=ticket.product,
        gate=gate,
        _overwrite_generate_qrimage_route_name="dummy.orderreview.qrdraw"
        )
