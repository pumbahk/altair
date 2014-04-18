# -*- coding:utf-8 -*-

from datetime import timedelta
import logging
logger = logging.getLogger(__name__)

from sqlalchemy import update
from sqlalchemy import and_
from sqlalchemy.sql.expression import asc, desc
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import make_transient

import sqlahelper

from .utils import JavaHashMap
from .models import SejNotification, SejOrder, SejTicket, SejRefundEvent, SejRefundTicket, SejNotificationType, ThinSejTenant
from .models import _session
from .interfaces import ISejTenant
from .exceptions import SejServerError, SejError, SejErrorBase
from .payment import request_cancel_order, request_order, request_update_order
from pyramid.threadlocal import get_current_registry
from pyramid.interfaces import IRequest

def do_sej_order(request, tenant, sej_order, now=None, session=None):
    if session is None:
        session = _session
    try:
        try:
            return request_order(request, tenant, sej_order)
        finally:
            session.merge(sej_order)
            session.commit()
    except SejErrorBase:
        raise
    except Exception as e:
        logger.exception(u'unhandled exception')
        raise SejError(u'generic failure (reason: %s)' % unicode(e), sej_order.order_no)

def refresh_sej_order(request, tenant, sej_order, update_reason, now=None, session=None):
    if session is None:
        session = _session
    try:
        try:
            return request_update_order(request, tenant, sej_order, update_reason)
        finally:
            session.merge(sej_order)
            session.commit()
    except SejErrorBase:
        raise
    except Exception as e:
        logger.exception(u'unhandled exception')
        raise SejError(u'generic failure (reason: %s)' % unicode(e), sej_order.order_no)

def cancel_sej_order(request, tenant, sej_order, now=None, session=None):
    if session is None:
        session = _session
    if sej_order.cancel_at is not None:
        raise SejError(u'already canceled', sej_order.order_no)
    if sej_order.shop_id != tenant.shop_id:
        raise SejError(u'SejOrder.shop_id (%s) != SejTenant.shop_id (%s)' % (sej_order.shop_id, tenant.shop_id), sej_order.order_no)
    try:
        try:
            request_cancel_order(
                request,
                tenant=tenant,
                sej_order=sej_order,
                now=now
            )
        finally:
            session.merge(sej_order)
            session.commit()
    except SejErrorBase:
        raise
    except Exception as e:
        logger.exception(u'unhandled exception')
        raise SejError(u'generic failure (reason: %s)' % unicode(e), sej_order.order_no)

def refund_sej_order(request, tenant, sej_order, performance_name, performance_code, performance_start_on, per_order_fee, per_ticket_fee, ticket_price_getter, refund_start_at, refund_end_at, ticket_expire_at, now, session=None):
    if session is None:
        session = _session
    if sej_order.cancel_at:
        raise SejError(u'already canceled', sej_order.order_no)

    sej_tickets = sorted(sej_order.tickets, key=lambda x: x.ticket_idx)
    if not sej_tickets:
        raise SejError(u'No tickets associated', sej_order.order_no)

    try:
        try:
            # create SejRefundEvent
            re = session.query(SejRefundEvent).filter(and_(
                SejRefundEvent.shop_id==tenant.shop_id,
                SejRefundEvent.event_code_01==performance_code
            )).first()
            if not re:
                re = SejRefundEvent()

            re.available = 1
            re.shop_id = tenant.shop_id
            re.event_code_01 = performance_code
            re.title = performance_name
            re.event_at = performance_start_on
            re.start_at = refund_start_at
            re.end_at = refund_end_at
            re.event_expire_at = refund_end_at
            re.ticket_expire_at = ticket_expire_at
            re.refund_enabled = 1
            re.need_stub = 1
            session.merge(re)

            # create SejRefundTicket
            for i, sej_ticket in enumerate(sej_tickets):
                rt = session.query(SejRefundTicket).filter(and_(
                    SejRefundTicket.order_no==sej_order.order_no,
                    SejRefundTicket.ticket_barcode_number==sej_ticket.barcode_number
                )).first()
                if not rt:
                    rt = SejRefundTicket()
                    session.add(rt)

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

                session.merge(rt)
        finally:
            session.commit()
    except SejErrorBase:
        raise
    except Exception as e:
        logger.exception(u'unhandled exception')
        raise SejError(u'generic failure (reason: %s)' % unicode(e), sej_order.order_no)

def get_sej_order(order_no, session=None):
    if session is None:
        session = _session 
    retval = session.query(SejOrder) \
        .filter_by(order_no=order_no) \
        .order_by(desc(SejOrder.branch_no)) \
        .first()
    return retval

def get_sej_orders(order_no, fetch_canceled=False, session=None):
    if session is None:
        session = _session
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

def remove_default_session():
    _session.remove()
