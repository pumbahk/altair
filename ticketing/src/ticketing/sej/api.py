# -*- coding:utf-8 -*-

from datetime import datetime
from dateutil.parser import parse

from sqlalchemy import update
from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound

import sqlahelper

from .utils import JavaHashMap
from .models import SejNotification, SejOrder, SejTicket

from .helpers import make_sej_response, create_hash_from_x_start_params, build_sej_datetime
from .resources import SejNotificationType, SejPaymentType
from .exceptions import SejResponseError


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
        n.order_id              = hash_map['X_shop_order_id']
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
        n.order_id                      = hash_map['X_shop_order_id']
        n.billing_number                = hash_map['X_haraikomi_no']
        n.exchange_number               = hash_map['X_hikikae_no']
        n.payment_type_new              = str(int(hash_map['X_shori_kbn_new']))
        n.billing_number_new            = hash_map['X_haraikomi_no_new']
        n.exchange_number_new           = hash_map['X_hikikae_no_new']
        n.ticketing_due_at_new    = parse(hash_map['X_lmt_time_new'])
        n.barcode_numbers = dict()
        n.barcode_numbers['barcodes'] = list()

        for idx in range(1,20):
            n.barcode_numbers['barcodes'].append(hash_map['X_barcode_no_new_%02d' % idx])
        n.processed_at          = parse(hash_map['X_shori_time'])
        n.signature                     = hash_map['xcode']

        return make_sej_response(dict(status='800' if not retry_data else '810'))

    def process_expire():
        n.process_number                = hash_map['X_shori_id']
        n.shop_id                       = hash_map['X_shop_id']
        n.order_id                      = hash_map['X_shop_order_id']
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
                SejOrder.order_id        == notification.order_id,
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
                        SejTicket.order_id == notification.order_id
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
                SejOrder.order_id        == notification.order_id,
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
                SejOrder.order_id        == notification.order_id,
                SejOrder.exchange_number == notification.exchange_number,
                SejOrder.billing_number  == notification.billing_number
            )
    ).values(
        process_number                = notification.process_number,
        order_id                      = notification.order_id,
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
        'X_shop_order_id':      n.order_id,
        'X_haraikomi_no':       n.billing_number or '',
        'X_hikikae_no':         n.exchange_number or '',
        'X_goukei_kingaku':     n.total_price,
        'X_ticket_cnt':         n.total_ticket_count,
        'X_ticket_hon_cnt':     n.ticket_count,
        'X_kaishu_cnt':         n.return_ticket_count,
        'X_pay_mise_no':        n.pay_store_number,
        'pay_mise_name':        n.pay_store_name,
        'X_hakken_mise_no':     n.ticketing_store_number,
        'hakken_mise_name':     n.ticketing_store_name,
        'X_torikeshi_riyu':     n.cancel_reason,
        'X_shori_time':         build_sej_datetime(n.processed_at),
        }

def create_payment_complete_request_from_record(n):
    params = create_payment_or_cancel_request_from_record(n)
    params['X_tuchi_type'] = str(SejNotificationType.PaymentComplete.v)

def create_cancel_request_from_record(n):
    params = create_payment_or_cancel_request_from_record(n)
    params['X_tuchi_type'] = str(SejNotificationType.CancelFromSVC.v)

def create_re_grant_request_from_record(n):
    params = {
        'X_tuchi_type':         str(SejNotificationType.ReGrant.v),
        'X_shori_id':           n.process_number,
        'X_shop_id':            n.shop_id,
        'X_shori_kbn':          str(int(n.payment_type)),
        'X_shop_order_id':      n.order_id,
        'X_haraikomi_no':       n.billing_number or '',
        'X_hikikae_no':         n.exchange_number or '',
        'X_shori_kbn_new':      str(int(n.payment_type_new)),
        'X_haraikomi_no_new':   n.billing_number_new or '',
        'X_hikikae_no_new':     n.exchange_number_new or '',
        'X_lmt_time_new':       build_sej_datetime(n.ticketing_due_at_new),
        'X_shori_time':         build_sej_datetime(n.processed_at),
        }
    if n.barcode_numbers is not None and 'barcodes' in n.barcode_numbers:
        barcodes = n.barcode_numbers['barcodes']
        for i in range(0, 20):
            barcode = barcodes[i] if i < len(barcodes) else ''
            params['X_barcode_no_new_%02d' % (i + 1)] = barcode
    return params

def create_expire_request_from_record(n):
    return {
        'X_tuchi_type':         str(SejNotificationType.TicketingExpire.v),
        'X_shori_id':           n.process_number,
        'X_shop_id':            n.shop_id,
        'X_shop_order_id':      n.order_id,
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
    params = processor[n.notification_type](n)
    params['xcode'] = create_hash_from_x_start_params(params, secret_key)
    return params
