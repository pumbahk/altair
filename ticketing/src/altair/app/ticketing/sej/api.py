# -*- coding:utf-8 -*-

from datetime import timedelta
import logging
logger = logging.getLogger(__name__)

from sqlalchemy import update
from sqlalchemy import and_
from sqlalchemy.sql.expression import desc
from sqlalchemy.orm.exc import NoResultFound

import sqlahelper

from .utils import JavaHashMap
from .models import SejNotification, SejOrder, SejTicket, SejTenant, SejRefundEvent, SejRefundTicket, SejNotificationType

from .helpers import create_hash_from_x_start_params
from altair.app.ticketing.sej.exceptions import SejServerError
from altair.app.ticketing.sej.payment import request_cancel_order
from pyramid.threadlocal import get_current_registry

DBSession = sqlahelper.get_session()

def cancel_sej_order(sej_order, organization_id):
    if not sej_order:
        logger.error(u'sej_order is None')
        return False
    if sej_order.cancel_at:
        logger.error(u'SejOrder(order_no=%s) is already canceled' % sej_order.order_no if sej_order else None)
        return False

    settings = get_current_registry().settings
    tenant = SejTenant.filter_by(organization_id=organization_id).first()

    inticket_api_url = (tenant and tenant.inticket_api_url) or settings.get('sej.inticket_api_url')
    shop_id = (tenant and tenant.shop_id) or settings.get('sej.shop_id')
    api_key = (tenant and tenant.api_key) or settings.get('sej.api_key')

    if sej_order.shop_id != shop_id:
        logger.error(u'SejOrder(order_no=%s).shop_id (%s) != SejTenant.shop_id (%s)' % (sej_order.order_no, sej_order.shop_id, shop_id))
        return False

    try:
        request_cancel_order(
            order_no=sej_order.order_no,
            billing_number=sej_order.billing_number,
            exchange_number=sej_order.exchange_number,
            shop_id=shop_id,
            secret_key=api_key,
            hostname=inticket_api_url
        )
        return True
    except SejServerError as e:
        import sys
        logger.error(u'Could not cancel SejOrder (%s)' % e, exc_info=sys.exc_info())
        return False

def get_per_order_fee(order):
    pdmp = order.payment_delivery_pair
    fee = 0
    if order.refund.include_system_fee:
        fee += order.system_fee
    if order.refund.include_special_fee:
        fee += order.special_fee
    if order.refund.include_transaction_fee:
        fee += pdmp.transaction_fee_per_order
    if order.refund.include_delivery_fee:
        fee += pdmp.delivery_fee_per_order
    if order.refund.include_item:
        # チケットに紐づかない商品明細分の合計金額
        for op in order.items:
            for opi in op.ordered_product_items:
                if not opi.product_item.ticket_bundle_id:
                    fee += opi.price * opi.quantity
    return fee

def get_per_ticket_fee(order):
    pdmp = order.payment_delivery_pair
    fee = 0
    if order.refund.include_transaction_fee:
        fee += pdmp.transaction_fee_per_ticket
    if order.refund.include_delivery_fee:
        fee += pdmp.delivery_fee_per_ticket
    return fee

def get_ticket_price(order, product_item_id):
    if not order.refund.include_item:
        return 0
    for op in order.items:
        for opi in op.ordered_product_items:
            if opi.product_item_id == product_item_id:
                return opi.price
    return 0

def refund_sej_order(sej_order, organization_id, order, now):
    if not sej_order:
        logger.error(u'sej_order is None')
        return False
    if sej_order.cancel_at:
        logger.error(u'SejOrder(order_no=%s) is already canceled' % sej_order.order_no if sej_order else None)
        return False

    sej_tickets = SejTicket.query.filter_by(order_no=sej_order.order_no).order_by(SejTicket.ticket_idx).all()
    if not sej_tickets:
        logger.error(u'No tickets associated with SejOrder(order_no=%s)' % sej_order.order_no)
        return False

    settings = get_current_registry().settings
    tenant = SejTenant.filter_by(organization_id=organization_id).first()
    shop_id = (tenant and tenant.shop_id) or settings.get('sej.shop_id')
    performance = order.performance

    # create SejRefundEvent
    re = SejRefundEvent.filter(and_(
        SejRefundEvent.shop_id==shop_id,
        SejRefundEvent.event_code_01==performance.code
    )).first()
    if not re:
        re = SejRefundEvent()
        DBSession.add(re)

    re.available = 1
    re.shop_id = shop_id
    re.event_code_01 = performance.code
    re.title = performance.name
    re.event_at = performance.start_on.strftime('%Y%m%d')
    re.start_at = order.refund.start_at.strftime('%Y%m%d')
    re.end_at = order.refund.end_at.strftime('%Y%m%d')
    re.event_expire_at = order.refund.end_at.strftime('%Y%m%d')
    ticket_expire_at = order.refund.end_at + timedelta(days=+7)
    re.ticket_expire_at = ticket_expire_at.strftime('%Y%m%d')
    re.refund_enabled = 1
    re.need_stub = 1
    DBSession.merge(re)

    # create SejRefundTicket
    per_order_fee = get_per_order_fee(order.prev)
    for i, sej_ticket in enumerate(sej_tickets):
        rt = SejRefundTicket.filter(and_(
            SejRefundTicket.order_no==sej_order.order_no,
            SejRefundTicket.ticket_barcode_number==sej_ticket.barcode_number
        )).first()
        if not rt:
            rt = SejRefundTicket()
            DBSession.add(rt)

        rt.available = 1
        rt.refund_event_id = re.id
        rt.event_code_01 = performance.code
        rt.order_no = sej_order.order_no
        rt.ticket_barcode_number = sej_ticket.barcode_number
        rt.refund_ticket_amount = get_ticket_price(order.prev, sej_ticket.product_item_id)
        rt.refund_other_amount = get_per_ticket_fee(order.prev)
        # 手数料などの払戻があったら1件目に含める
        if per_order_fee > 0 and i == 0:
            rt.refund_other_amount += per_order_fee

        DBSession.merge(rt)

    return True

def get_sej_order(order_no, session=None):
    if session is None:
        session = DBSession
    return session.query(SejOrder) \
        .filter_by(order_no=order_no) \
        .order_by(desc(SejOrder.branch_no)) \
        .first()
