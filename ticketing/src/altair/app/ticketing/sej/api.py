# -*- coding:utf-8 -*-

from dateutil.parser import parse
from datetime import timedelta
import logging
logger = logging.getLogger(__name__)

from sqlalchemy import update
from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound

import sqlahelper

from .utils import JavaHashMap
from .models import SejNotification, SejOrder, SejTicket, SejTenant, SejRefundEvent, SejRefundTicket, SejNotificationType

from .helpers import make_sej_response, create_hash_from_x_start_params, build_sej_datetime
from .exceptions import SejResponseError
from altair.app.ticketing.sej.exceptions import SejServerError
from altair.app.ticketing.sej.payment import request_cancel_order
from pyramid.threadlocal import get_current_registry

DBSession = sqlahelper.get_session()

def callback_notification(params,
                          secret_key = u'E6PuZ7Vhe7nWraFW'):

    hash_map = JavaHashMap()
    for k,v in params.items():
        hash_map[k] = v

    hash = create_hash_from_x_start_params(hash_map, secret_key)

    if hash != params.get('xcode'):
        raise SejResponseError(
            400, 'Bad Request',dict(status='400', Error_Type='00', Error_Msg='Bad Value', Error_Field='xcode'))

    process_number = params.get('X_shori_id')
    if not process_number:
        raise SejResponseError(
             400, 'Bad Request',dict(status='422', Error_Type='01', Error_Msg='No Data', Error_Field='X_shori_id'))

    retry_data = False
    q = SejNotification.query.filter_by(process_number = process_number)
    if q.count():
        n = q.one()
        retry_data = True
    else:
        n = SejNotification()
        DBSession.add(n)

    def process_payment_complete():
        '''3-1.入金発券完了通知'''
        n.process_number        = hash_map['X_shori_id']
        n.shop_id               = hash_map['X_shop_id']
        n.payment_type          = str(int(hash_map['X_shori_kbn']))
        n.order_no              = hash_map['X_shop_order_id']
        n.billing_number        = hash_map['X_haraikomi_no']
        n.exchange_number       = hash_map['X_hikikae_no']
        n.total_price           = hash_map['X_goukei_kingaku']
        n.total_ticket_count    = hash_map['X_ticket_cnt']
        n.ticket_count          = hash_map['X_ticket_hon_cnt']
        n.return_ticket_count   = hash_map['X_kaishu_cnt']
        n.pay_store_number      = hash_map['X_pay_mise_no']
        n.pay_store_name        = hash_map['pay_mise_name']
        n.ticketing_store_number= hash_map['X_hakken_mise_no']
        n.ticketing_store_name  = hash_map['hakken_mise_name']
        n.cancel_reason         = hash_map['X_torikeshi_riyu']
        n.processed_at          = parse(hash_map['X_shori_time'])
        n.signature             = hash_map['xcode']
        return make_sej_response(dict(status='800' if not retry_data else '810'))


    def process_re_grant():
        n.process_number                = hash_map['X_shori_id']
        n.shop_id                       = hash_map['X_shop_id']
        n.payment_type                  = str(int(hash_map['X_shori_kbn']))
        n.order_no                      = hash_map['X_shop_order_id']
        n.billing_number                = hash_map['X_haraikomi_no']
        n.exchange_number               = hash_map['X_hikikae_no']
        n.payment_type_new              = str(int(hash_map['X_shori_kbn_new']))
        n.billing_number_new            = hash_map['X_haraikomi_no_new']
        n.exchange_number_new           = hash_map['X_hikikae_no_new']
        n.ticketing_due_at_new    = parse(hash_map['X_lmt_time_new'])
        n.barcode_numbers = dict()

        for idx in range(1, 20):
            barcode_number = hash_map['X_barcode_no_new_%02d' % idx]
            if barcode_number:
                n.barcode_numbers[idx] = barcode_number
        n.processed_at          = parse(hash_map['X_shori_time'])
        n.signature                     = hash_map['xcode']

        return make_sej_response(dict(status='800' if not retry_data else '810'))

    def process_expire():
        n.process_number                = hash_map['X_shori_id']
        n.shop_id                       = hash_map['X_shop_id']
        n.order_no                      = hash_map['X_shop_order_id']
        n.payment_type                  = str(int(hash_map['X_shori_kbn']))
        n.ticketing_due_at              = parse(hash_map['X_lmt_time'])
        n.billing_number                = hash_map['X_haraikomi_no']
        n.exchange_number               = hash_map['X_hikikae_no']
        n.processed_at                  = parse(hash_map['X_shori_time'])
        n.signature                     = hash_map['xcode']

        return make_sej_response(dict(status='800' if not retry_data else '810'))

    def dummy():
        raise SejResponseError(
             422, 'Bad Request',dict(status='422', Error_Type='01', Error_Msg='Bad Value', Error_Field='X_tuchi_type'))

    ret = {
        SejNotificationType.PaymentComplete.v   : process_payment_complete,
        SejNotificationType.CancelFromSVC.v     : process_payment_complete,
        SejNotificationType.ReGrant.v           : process_re_grant,
        SejNotificationType.TicketingExpire.v   : process_expire,
    }.get(int(params['X_tuchi_type']), dummy)()
    n.notification_type = str(int(params['X_tuchi_type']))

    DBSession.flush()

    return ret


def reflect_re_grant(notification):

    update(SejOrder)\
        .where(
            and_(
                SejOrder.shop_id         == notification.shop_id,
                SejOrder.order_no        == notification.order_no,
                SejOrder.exchange_number == notification.exchange_number,
                SejOrder.billing_number  == notification.billing_number
            )
    ).values(
        process_number          = notification.process_number,
        payment_type            = notification.payment_type_new,
        billing_number          = notification.billing_number_new,
        exchange_number         = notification.exchange_number_new,
        ticketing_due_at        = notification.ticketing_due_at_new,
        processed_at            = notification.processed_at,
    )

    for idx in range(1,20):
        barcode_number = notification.barcode_numbers['barcodes'][idx]
        if barcode_number:
            update(SejTicket)\
                .where(
                    and_(
                        SejTicket.barcode_number == barcode_number,
                        SejTicket.order_no == notification.order_no
                    )
            ).values(
                barcode_number = barcode_number
            )

def reflect_payment_complete (notification):
    cancel_at = None
    if notification.notification_type == SejNotificationType.CancelFromSVC:
        cancel_at = notification.processed_at

    update(SejOrder)\
        .where(
            and_(
                SejOrder.shop_id         == notification.shop_id,
                SejOrder.order_no        == notification.order_no,
                SejOrder.exchange_number == notification.exchange_number,
                SejOrder.billing_number  == notification.billing_number
            )
    ).values(
        process_number          = notification.process_number,
        payment_type            = notification.shop_id,
        total_price             = notification.total_price,
        total_ticket_count      = notification.total_ticket_count,
        ticket_count            = notification.ticket_count,
        return_ticket_count     = notification.return_ticket_count,
        pay_store_number        = notification.pay_store_number,
        pay_store_name          = notification.pay_store_name,
        ticketing_store_number  = notification.ticketing_store_number,
        ticketing_store_name    = notification.ticketing_store_name,
        cancel_reason           = notification.cancel_reason,
        processed_at            = notification.processed_at,
        cancel_at               = cancel_at
    )

def reflect_expire(notification):

    update(SejOrder)\
        .where(
            and_(
                SejOrder.shop_id         == notification.shop_id,
                SejOrder.order_no        == notification.order_no,
                SejOrder.exchange_number == notification.exchange_number,
                SejOrder.billing_number  == notification.billing_number
            )
    ).values(
        process_number                = notification.process_number,
        order_no                      = notification.order_no,
        ticketing_due_at              = notification.ticketing_due_at,
        billing_number                = notification.billing_number,
        exchange_number               = notification.exchange_number,
        processed_at                  = notification.processed_at
    )


def process_notification():

    while True:
        try:
            notifications = SejNotification.filter(
                SejNotification.reflected_at == None
            ).limit(500).all()

            for notification in notifications:
                if notification.notification_type == SejNotificationType.InstantPaymentInfo or\
                    notification.notification_type == SejNotificationType.CancelFromSVC:
                    reflect_payment_complete(notification)
                if notification.notification_type == SejNotificationType.ReGrant:
                    reflect_re_grant(notification)
                if notification.notification_type == SejNotificationType.TicketingExpire:
                    reflect_expire(notification)

        except NoResultFound, e:
            break

def create_payment_or_cancel_request_from_record(n):
    return {
        'X_shori_id':           n.process_number,
        'X_shop_id':            n.shop_id,
        'X_shori_kbn':          str(int(n.payment_type)),
        'X_shop_order_id':      n.order_no,
        'X_haraikomi_no':       n.billing_number or '',
        'X_hikikae_no':         n.exchange_number or '',
        'X_goukei_kingaku':     str(n.total_price),
        'X_ticket_cnt':         str(n.total_ticket_count),
        'X_ticket_hon_cnt':     str(n.ticket_count),
        'X_pay_mise_no':        n.pay_store_number,
        'pay_mise_name':        n.pay_store_name,
        'X_hakken_mise_no':     n.ticketing_store_number,
        'hakken_mise_name':     n.ticketing_store_name,
        'X_shori_time':         build_sej_datetime(n.processed_at),
        }

def create_payment_complete_request_from_record(n):
    params = create_payment_or_cancel_request_from_record(n)
    params['X_tuchi_type'] = str(SejNotificationType.PaymentComplete.v)
    return params

def create_cancel_request_from_record(n):
    params = create_payment_or_cancel_request_from_record(n)
    params['X_torikeshi_riyu'] = n.cancel_reason
    params['X_tuchi_type'] = str(SejNotificationType.CancelFromSVC.v)
    params['X_kaishu_cnt'] = str(n.return_ticket_count)
    return params

def create_re_grant_request_from_record(n):
    params = {
        'X_tuchi_type':         str(SejNotificationType.ReGrant.v),
        'X_shori_id':           n.process_number,
        'X_shop_id':            n.shop_id,
        'X_shori_kbn':          str(int(n.payment_type)),
        'X_shop_order_id':      n.order_no,
        'X_haraikomi_no':       n.billing_number or '',
        'X_hikikae_no':         n.exchange_number or '',
        'X_shori_kbn_new':      str(int(n.payment_type_new)),
        'X_haraikomi_no_new':   n.billing_number_new or '',
        'X_hikikae_no_new':     n.exchange_number_new or '',
        'X_lmt_time_new':       build_sej_datetime(n.ticketing_due_at_new),
        'X_shori_time':         build_sej_datetime(n.processed_at),
        }
    if n.barcode_numbers is not None:
        for i in range(0, 20):
            barcode_number = n.barcode_numbers.get(i + 1)
            if barcode_number:
                params['X_barcode_no_new_%02d' % (i + 1)] = barcode_number
    return params

def create_expire_request_from_record(n):
    return {
        'X_tuchi_type':         str(SejNotificationType.TicketingExpire.v),
        'X_shori_id':           n.process_number,
        'X_shop_id':            n.shop_id,
        'X_shop_order_id':      n.order_no,
        'X_shori_kbn':          str(n.payment_type),
        'X_lmt_time':           build_sej_datetime(n.ticketing_due_at),
        'X_haraikomi_no':       n.billing_number or '',
        'X_hikikae_no':         n.exchange_number or '',
        'X_shori_time':         build_sej_datetime(n.processed_at),
        }

def create_sej_notification_data_from_record(n, secret_key):
    """for testing"""
    processor = {
        SejNotificationType.PaymentComplete.v:
            create_payment_complete_request_from_record,
        SejNotificationType.CancelFromSVC.v:
            create_cancel_request_from_record,
        SejNotificationType.ReGrant.v:
            create_re_grant_request_from_record,
        SejNotificationType.TicketingExpire.v:
            create_expire_request_from_record,
        }
    params = processor[int(n.notification_type)](n)
    params['xcode'] = create_hash_from_x_start_params(params, secret_key)
    return params

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
