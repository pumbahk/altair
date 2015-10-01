# -*- coding:utf-8 -*-

import hashlib, re
import logging

import tempfile
from zlib import decompress
from datetime import datetime
from dateutil.parser import parse
from pyramid.interfaces import IRequest

from .utils import JavaHashMap
from .models import (
    is_ticket,
    need_ticketing,
    SejOrder,
    SejTicket,
    SejOrderUpdateReason,
    SejPaymentType,
    SejTicketType,
    code_from_payment_type,
    code_from_ticket_type
    )
from .exceptions import SejServerError, SejError
from .interfaces import ISejPaymentAPICommunicatorFactory
from .payload import build_sej_datetime_without_second, build_sej_date
from .ticket import SejTicketDataXml

logger = logging.getLogger(__name__)

def create_communicator(request_or_registry, tenant, path):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    factory = registry.getUtility(ISejPaymentAPICommunicatorFactory)
    return factory(tenant, path)

def create_sej_request_data(
        order_no,
        total_price,
        ticket_price,
        commission_fee,
        payment_type,
        ticketing_fee,
        payment_due_at,
        ticketing_start_at,
        ticketing_due_at,
        regrant_number_due_at,
        tickets,
        user_name=None,
        user_name_kana=None,
        tel=None,
        zip_code=None,
        email=None):

    params = JavaHashMap()
    # 注文ID
    if order_no is not None:
        params['X_shop_order_id']   = order_no

    if int(payment_type) == int(SejPaymentType.Paid):
        assert payment_due_at is None, '%s is not None' % payment_due_at
        x_ticket_daikin = 0
        x_ticket_kounyu_daikin = 0
        x_hakken_daikin = 0
        x_goukei_kingaku = 0
        x_pay_lmt = None
    else:
        x_ticket_daikin = ticket_price
        x_ticket_kounyu_daikin = commission_fee
        x_hakken_daikin = ticketing_fee
        x_goukei_kingaku = x_ticket_daikin + x_ticket_kounyu_daikin + x_hakken_daikin
        x_pay_lmt = payment_due_at and build_sej_datetime_without_second(payment_due_at)
        assert x_goukei_kingaku == total_price, "%s != %s" % (x_goukei_kingaku, total_price)

    if x_pay_lmt is not None:
        # 支払い期限
        params['X_pay_lmt']          = x_pay_lmt
    # チケット代金
    params['X_ticket_daikin']        = u'%06d' % x_ticket_daikin
    # チケット購入代金
    params['X_ticket_kounyu_daikin'] = u'%06d' % x_ticket_kounyu_daikin
    # 発券代金
    params['X_hakken_daikin']        = u'%06d' % x_hakken_daikin
    # 合計金額 = チケット代金 + チケット購入代金+発券代金の場合
    params['X_goukei_kingaku']       = u'%06d' % x_goukei_kingaku

    # 前払い
    if int(payment_type) in (int(SejPaymentType.Prepayment), int(SejPaymentType.Paid)):
        # 支払いと発券が異なる場合、発券開始日時と発券期限を指定できる。
        if ticketing_start_at is not None:
            params['X_hakken_mise_date'] = build_sej_datetime_without_second(ticketing_start_at)
            # 発券開始日時状態フラグ
        else:
            params['X_hakken_mise_date_sts'] = u'1'

        if ticketing_due_at is not None:
            # 発券期限日時状態フラグ
            params['X_hakken_lmt']      = build_sej_datetime_without_second(ticketing_due_at)
        else:
            # 発券期限日時
            params['X_hakken_lmt_sts'] = u'1'
    #else:
    #    if ticketing_start_at is not None:
    #        params['X_hakken_mise_date'] = build_sej_datetime_without_second(ticketing_start_at)
    #    if ticketing_due_at is not None:
    #        # 発券開始日時状態フラグ
    #        params['X_hakken_lmt']      = build_sej_datetime_without_second(ticketing_due_at)

    ticket_num = 0
    e_ticket_num = 0

    for ticket in tickets:
        if not isinstance(ticket['performance_datetime'], datetime):
            raise ValueError('performance_datetime : %s' % ticket['performance_datetime'])
        if is_ticket(ticket['ticket_type']):
            ticket_num+=1
        else:
            e_ticket_num+=1

    if need_ticketing(payment_type):
        params['X_saifuban_hakken_lmt'] = build_sej_datetime_without_second(regrant_number_due_at)
    else:
        tickets=[]
        ticket_num = 0
        e_ticket_num = 0

    params['X_ticket_cnt']          = u'%02d' % len(tickets)
    params['X_ticket_hon_cnt']      = u'%02d' % ticket_num

    idx = 1

    if need_ticketing(payment_type):
        for ticket in tickets:
            # 発券がある場合
            params['X_ticket_kbn_%02d' % idx]       = u'%d' % ticket['ticket_type'].v

            if is_ticket(ticket['ticket_type']):
                # 本券の場合必須項目
                if ticket['event_name'] is None or len(ticket['event_name']) == 0:
                    raise ValueError('event_name is required')
                params['kougyo_mei_%02d' % idx]     = ticket['event_name']

            params['kouen_mei_%02d' % idx]          = ticket['performance_name']
            params['X_kouen_date_%02d' % idx]       = build_sej_datetime_without_second(ticket['performance_datetime'])
            params['X_ticket_template_%02d' % idx]  = ticket['ticket_template_id']
            params['ticket_text_%02d' % idx]        = unicode(SejTicketDataXml(ticket['xml']))
            idx+=1

    # お客様氏名
    if user_name is not None:
        params['user_namek']        = user_name
    # お客様氏名カナ
    if user_name_kana is not None:
        params['user_name_kana']    = user_name_kana
    # お客様電話番号
    if tel is not None:
        params['X_user_tel_no']     = tel
    #　お客様郵便番号
    if zip_code is not None:
        params['X_user_post']       = zip_code
    # お客様メールアドレス
    if email is not None:
        params['X_user_email']      = email
    return params

def request_order(request_or_registry, tenant, sej_order, now=None):
    """決済要求 https://inticket.sej.co.jp/order/order.do"""
    if now is None:
        now = datetime.now()
    ticket_dict = dict(
        (ticket.ticket_idx, ticket)
        for ticket in sej_order.tickets
        )
    sej_order.total_ticket_count = len(ticket_dict)
    sej_order.shop_id = tenant.shop_id

    assert int(sej_order.payment_type) == int(SejPaymentType.PrepaymentOnly) or \
           (
                len(ticket_dict) == sej_order.total_ticket_count and
                sej_order.total_ticket_count <= 20
                ), \
           '%d == %d and %d < 20' % (len(ticket_dict), sej_order.total_ticket_count, sej_order.total_ticket_count)

    payment_due_at = sej_order.payment_due_at
    if int(sej_order.payment_type) == int(SejPaymentType.Paid):
        payment_due_at = None

    payment = create_communicator(request_or_registry, tenant, '/order/order.do')
    params = create_sej_request_data(
        order_no=sej_order.order_no,
        total_price=sej_order.total_price,
        ticket_price=sej_order.ticket_price,
        commission_fee=sej_order.commission_fee,
        payment_type=sej_order.payment_type,
        ticketing_fee=sej_order.ticketing_fee,
        payment_due_at=payment_due_at,
        ticketing_start_at=sej_order.ticketing_start_at,
        ticketing_due_at=sej_order.ticketing_due_at,
        regrant_number_due_at=sej_order.regrant_number_due_at,
        user_name=sej_order.user_name,
        user_name_kana=sej_order.user_name_kana,
        tel=sej_order.tel,
        zip_code=sej_order.zip_code,
        email=sej_order.email,
        tickets=[
            dict(
                ticket_type=code_from_ticket_type[int(ticket.ticket_type)],
                event_name=ticket.event_name,
                performance_name=ticket.performance_name,
                performance_datetime=ticket.performance_datetime,
                ticket_template_id=ticket.ticket_template_id,
                xml=ticket.ticket_data_xml,
                product_item_id=ticket.product_item_id
                )
            for ticket in sorted(ticket_dict.values(), lambda a, b: cmp(a.ticket_idx, b.ticket_idx))
            ]
        )

    params['shop_namek']        = tenant.shop_name
    # 連絡先1

    params['X_renraku_saki']    = tenant.contact_01
    # 連絡先2
    params['renraku_saki']      = tenant.contact_02
    # 処理区分
    params['X_shori_kbn']       = u'%02d' % int(sej_order.payment_type)

    ret = payment.request(params, 0)
    # example response
    # {
    #   'X_haraikomi_no': '2306667473026',
    #   'X_ticket_cnt': '03',
    #   'X_url_info': 'https://www.r1test.com/order/hi.do',
    #   'X_shop_order_id': 'orderid00001',
    #   'iraihyo_id_00': '3052030666747302c21b35696fdd51ca',
    #   'DATA': 'END',
    #   'X_ticket_hon_cnt': '01'
    # }

    error_type = ret.get('Error_Type', 0)
    if error_type:
        error_message = ret.get('Error_Msg', None)
        error_field = ret.get('Error_Field', None)
        sej_order.error_type = int(error_type)
        sej_order.order_at = None
        raise SejError(
            message=error_message,
            order_no=sej_order.order_no,
            error_type=int(error_type),
            error_field=error_field
            )

    sej_order.billing_number        = ret.get('X_haraikomi_no')
    sej_order.total_ticket_count    = int(ret.get('X_ticket_cnt', 0))
    sej_order.ticket_count          = int(ret.get('X_ticket_hon_cnt', 0))
    sej_order.exchange_sheet_url    = ret.get('X_url_info')
    sej_order.order_no              = ret.get('X_shop_order_id')
    sej_order.exchange_sheet_number = ret.get('iraihyo_id_00')
    sej_order.exchange_number       = ret.get('X_hikikae_no')
    sej_order.total_price           = int(params.get('X_goukei_kingaku', 0))
    sej_order.ticket_price          = int(params.get('X_ticket_daikin', 0))
    sej_order.commission_fee        = int(params.get('X_ticket_kounyu_daikin',0))
    sej_order.ticketing_fee         = int(params.get('X_hakken_daikin',0))
    sej_order.payment_due_at        = payment_due_at
    sej_order.order_at              = now
    sej_order.updated_at            = sej_order.order_at

    for idx in range(1, 21):
        ticket = ticket_dict.get(idx)
        barcode_number = ret.get('X_barcode_no_%02d' % idx)
        if not ticket:
            continue
        ticket.barcode_number = barcode_number

    return sej_order

def request_cancel_order(request_or_registry, tenant, sej_order, now=None):
    '''
    注文キャンセル https://inticket.sej.co.jp/order/cancelorder.do
    '''
    if now is None:
        now = datetime.now()
    payment = create_communicator(request_or_registry, tenant, '/order/cancelorder.do')
    params = JavaHashMap()
    params['X_shop_order_id']   = sej_order.order_no
    if sej_order.billing_number:
        params['X_haraikomi_no'] = sej_order.billing_number
    if sej_order.exchange_number:
        params['X_hikikae_no']   = sej_order.exchange_number

    ret = payment.request(params)

    error_type = ret.get('Error_Type', 0)
    if error_type:
        error_message = ret.get('Error_Msg', None)
        error_field = ret.get('Error_Field', None)
        sej_order.error_type = int(error_type)
        raise SejError(
            message=error_message,
            order_no=sej_order.order_no,
            error_type=int(error_type),
            error_field=error_field
            )

    sej_order.mark_canceled(now)
    return sej_order

def request_update_order(request_or_registry, tenant, sej_order, update_reason, now=None):
    """
    注文情報更新 https://inticket.sej.co.jp/order/updateorder.do
    """
    if type(update_reason) is not SejOrderUpdateReason:
        raise ValueError('update_reason')

    if now is None:
        now = datetime.now()

    ticket_dict = dict(
        (ticket.ticket_idx, ticket)
        for ticket in sej_order.tickets
        )

    assert int(sej_order.payment_type) == int(SejPaymentType.PrepaymentOnly) or \
           (
                len(ticket_dict) == sej_order.total_ticket_count and
                sej_order.total_ticket_count <= 20
                ), \
           '%d == %d and %d < 20' % (len(ticket_dict), sej_order.total_ticket_count, sej_order.total_ticket_count)

    payment = create_communicator(request_or_registry, tenant, '/order/updateorder.do')
    params = create_sej_request_data(
        order_no=sej_order.order_no,
        total_price=sej_order.total_price,
        ticket_price=sej_order.ticket_price,
        commission_fee=sej_order.commission_fee,
        payment_type=sej_order.payment_type,
        ticketing_fee=sej_order.ticketing_fee,
        payment_due_at=sej_order.payment_due_at,
        ticketing_start_at=sej_order.ticketing_start_at,
        ticketing_due_at=sej_order.ticketing_due_at,
        regrant_number_due_at=sej_order.regrant_number_due_at,
        tickets=[
            dict(
                ticket_type=code_from_ticket_type[int(ticket.ticket_type)],
                event_name=ticket.event_name,
                performance_name=ticket.performance_name,
                performance_datetime=ticket.performance_datetime,
                ticket_template_id=ticket.ticket_template_id,
                xml=ticket.ticket_data_xml,
                product_item_id=ticket.product_item_id
                )
            for ticket in sorted(ticket_dict.values(), lambda a, b: cmp(a.ticket_idx, b.ticket_idx))
            ]
        )
    params['X_upd_riyu']        = '%02d' % update_reason.v
    if sej_order.billing_number is not None:
        params['X_haraikomi_no']    = sej_order.billing_number
    if sej_order.exchange_number is not None:
        params['X_hikikae_no']      = sej_order.exchange_number
    sej_order.total_ticket_count    = int(params.get('X_ticket_cnt', 0))
    sej_order.ticket_count          = int(params.get('X_ticket_hon_cnt', 0))
    ret = payment.request(params, 0)

    # example response
    # {
    #   'X_haraikomi_no': '2306667473026',
    #   'X_ticket_cnt': '03',
    #   'X_url_info': 'https://www.r1test.com/order/hi.do',
    #   'X_shop_order_id': 'orderid00001',
    #   'iraihyo_id_00': '3052030666747302c21b35696fdd51ca',
    #   'DATA': 'END',
    #   'X_ticket_hon_cnt': '01'
    # }

    error_type = ret.get('Error_Type', 0)
    if error_type:
        error_message = ret.get('Error_Msg', None)
        error_field = ret.get('Error_Field', None)
        sej_order.error_type = int(error_type)
        sej_order.order_at = None
        raise SejError(
            message=error_message,
            order_no=sej_order.order_no,
            error_type=int(error_type),
            error_field=error_field
            )

    assert (not sej_order.order_no) or sej_order.order_no == ret.get('X_shop_order_id')
    assert (not sej_order.billing_number) or sej_order.billing_number == ret.get('X_haraikomi_no')
    assert (not sej_order.exchange_number) or sej_order.exchange_number == ret.get('X_hikikae_no')
    if int(sej_order.payment_type) != int(SejPaymentType.PrepaymentOnly):
        assert (not sej_order.total_ticket_count) or sej_order.total_ticket_count == int(ret.get('X_ticket_cnt', 0))
        assert (not sej_order.ticket_count) or sej_order.ticket_count == int(ret.get('X_ticket_hon_cnt', 0))
    assert (not sej_order.exchange_sheet_url) or sej_order.exchange_sheet_url == ret.get('X_url_info')
    assert (not sej_order.exchange_sheet_number) or sej_order.exchange_sheet_number == ret.get('iraihyo_id_00')

    sej_order.updated_at = now

    for idx in range(1, 21):
        ticket = ticket_dict.get(idx)
        barcode_number = ret.get('X_barcode_no_%02d' % idx)
        if int(sej_order.payment_type) == int(SejPaymentType.PrepaymentOnly):
            assert not barcode_number, '%d: %r' % (idx, ret)
        else:
            assert (
                (not barcode_number and (
                    (not ticket) \
                    or int(ticket.ticket_type) in (SejTicketType.Ticket.v, SejTicketType.ExtraTicket.v))) \
                or (barcode_number and ticket)), \
                '%d: %r / %r' % (idx, ret, ticket_dict)
            if not ticket:
                continue
            ticket.barcode_number = barcode_number
    return sej_order

def request_fileget(request_or_registry, tenant, notification_type, date):
    """ファイル取得先 https://inticket.sej.co.jp/order/getfile.do"""
    params = JavaHashMap()

    params['X_data_type'] = "%02d" % notification_type
    params['X_date'] = build_sej_date(date)

    payment = create_communicator(request_or_registry, tenant, '/order/getfile.do')
    body = payment.request_file(params)

    return decompress(body)

def request_cancel_event(cancel_events):
    from .zip_file import EnhZipFile, ZipInfo

    # YYYYMMDD_TPBKOEN.dat
    # YYYYMMDD_TPBTICKET.dat
    # archive.txt

    tpboen_file_name = "%s_TPBKOEN.dat" % datetime.now().strftime('%Y%m%d')
    tpbticket_file_name = "%s_TPBTICKET.dat" % datetime.now().strftime('%Y%m%d')
    archive_txt_body = "%s\r\n%s\r\n" % (tpboen_file_name, tpbticket_file_name)

    zip_file_name = "/tmp/refund_file_%s.zip" % datetime.now().strftime('%Y%m%d%H%M')
    zf = EnhZipFile(zip_file_name, 'w')

    import zipfile
    import time
    import csv
    from utils import UnicodeWriter
    import StringIO

    zi = ZipInfo('archive.txt', time.localtime()[:6])
    zi.external_attr = 0666 << 16L
    w = zf.start_entry(zi)
    w.write(archive_txt_body)
    w.close()
    zf.finish_entry()

    output = StringIO.StringIO()
    event_tsv = UnicodeWriter(output, delimiter='\t', lineterminator=u'\r\n')

    for cancel_event in cancel_events:
        event_tsv.writerow([
            unicode(cancel_event.available),# 有効フラグ ○
            cancel_event.shop_id,#ショップID ○
            cancel_event.event_code_01,#公演決定キー1 ○
            cancel_event.event_code_02,#公演決定キー2 16以下 半角[0-9]
            cancel_event.title,#メインタイトル ○
            cancel_event.sub_title,#サブタイトル 600以下 漢字(SJIS)
            cancel_event.event_at.strftime('%Y%m%d'),#公演日 ○
            cancel_event.start_at.strftime('%Y%m%d'),#レジ払戻受付開始日 ○
            cancel_event.end_at.strftime('%Y%m%d'),#レジ払戻受付終了日 ○
            cancel_event.ticket_expire_at.strftime('%Y%m%d'),#チケット持ち込み期限 ○
            cancel_event.event_expire_at.strftime('%Y%m%d'),#公演レコード有効期限 ○
            u"%d" % cancel_event.refund_enabled, #レジ払戻可能フラグ ○
            u"%02d" % cancel_event.disapproval_reason if cancel_event.disapproval_reason else '',#払戻不可理由 2固定 半角[0-9]
            u"%d" % cancel_event.need_stub,#半券要否区分 ○
            cancel_event.remarks,#備考 256以下
            cancel_event.un_use_01 if cancel_event.un_use_01 else u'',
            cancel_event.un_use_02 if cancel_event.un_use_02 else u'',
            cancel_event.un_use_03 if cancel_event.un_use_03 else u'',
            cancel_event.un_use_04 if cancel_event.un_use_04 else u'',
            cancel_event.un_use_05 if cancel_event.un_use_05 else u'',
        ])


    zi = ZipInfo(tpboen_file_name, time.localtime()[:6])
    zi.external_attr = 0666 << 16L
    w = zf.start_entry(zi)
    w.write(unicode(output.getvalue(),'utf8').encode('CP932'))
    w.close()
    output.close()

    zf.finish_entry()

    output = StringIO.StringIO()
    ticket_tsv = UnicodeWriter(output, delimiter='\t', lineterminator=u'\r\n')
    for cancel_event in cancel_events:
        for ticket in cancel_event.tickets:
            ticket_tsv.writerow([
                unicode(ticket.available),
                cancel_event.shop_id,
                ticket.event_code_01,
                ticket.event_code_02,
                ticket.order_no,
                unicode(ticket.ticket_barcode_number),
                unicode(ticket.refund_ticket_amount),
                unicode(ticket.refund_other_amount),
            ])

    zi = ZipInfo(tpbticket_file_name, time.localtime()[:6])
    zi.external_attr = 0666 << 16L
    w = zf.start_entry(zi)
    w.write(unicode(output.getvalue(),'utf8').encode('CP932'))
    w.close()

    zf.close()

    return
