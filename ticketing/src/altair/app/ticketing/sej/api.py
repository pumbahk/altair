# -*- coding:utf-8 -*-

from datetime import timedelta
import logging
logger = logging.getLogger(__name__)

from sqlalchemy import update
from sqlalchemy import and_
from sqlalchemy.sql.expression import asc, desc
from sqlalchemy.orm.exc import NoResultFound

import sqlahelper

from .utils import JavaHashMap
from .models import SejNotification, SejOrder, SejTicket, SejRefundEvent, SejRefundTicket, SejNotificationType, ThinSejTenant

from .helpers import create_hash_from_x_start_params
from .interfaces import ISejTenant
from altair.app.ticketing.sej.exceptions import SejServerError
from altair.app.ticketing.sej.payment import request_cancel_order
from pyramid.threadlocal import get_current_registry
from pyramid.interfaces import IRequest

DBSession = sqlahelper.get_session()

def cancel_sej_order(request, tenant, sej_order, now=None):
    if not sej_order:
        logger.error(u'sej_order is None')
        return False
    if sej_order.cancel_at:
        logger.error(u'SejOrder(order_no=%s) is already canceled' % sej_order.order_no if sej_order else None)
        return False

    if sej_order.shop_id != tenant.shop_id:
        logger.error(u'SejOrder(order_no=%s).shop_id (%s) != SejTenant.shop_id (%s)' % (sej_order.order_no, sej_order.shop_id, tenant.shop_id))
        return False

    try:
        request_cancel_order(
            request,
            tenant=tenant,
            sej_order=sej_order,
			now=now
        )
        return True
    except SejServerError as e:
        import sys
        logger.error(u'Could not cancel SejOrder (%s)' % e, exc_info=sys.exc_info())
        return False

def refund_sej_order(request, tenant, sej_order, performance_name, performance_code, performance_start_on, per_order_fee, per_ticket_fee, ticket_price_getter, refund_start_at, refund_end_at, ticket_expire_at, now):
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

    # create SejRefundEvent
    re = SejRefundEvent.filter(and_(
        SejRefundEvent.shop_id==tenant.shop_id,
        SejRefundEvent.event_code_01==performance_code
    )).first()
    if not re:
        re = SejRefundEvent()
        DBSession.add(re)

    re.available = 1
    re.shop_id = tenant.shop_id
    re.event_code_01 = performance_code
    re.title = performance_name
    re.event_at = performance_start_on.strftime('%Y%m%d')
    re.start_at = refund_start_at.strftime('%Y%m%d')
    re.end_at = refund_end_at.strftime('%Y%m%d')
    re.event_expire_at = refund_end_at.strftime('%Y%m%d')
    re.ticket_expire_at = ticket_expire_at.strftime('%Y%m%d')
    re.refund_enabled = 1
    re.need_stub = 1
    DBSession.merge(re)

    # create SejRefundTicket
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
        rt.event_code_01 = performance_code
        rt.order_no = sej_order.order_no
        rt.ticket_barcode_number = sej_ticket.barcode_number
        rt.refund_ticket_amount = ticket_price_getter(sej_ticket)
        rt.refund_other_amount = per_ticket_fee
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

def get_sej_orders(order_no, fetch_canceled=False, session=None):
    if session is None:
        session = DBSession
    q = session.query(SejOrder)
    q = q.filter_by(order_no=order_no)
    if not fetch_canceled:
        q = q.filter_by(cancel_at=None)
    return q.all()

def get_default_sej_tenant(request_or_registry):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    return registry.getUtility(ISejTenant)


def merge_sej_tenant(src, override_by):
    return ThinSejTenant(
        src,
        shop_name=override_by.shop_name,
        shop_id=override_by.shop_id,
        contact_01=override_by.contact_01,
        contact_02=override_by.contact_02,
        api_key=override_by.api_key,
        inticket_api_url=override_by.inticket_api_url
        )

def validate_sej_tenant(sej_tenant):
    if not sej_tenant.shop_id:
        raise AssertionError('shop_id is empty')
    if not sej_tenant.api_key:
        raise AssertionError('api_key is empty')
    if not sej_tenant.inticket_api_url:
        raise AssertionError('inticket_api_url is empty')

def build_sej_tickets_from_dicts(order_no, tickets, barcode_number_getter):
    return [
        SejTicket(
            order_no             = order_no,
            ticket_idx           = (i + 1),
            ticket_type          = '%d' % ticket.get('ticket_type').v,
            event_name           = ticket.get('event_name'),
            performance_name     = ticket.get('performance_name'),
            performance_datetime = ticket.get('performance_datetime'),
            ticket_template_id   = ticket.get('ticket_template_id'),
            ticket_data_xml      = ticket.get('xml').xml,
            product_item_id      = ticket.get('product_item_id'),
            barcode_number       = barcode_number_getter(i + 1)
            )
        for i, ticket in enumerate(tickets)
        ]

def create_sej_order(
        request_or_registry,
        order_no,
        user_name,
        user_name_kana,
        tel,
        zip_code,
        email,
        total_price,
        ticket_price,
        commission_fee,
        payment_type,
        ticketing_fee=0,
        payment_due_at=None,
        ticketing_start_at=None,
        ticketing_due_at=None,
        regrant_number_due_at=None,
        tickets=[]):
    sej_order = SejOrder(
        order_no=order_no,
        user_name=user_name,
        user_name_kana=user_name_kana,
        tel=tel,
        zip_code=zip_code,
        email=email,
        total_price=total_price,
        ticket_price=ticket_price,
        commission_fee=commission_fee,
        payment_type='%d' % int(payment_type),
        ticketing_fee=ticketing_fee,
        payment_due_at=payment_due_at,
        ticketing_start_at=ticketing_start_at,
        ticketing_due_at=ticketing_due_at,
        regrant_number_due_at=regrant_number_due_at,
        tickets=build_sej_tickets_from_dicts(order_no, tickets, lambda _: None)
        )
    return sej_order
