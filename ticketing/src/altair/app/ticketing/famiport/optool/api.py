from os import urandom
import hashlib
import six
import logging
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import and_, not_, or_
from altair.sqlahelper import get_db_session
from ..models import (
    FamiPortPerformance,
    FamiPortEvent,
    FamiPortSalesSegment,
    FamiPortReceipt,
    FamiPortOrder,
    FamiPortTicket,
    FamiPortRefund,
    FamiPortRefundEntry,
    FamiPortShop
)
from .models import FamiPortOperator

logger = logging.getLogger(__name__)

def create_user(request, user_name, password, role):
    salt = u''.join('%02x' % six.byte2int(c) for c in urandom(16))
    h = hashlib.sha256()
    h.update(salt + password)
    password_digest = h.hexdigest()
    operator = FamiPortOperator(
        user_name=user_name,
        password=(salt + password_digest),
        role=role
        )
    session = get_db_session(request, 'famiport')
    session.add(operator)
    session.commit()

def lookup_user_by_credentials(request, user_name, password):
    session = get_db_session(request, 'famiport')
    try:
        operator = session.query(FamiPortOperator) \
            .filter(FamiPortOperator.user_name == user_name) \
            .one()
        h = hashlib.sha256()
        h.update(operator.password[0:32] + password)
        password_digest = h.hexdigest()
        if operator.password[32:] != password_digest:
            return None
        return operator
    except NoResultFound:
        return None

def lookup_user_by_id(request, id):
    session = get_db_session(request, 'famiport')
    try:
        return session.query(FamiPortOperator) \
            .filter(FamiPortOperator.id == id) \
            .one()
    except NoResultFound:
        return None

def lookup_performance_by_searchform_data(request, formdata=None):
    fami_session = get_db_session(request, name="famiport")

    query = fami_session.query(FamiPortPerformance) \
                        .join(FamiPortEvent, FamiPortPerformance.famiport_event_id == FamiPortEvent.id)

    if formdata.get('event_id'):
        query = query.filter(FamiPortEvent.id==formdata.get('event_id'))

    if formdata.get('event_code_1'):
        query = query.filter(FamiPortEvent.code_1==formdata.get('event_code_1').zfill(6))
    if formdata.get('event_code_2'):
        query = query.filter(FamiPortEvent.code_2==formdata.get('event_code_2').zfill(4))

    if formdata.get('event_name_1'):
        pattern = u'%{}%'.format(formdata.get('event_name_1'))
        query = query.filter(FamiPortEvent.name_1.like(pattern))

    if formdata.get('performance_name'):
        pattern = u'%{}%'.format(formdata.get('performance_name'))
        query = query.filter(FamiPortPerformance.name.like(pattern))

    if formdata.get('venue_name'):
        pattern = u'%{}%'.format(formdata.get('venue_name'))
        query = query.filter(FamiPortEvent.venue.like(pattern))

    if formdata.get('performance_from'):
        req_from = formdata.get('performance_from') + ' 00:00:00'
        if formdata.get('performance_to'):
            req_to = formdata.get('performance_to') + ' 23:59:59'
            query = query.filter(FamiPortPerformance.start_at >= req_from,
                                 FamiPortPerformance.start_at <= req_to)
        else:
            query = query.filter(FamiPortPerformance.start_at >= req_from)
    elif formdata.get('performance_to'):
        req_from = '1900-01-01 00:00:00'
        req_to = formdata.get('performance_to') + ' 23:59:59'
        query = query.filter(FamiPortPerformance.start_at >= req_from,
                             FamiPortPerformance.start_at <= req_to)

    performances = query.all()
    return performances

def lookup_refund_performance_by_searchform_data(request, formdata=None):
    fami_session = get_db_session(request, name='famiport')
    query = fami_session.query(FamiPortRefundEntry, FamiPortPerformance)\
                        .join(FamiPortTicket, FamiPortTicket.id == FamiPortRefundEntry.famiport_ticket_id)\
                        .join(FamiPortRefund, FamiPortRefundEntry.famiport_refund_id == FamiPortRefund.id)\
                        .join(FamiPortOrder, FamiPortOrder.id == FamiPortTicket.famiport_order_id)\
                        .join(FamiPortSalesSegment, FamiPortSalesSegment.id == FamiPortOrder.famiport_sales_segment_id)\
                        .join(FamiPortPerformance, FamiPortPerformance.id == FamiPortSalesSegment.famiport_performance_id)\
                        .join(FamiPortEvent, FamiPortEvent.id == FamiPortPerformance.famiport_event_id)\
                        .group_by(FamiPortPerformance.id, FamiPortRefund.start_at, FamiPortRefund.end_at, FamiPortRefund.send_back_due_at)

    before_refund = formdata.get('before_refund')
    during_refund = formdata.get('during_refund')
    after_refund = formdata.get('after_refund')
    performance_from = formdata.get('performance_from')
    performance_to = formdata.get('performance_to')

    if before_refund and during_refund and after_refund:
        pass
    elif before_refund and during_refund: # <=> Not after_refund
        query = query.filter(not_(FamiPortRefund.end_at < datetime.now()))
    elif during_refund and after_refund: # <=> Not before_refund
        query = query.filter(not_(FamiPortRefund.start_at > datetime.now()))
    elif before_refund and after_refund: # <=> Not during_refund
        query = query.filter(not_(and_(FamiPortRefund.start_at < datetime.now(), datetime.now() < FamiPortRefund.end_at)))
    elif before_refund:
        query = query.filter(FamiPortRefund.start_at > datetime.now())
    elif during_refund:
        query = query.filter(and_(FamiPortRefund.start_at < datetime.now(), datetime.now() < FamiPortRefund.end_at))
    elif after_refund:
        query = query.filter(FamiPortRefund.end_at < datetime.now())

    if performance_from:
        query = query.filter(performance_from <= FamiPortPerformance.start_at)
    if performance_to:
        query = query.filter(FamiPortPerformance.start_at <= performance_to)

    performances = query.all()
    return performances

def lookup_receipt_by_searchform_data(request, formdata=None):
    fami_session = get_db_session(request, name="famiport")

    query = fami_session.query(FamiPortReceipt) \
                        .join(FamiPortOrder, FamiPortReceipt.famiport_order_id == FamiPortOrder.id) \
                        .join(FamiPortSalesSegment, FamiPortOrder.famiport_sales_segment_id == FamiPortSalesSegment.id) \
                        .join(FamiPortTicket, FamiPortOrder.id == FamiPortTicket.famiport_order_id) \
                        .outerjoin(FamiPortShop, FamiPortReceipt.shop_code == FamiPortShop.code) \
                        .group_by(FamiPortReceipt.id)

    if formdata.get('barcode_no'):
        query = query.filter(FamiPortReceipt.barcode_no == formdata.get('barcode_no'))
    if formdata.get('reserve_number'):
        query = query.filter(FamiPortReceipt.reserve_number == formdata.get('reserve_number'))
    if formdata.get('management_number'):
        pattern = u'%{}'.format(formdata.get('management_number'))
        query = query.filter(or_(FamiPortOrder.famiport_order_identifier.like(pattern), FamiPortReceipt.famiport_order_identifier.like(pattern)))
    if formdata.get('barcode_number'):
        pattern = u'%{}'.format(formdata.get('barcode_number'))
        query = query.filter(FamiPortTicket.barcode_number.like(pattern))
    if formdata.get('customer_phone_number'):
        query = query.filter(FamiPortOrder.customer_phone_number == formdata.get('customer_phone_number'))
    if formdata.get('shop_code'):
        query = query.filter(FamiPortReceipt.shop_code == formdata.get('shop_code'))
    if formdata.get('shop_name'):
        pattern = u'%{}%'.format(formdata.get('shop_name'))
        query = query.filter(FamiPortShop.name.like(pattern))
    if formdata.get('sales_from'):
        req_from = formdata.get('sales_from') + ' 00:00:00'
        if formdata.get('sales_to'):
            req_to = formdata.get('sales_to') + ' 23:59:59'
            query = query.filter(FamiPortSalesSegment.start_at >= req_from,
                                 FamiPortSalesSegment.start_at <= req_to)
        else:
            query = query.filter(FamiPortSalesSegment.start_at >= req_from)
    elif formdata.get('sales_to'):
        req_from = '1900-01-01 00:00:00'
        req_to = formdata.get('sales_to') + ' 23:59:59'
        query = query.filter(FamiPortSalesSegment.start_at >= req_from,
                             FamiPortSalesSegment.start_at <= req_to)

    receipts = query.all()
    return receipts

def search_refund_ticket_by(request, params):
    session = get_db_session(request, 'famiport')
    query = session.query(FamiPortRefundEntry).join(FamiPortTicket, FamiPortTicket.id == FamiPortRefundEntry.famiport_ticket_id)\
                                              .join(FamiPortRefund, FamiPortRefundEntry.famiport_refund_id == FamiPortRefund.id)\
                                              .join(FamiPortOrder, FamiPortOrder.id == FamiPortTicket.famiport_order_id)\
                                              .join(FamiPortSalesSegment, FamiPortSalesSegment.id == FamiPortOrder.famiport_sales_segment_id)\
                                              .join(FamiPortPerformance, FamiPortPerformance.id == FamiPortSalesSegment.famiport_performance_id)\
                                              .join(FamiPortEvent, FamiPortEvent.id == FamiPortPerformance.famiport_event_id)

    before_refund = params.get('before_refund', None)
    during_refund = params.get('during_refund', None)
    after_refund = params.get('after_refund', None)
    management_number = params.get('management_number', None)
    barcode_number = params.get('barcode_number', None)
    refunded_shop_code = params.get('refunded_shop_code', None)
    event_code = params.get('event_code', None)
    event_subcode = params.get('event_subcode', None)
    str_performance_start_date = params.get('performance_start_date', '')
    performance_start_date = datetime.strptime(str_performance_start_date, "%Y-%m-%d") if str_performance_start_date else str_performance_start_date
    str_performance_end_date = params.get('performance_end_date', '')
    performance_end_date = datetime.strptime(str_performance_end_date, "%Y-%m-%d") if str_performance_end_date else str_performance_end_date

    if (before_refund and during_refund and after_refund) or not (before_refund or during_refund or after_refund):
        pass
    elif before_refund and during_refund: # <=> Not after_refund
        query = query.filter(not_(FamiPortRefund.end_at < datetime.now()))
    elif during_refund and after_refund: # <=> Not before_refund
        query = query.filter(not_(FamiPortRefund.start_at > datetime.now()))
    elif before_refund and after_refund: # <=> Not during_refund
        query = query.filter(not_(and_(FamiPortRefund.start_at < datetime.now(), datetime.now() < FamiPortRefund.end_at)))
    elif before_refund:
        query = query.filter(FamiPortRefund.start_at > datetime.now())
    elif during_refund:
        query = query.filter(and_(FamiPortRefund.start_at < datetime.now(), datetime.now() < FamiPortRefund.end_at))
    elif after_refund:
        query = query.filter(FamiPortRefund.end_at < datetime.now())

    if barcode_number:
        query = query.filter(FamiPortTicket.barcode_number == barcode_number)
    if management_number:
        query = query.filter(FamiPortOrder.famiport_order_identifier.endswith(management_number))
    if refunded_shop_code:
        query = query.filter(FamiPortRefundEntry.shop_code == refunded_shop_code)
    if event_code:
        query = query.filter(FamiPortEvent.code_1 == event_code)
    if event_subcode:
        query = query.filter(FamiPortEvent.code_2 == event_subcode)
    if performance_start_date:
        query = query.filter(performance_start_date <= FamiPortPerformance.start_at)
    if performance_end_date:
        query = query.filter(FamiPortPerformance.start_at <= performance_end_date)
    query = query.order_by(FamiPortRefundEntry.refunded_at)
    return query.all()

def get_famiport_shop_by_code(request, shop_code):
    session = get_db_session(request, 'famiport')
    return FamiPortShop.get_by_code(shop_code, session)