# -*- coding:utf-8 -*-

from datetime import timedelta
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

from collections import OrderedDict

from sqlalchemy import update
from sqlalchemy import and_
from sqlalchemy.sql.expression import asc, desc
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import make_transient

import sqlahelper

from .utils import JavaHashMap
from .models import SejOrder, SejTicket, SejRefundEvent, SejRefundTicket, ThinSejTenant, SejTicketTemplateFile, SejTicketType, SejPaymentType
from .models import _session
from .interfaces import ISejTenant, ISejNWTSUploader, ISejNWTSUploaderFactory
from .exceptions import SejServerError, SejError, SejErrorBase, RefundTotalAmountOverError
from .payment import request_cancel_order, request_order, request_update_order
from pyramid.threadlocal import get_current_registry
from pyramid.interfaces import IRequest

def do_sej_order(request, tenant, sej_order, now=None, session=None):
    if session is None:
        session = _session
    try:
        try:
            sej_order = request_order(request, tenant, sej_order)
        finally:
            versions = session.query(SejOrder.version_no).filter(SejOrder.order_no == sej_order.order_no).with_lockmode('update').order_by(desc(SejOrder.version_no)).distinct().all()
            # バージョン番号は 0 スタート
            sej_order.version_no = versions[0][0] + 1 if len(versions) > 0 else 0
            sej_order = session.merge(sej_order)
            session.commit()
    except SejErrorBase:
        raise
    except Exception as e:
        logger.exception(u'unhandled exception')
        raise SejError(u'generic failure (reason: %s)' % unicode(e), sej_order.order_no)
    return sej_order

def refresh_sej_order(request, tenant, sej_order, update_reason, now=None, session=None):
    if session is None:
        session = _session
    try:
        try:
            sej_order = request_update_order(request, tenant, sej_order, update_reason)
        finally:
            sej_order = session.merge(sej_order)
            session.commit()
    except SejErrorBase:
        raise
    except Exception as e:
        logger.exception(u'unhandled exception')
        raise SejError(u'generic failure (reason: %s)' % unicode(e), sej_order.order_no)
    return sej_order


def validate_sej_order_cancellation(request, tenant, sej_order, origin_order, now=None):
    """SejOrderバリデーション"""
    if not now:
        now = datetime.now()
    if sej_order.cancel_at is not None:
        raise SejError(u'SejOrder already canceled', sej_order.order_no)
    if sej_order.pay_at is not None:
        raise SejError(u'SejOrder already paid', sej_order.order_no)
    if sej_order.shop_id != tenant.shop_id:
        raise SejError(u'SejOrder.shop_id (%s) != SejTenant.shop_id (%s)' % (sej_order.shop_id, tenant.shop_id), sej_order.order_no)
    # 代済の時は未発券のときならキャンセルできる
    if int(sej_order.payment_type) == SejPaymentType.Paid.v and sej_order.issue_at is not None:
        raise SejError(u'SejOrder.type=Paid and already printed', sej_order.order_no)
    # コンビニ支払が発生する予約は支払期限を過ぎるとキャンセルできない
    if int(sej_order.payment_type) in (SejPaymentType.Prepayment.v, SejPaymentType.CashOnDelivery.v, SejPaymentType.PrepaymentOnly.v):
        # 本当はSejOrderの入金期限を見るべきと思うが、実際のデータは入ってない場合もあるのでOrderの期限をみるようにする
        # and sej_order.payment_due_at and sej_order.payment_due_at < now:
        if origin_order.payment_due_at and origin_order.payment_due_at < now:
            raise SejError(u'payment is overdue(Order.payment_due_at: {})'.format(origin_order.payment_due_at), origin_order.order_no)
    # コンビニ発券が発生する予約は発券期限を過ぎるとキャンセルできない
    if int(sej_order.payment_type) in (SejPaymentType.Prepayment.v, SejPaymentType.CashOnDelivery.v, SejPaymentType.Paid.v):
        # 本当はSejOrderの発券期限を見るべきと思うが、実際のデータは入ってない場合もあるのでOrderの期限をみるようにする
        # and sej_order.ticketing_due_at and sej_order.ticketing_due_at < now:
        if origin_order.issuing_end_at and origin_order.issuing_end_at < now:
            raise SejError(u'ticketing is overdue(Order.ticketing_due_at: {})'.format(origin_order.issuing_end_at), origin_order.order_no)


def cancel_sej_order(request, tenant, sej_order, origin_order, now=None, session=None):
    if session is None:
        session = _session
    try:
        validate_sej_order_cancellation(request, tenant, sej_order, origin_order, now)
        try:
            request_cancel_order(
                request,
                tenant=tenant,
                sej_order=sej_order,
                now=now
            )
        finally:
            sej_order = session.merge(sej_order)
            session.commit()
    except SejErrorBase:
        raise
    except Exception as e:
        logger.exception(u'unhandled exception')
        raise SejError(u'generic failure (reason: %s)' % unicode(e), sej_order.order_no)
    return sej_order

def refund_sej_order(request,
                     tenant,
                     sej_order,
                     performance_name,
                     performance_code,
                     performance_start_on,
                     per_order_fee,
                     per_ticket_fee,
                     ticket_price_getter,
                     refund_start_at,
                     refund_end_at,
                     need_stub,
                     ticket_expire_at,
                     refund_total_amount,
                     now,
                     session=None):
    if session is None:
        session = _session
    if sej_order.cancel_at:
        raise SejError(u'already canceled', sej_order.order_no)

    sej_tickets = sorted(sej_order.tickets, key=lambda x: x.ticket_idx)
    if not sej_tickets:
        raise SejError(u'No tickets associated', sej_order.order_no)

    try:
        # create SejRefundEvent
        re = session.query(SejRefundEvent).filter(and_(
            SejRefundEvent.shop_id==tenant.shop_id,
            SejRefundEvent.nwts_endpoint_url==tenant.nwts_endpoint_url,
            SejRefundEvent.nwts_terminal_id==tenant.nwts_terminal_id,
            SejRefundEvent.nwts_password==tenant.nwts_password,
            SejRefundEvent.event_code_01==performance_code
        )).first()
        if not re:
            re = SejRefundEvent(
                shop_id=tenant.shop_id,
                nwts_endpoint_url=tenant.nwts_endpoint_url,
                nwts_terminal_id=tenant.nwts_terminal_id,
                nwts_password=tenant.nwts_password,
                event_code_01=performance_code
                )
            session.add(re)

        re.available = 1
        re.title = performance_name
        re.event_at = performance_start_on
        re.start_at = refund_start_at
        re.end_at = refund_end_at
        re.event_expire_at = refund_end_at
        re.ticket_expire_at = ticket_expire_at
        re.refund_enabled = 1
        re.need_stub = need_stub

        # create SejRefundTicket
        i = 0
        sum_amount = 0
        for sej_ticket in sej_tickets:
            # 主券でかつバーコードがあるものだけ払戻する
            if sej_ticket.barcode_number is not None and \
               int(sej_ticket.ticket_type) in (SejTicketType.Ticket.v, SejTicketType.TicketWithBarcode.v):
                ticket_amount = ticket_price_getter(sej_ticket)
                rt = session.query(SejRefundTicket).filter(and_(
                    SejRefundTicket.order_no==sej_order.order_no,
                    SejRefundTicket.ticket_barcode_number==sej_ticket.barcode_number
                )).first()
                if not rt:
                    rt = SejRefundTicket()

                # すべてが0の場合はデータを追加しない refs #9766
                if ticket_amount == 0 and (per_order_fee == 0 or i > 0) and per_ticket_fee == 0:
                    if rt.id is not None:
                        session.delete(rt)
                    continue

                rt.available = 1
                rt.refund_event_id = re.id
                rt.event_code_01 = performance_code
                rt.order_no = sej_order.order_no
                rt.ticket_barcode_number = sej_ticket.barcode_number
                rt.refund_ticket_amount = ticket_amount
                rt.refund_other_amount = per_ticket_fee
                # 手数料などの払戻があったら1件目に含める
                if per_order_fee > 0 and i == 0:
                    rt.refund_other_amount += per_order_fee

                # チケットデータの状態不正などにより払戻データの合計額が予約金額を超える場合はエラーにする
                sum_amount += rt.refund_ticket_amount + rt.refund_other_amount
                if refund_total_amount < sum_amount:
                    logger.error(u'check over amount {0} < {1}'.format(refund_total_amount, sum_amount))
                    raise RefundTotalAmountOverError(u'refund total amount over: {0} < {1}'.format(refund_total_amount, sum_amount))

                session.add(rt)
                i += 1
        if i == 0:
            logger.warning(u'No refundable tickets found: %s' % sej_order.order_no)

        session.commit()
        return re
    except (RefundTotalAmountOverError, SejErrorBase):
        raise
    except Exception as e:
        logger.exception(u'unhandled exception')
        raise SejError(u'generic failure (reason: %s)' % unicode(e), sej_order.order_no)

def get_sej_order(order_no, fetch_canceled=False, session=None):
    if session is None:
        session = _session
    q = session.query(SejOrder) \
        .filter(SejOrder.order_no == order_no) \
        .filter(SejOrder.error_type == None) \
        .filter(SejOrder.order_at != None)
    if not fetch_canceled:
        q = q.filter(SejOrder.cancel_at == None)
    retval = q \
        .order_by(desc(SejOrder.version_no), desc(SejOrder.branch_no)) \
        .first()
    return retval

def get_sej_order_by_exchange_number_or_billing_number(order_no=None, exchange_number=None, billing_number=None, session=None):
    if session is None:
        session = _session
    if order_no is None and exchange_number is None and billing_number is None:
        raise ValueError('any of order_no, exchange_number and billing_number must be non-null value')
    q = session.query(SejOrder) \
        .filter(SejOrder.error_type == None) \
        .filter(SejOrder.order_at != None)
    if order_no is not None:
        q = q.filter_by(order_no=order_no)
    if exchange_number:
        q = q.filter_by(exchange_number=exchange_number)
    if billing_number:
        q = q.filter_by(billing_number=billing_number)
    return q.order_by(desc(SejOrder.version_no), desc(SejOrder.branch_no)).first()

def get_sej_orders(order_no, fetch_canceled=False, session=None):
    if session is None:
        session = _session
    q = session.query(SejOrder)
    q = q.filter(SejOrder.order_no == order_no) \
        .filter(SejOrder.error_type == None) \
        .filter(SejOrder.order_at != None)
    if not fetch_canceled:
        q = q.filter_by(cancel_at=None)
    q = q.order_by(desc(SejOrder.version_no), desc(SejOrder.branch_no))
    return q.all()

def get_valid_sej_orders(order_no, session=None):
    if session is None:
        session = _session
    q = session.query(SejOrder) \
        .filter(SejOrder.order_no == order_no) \
        .filter(SejOrder.error_type == None) \
        .filter(SejOrder.order_at != None) \
        .filter(SejOrder.cancel_at == None) \
        .order_by(desc(SejOrder.version_no), desc(SejOrder.branch_no))
    lists = OrderedDict()
    for sej_order in q:
        payment_type = int(sej_order.payment_type)
        if payment_type == int(SejPaymentType.CashOnDelivery):
            if not sej_order.billing_number:
                continue
            key = (sej_order.billing_number, None)
        elif payment_type == int(SejPaymentType.Prepayment):
            if not sej_order.billing_number or not sej_order.exchange_number:
                continue
            key = (sej_order.billing_number, sej_order.exchange_number)
        elif payment_type == int(SejPaymentType.Paid):
            if not sej_order.exchange_number:
                continue
            key = (None, sej_order.exchange_number)
        elif payment_type == int(SejPaymentType.PrepaymentOnly):
            if not sej_order.billing_number:
                continue
            key = (sej_order.billing_number, None)
        lists.setdefault(key, []).append(sej_order)
    return [v[0] for v in lists.values()]

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
        inticket_api_url=override_by.inticket_api_url,
        nwts_endpoint_url=override_by.nwts_endpoint_url,
        nwts_terminal_id=override_by.nwts_terminal_id,
        nwts_password=override_by.nwts_password
        )

def validate_sej_tenant(sej_tenant):
    if not sej_tenant.shop_id:
        raise AssertionError('shop_id is empty')
    if not sej_tenant.api_key:
        raise AssertionError('api_key is empty')
    if not sej_tenant.inticket_api_url:
        raise AssertionError('inticket_api_url is empty')
    if not sej_tenant.nwts_endpoint_url:
        raise AssertionError('endpoint_url is empty')
    if not sej_tenant.nwts_terminal_id:
        raise AssertionError('terminal_id is empty')
    if not sej_tenant.nwts_password:
        raise AssertionError('password is empty')

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
            ticket_data_xml      = ticket.get('xml'),
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

def get_ticket_template_record(request, template_id, session=None):
    if session is None:
        session = _session
    try:
        template_file_rec = session.query(SejTicketTemplateFile) \
            .filter(SejTicketTemplateFile.template_id == template_id) \
            .one()
        return template_file_rec
    except NoResultFound:
        return None

def get_nwts_uploader_factory(request_or_registry):
    if hasattr(request_or_registry, 'registry'):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    return registry.queryUtility(ISejNWTSUploaderFactory)
