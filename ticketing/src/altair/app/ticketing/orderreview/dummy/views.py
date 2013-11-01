# -*- coding:utf-8 -*-
import mock
import logging
logger = logging.getLogger(__name__)
from functools import wraps
from datetime import datetime

from pyramid.view import view_config
from altair.mobile import mobile_view_config
from altair.app.ticketing.cart.selectable_renderer import selectable_renderer
from altair.app.ticketing.core.models import (
    Organization,
    Host,
    TicketPrintHistory
)
from altair.app.ticketing.qr.utils import build_qr_by_history

def overwrite_request_organization(fn):
    @wraps(fn)
    def wrapped(context, request):
        if "organization_id" in request.params:
            organization_id = request.params["organization_id"]
            logger.info("* dummy overwrite organization: organization_id = {0}".format(organization_id))
            organization = Organization.query.filter_by(id=organization_id).first()
            if organization:
                request.organization = organization
        return fn(context, request)
    return wrapped

from altair.app.ticketing.qr.builder import qr

class DummyQRMaker(qr):
    def __init__(self, request):
        self.request = request

    def make(self, params):
        return "qr image"
    key = "k"

@view_config(route_name="dummy.orderreview.index", renderer="altair.app.ticketing.orderreview:templates/dummy/index.html")
def dummy_index(context, request):
    organizations = Organization.query.filter_by(deleted_at=None).filter(Host.organization_id==Organization.id).all()
    return {"organizations": organizations}

@mobile_view_config(route_name='dummy.orderreview.qr', decorator=overwrite_request_organization, renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review/qr.html"))
@view_config(route_name='dummy.orderreview.qr', decorator=overwrite_request_organization, renderer=selectable_renderer("altair.app.ticketing.orderreview:templates/%(membership)s/order_review/qr.html"))
def dummy_qr(context, request):
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
        )


