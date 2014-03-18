# -*- coding:utf-8 -*-

import hashlib, time, re, urllib2
import logging

import tempfile
from zlib import decompress
from datetime import datetime
from dateutil.parser import parse

from .utils import JavaHashMap
from .models import (
    is_ticket,
    need_ticketing,
    SejOrder,
    SejTicket,
    SejNotification,
    SejNotificationType,
    SejOrderUpdateReason,
    SejPaymentType,
    SejTicketType,
    code_from_payment_type,
    code_from_ticket_type
    )
from .helpers import (
    parse_sej_response,
    create_sej_request,
    create_request_params,
    create_hash_from_x_start_params
    )
from .exceptions import SejServerError, SejError

import sqlahelper

DBSession = sqlahelper.get_session()

sej_hostname = u'https://pay.r1test.com/'
logger = logging.getLogger(__name__)


class SejPayment(object):

    url = ''
    secret_key = ''

    time_out = 120
    retry_count = 3
    retry_interval = 5

    response = {}


    def __init__(self, secret_key, url, time_out = 120, retry_count = 3, retry_interval = 5):
        self.secret_key = secret_key
        self.url = url
        self.time_out = time_out
        self.retry_count = retry_count
        self.retry_interval = retry_interval

    def request_file(self, params, retry_mode):
        request_params = create_request_params(params, self.secret_key)
        req = create_sej_request(self.url, request_params)
        try:
            res = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            res = e
        except urllib2.URLError, e:
            raise

        status = res.code
        reason = res.msg
        body = res.read()

        if status != 800:
            raise SejServerError(status_code=status, reason=reason, body=body)

        return body

    def request(self, params, retry_mode):
        request_params = create_request_params(params, self.secret_key)
        self.send_request(request_params, 0, retry_mode)

    def send_request(self, request_params, mode, retry_flg):
        for count in range(self.retry_count):
            if count > 0:
                time.sleep(self.retry_interval)
            if self._send_request(request_params, mode, retry_flg):
                return
            else:
                retry_flg=1

        reason = 'Sej Server connection error'
        logger.error(reason)
        raise SejServerError(status_code=None, reason=reason, body=None)

    def _send_request(self, request_params, mode, retry_flg):
        if retry_flg:
            request_params['retry_cnt'] = '1'
        req = create_sej_request(self.url, request_params)

        try:
            res = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            res = e
        except urllib2.URLError, e:
            logger.error(e)
            return

        status = res.code
        reason = res.msg
        body = res.read()

        logger.info("[response]\n%s" % body)

        if status == 200:
            # status == 200 はSyntaxErrorなんだって！
            raise SejServerError(status_code=200, reason="Script syntax error", body=body)

        if (status == 800 and mode != 1) or status == 902 or status == 910:
            self.response = parse_sej_response(body, "SENBDATA")
        else:
            raise SejServerError(status_code=status, reason=reason, body=body)

        return True

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
        shop_id):

    params = JavaHashMap()
    # ショップID Sejから割り当てられるshop_id

    params['X_shop_id']         = shop_id
    # ショップ名称
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
        x_pay_lmt = payment_due_at and payment_due_at.strftime('%Y%m%d%H%M')
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
            params['X_hakken_mise_date'] = ticketing_start_at.strftime('%Y%m%d%H%M')
            # 発券開始日時状態フラグ
        else:
            params['X_hakken_mise_date_sts'] = u'1'

        if ticketing_due_at is not None:
            # 発券期限日時状態フラグ
            params['X_hakken_lmt']      = ticketing_due_at.strftime('%Y%m%d%H%M')
        else:
            # 発券期限日時
            params['X_hakken_lmt_sts'] = u'1'
    #else:
    #    if ticketing_start_at is not None:
    #        params['X_hakken_mise_date'] = ticketing_start_at.strftime('%Y%m%d%H%M')
    #    if ticketing_due_at is not None:
    #        # 発券開始日時状態フラグ
    #        params['X_hakken_lmt']      = ticketing_due_at.strftime('%Y%m%d%H%M')

    ticket_num = 0
    e_ticket_num = 0

    for ticket in tickets:
        if type(ticket['ticket_type']) is not SejTicketType:
            raise ValueError('ticket_type : %s' % ticket['ticket_type'])
        if type(ticket['performance_datetime']) is not datetime:
            raise ValueError('performance_datetime : %s' % ticket['performance_datetime'])
        if is_ticket(ticket['ticket_type']):
            ticket_num+=1
        else:
            e_ticket_num+=1

    if need_ticketing(payment_type):
        params['X_saifuban_hakken_lmt'] = regrant_number_due_at.strftime('%Y%m%d%H%M')
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
            params['X_kouen_date_%02d' % idx]       = ticket['performance_datetime'].strftime('%Y%m%d%H%M')
            params['X_ticket_template_%02d' % idx]  = ticket['ticket_template_id']
            params['ticket_text_%02d' % idx]        = ticket['xml']
            idx+=1

    return params

def build_sej_tickets_from_dicts(sej_order, tickets, barcode_number_getter):
    return [
        SejTicket(
            order                = sej_order,
            order_no             = sej_order.order_no,
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

def request_order(
        shop_name,
        contact_01,
        contact_02,
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
        payment_due_at = None,
        ticketing_start_at = None,
        ticketing_due_at = None,
        regrant_number_due_at = None,
        tickets = [],
        shop_id = u'30520',
        secret_key = u'E6PuZ7Vhe7nWraFW',
        hostname = sej_hostname
        ):
    """済要求 https://inticket.sej.co.jp/order/order.do"""

    if type(payment_type) is not SejPaymentType:
        raise ValueError('payment_type')

    if int(payment_type) == int(SejPaymentType.Paid):
        payment_due_at = None

    payment = SejPayment(url = hostname + '/order/order.do', secret_key = secret_key)
    params = create_sej_request_data(
        order_no=order_no,
        total_price=total_price,
        ticket_price=ticket_price,
        commission_fee=commission_fee,
        payment_type=payment_type,
        ticketing_fee=ticketing_fee,
        payment_due_at=payment_due_at,
        ticketing_start_at=ticketing_start_at,
        ticketing_due_at=ticketing_due_at,
        regrant_number_due_at=regrant_number_due_at,
        tickets=tickets,
        shop_id=shop_id,
    )

    params['shop_namek']        = shop_name
    # 連絡先1

    params['X_renraku_saki']    = contact_01
    # 連絡先2
    params['renraku_saki']      = contact_02
    # お客様氏名
    params['user_namek']        = user_name
    # お客様氏名カナ
    params['user_name_kana']    = user_name_kana
    # お客様電話番号
    params['X_user_tel_no']     = tel
    #　お客様郵便番号
    params['X_user_post']       = zip_code
    # お客様メールアドレス
    params['X_user_email']      = email
    # 処理区分
    params['X_shori_kbn']       = u'%02d' % payment_type.v

    payment.request(params, 0)
    ret = payment.response
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
        raise SejError(
            message=ret.get('Error_Msg', None),
            order_no=order_no,
            error_code=int(error_type),
            error_field=ret.get('Error_Field', None)
            )

    sej_order = SejOrder(
        shop_id                   = shop_id,
        shop_name                 = shop_name,
        contact_01                = contact_01,
        contact_02                = contact_02,
        user_name                 = user_name,
        user_name_kana            = user_name_kana,
        tel                       = tel,
        zip_code                  = zip_code,
        email                     = email,
        payment_type              = payment_type.v,
        billing_number            = ret.get('X_haraikomi_no'),
        total_ticket_count        = int(ret.get('X_ticket_cnt', 0)),
        ticket_count              = int(ret.get('X_ticket_hon_cnt', 0)),
        exchange_sheet_url        = ret.get('X_url_info'),
        order_no                  = ret.get('X_shop_order_id'),
        exchange_sheet_number     = ret.get('iraihyo_id_00'),
        exchange_number           = ret.get('X_hikikae_no'),
        order_at                  = datetime.now(),
        total_price               = int(params.get('X_goukei_kingaku',0)),
        ticket_price              = int(params.get('X_ticket_daikin',0)),
        commission_fee            = int(params.get('X_ticket_kounyu_daikin',0)),
        ticketing_fee             = int(params.get('X_hakken_daikin',0)),
        payment_due_at            = payment_due_at,
        ticketing_start_at        = ticketing_start_at,
        ticketing_due_at          = ticketing_due_at,
        regrant_number_due_at     = regrant_number_due_at
        )
    sej_tickets = build_sej_tickets_from_dicts(
        sej_order,
        tickets,
        lambda idx: ret.get('X_barcode_no_%02d' % idx) or None
        )
    for sej_ticket in sej_tickets:
        DBSession.add(sej_ticket)

    DBSession.add(sej_order)
    DBSession.flush()

    return sej_order

def request_cancel_order(
        order_no,
        billing_number,
        exchange_number,
        shop_id = u'30520',
        secret_key = u'E6PuZ7Vhe7nWraFW',
        hostname = sej_hostname,
        now=None
    ):
    '''
    注文キャンセル https://inticket.sej.co.jp/order/cancelorder.do
    '''
    payment = SejPayment(url = hostname + u'/order/cancelorder.do', secret_key = secret_key)
    params = JavaHashMap()
    params['X_shop_id']         = shop_id
    params['X_shop_order_id']   = order_no
    if billing_number:
        params['X_haraikomi_no']    = billing_number
    if exchange_number:
        params['X_hikikae_no']      = exchange_number

    payment.request(params, 0)
    ret = payment.response

    error_type = ret.get('Error_Type', 0)
    if error_type:
        raise SejError(
            message=ret.get('Error_Msg', None),
            order_no=order_no,
            error_code=int(error_type),
            error_field=ret.get('Error_Field', None)
            )

    from .api import get_sej_order
    sej_order = get_sej_order(order_no)
    if sej_order.billing_number != billing_number or \
       sej_order.exchange_number != exchange_number:
        raise ValueError('validation error: billing_number or exchange_number is different from SejOrder(order_no=%s): billing_number=%s (expected %s), exchange_number=%s (expected %s)' % (
            order_no,
            exchange_number, sej_order.exchange_number,
            billing_number, sej_order.billing_number,
            ))
    sej_order.mark_canceled(now)
    DBSession.merge(sej_order)
    DBSession.flush()

    return sej_order

def request_update_order(
        new_order,
        update_reason,
        shop_id = u'30520',
        secret_key = u'E6PuZ7Vhe7nWraFW',
        hostname = sej_hostname
):
    """
    注文情報更新 https://inticket.sej.co.jp/order/updateorder.do
    """
    if type(update_reason) is not SejOrderUpdateReason:
        raise ValueError('update_reason')

    ticket_dict = dict(
        (ticket.ticket_idx, ticket)
        for ticket in new_order.tickets
        )

    assert int(new_order.payment_type) == int(SejPaymentType.PrepaymentOnly) or \
           (
                len(ticket_dict) == new_order.total_ticket_count and
                new_order.total_ticket_count <= 20
                ), \
           '%d == %d and %d < 20' % (len(ticket_dict), new_order.total_ticket_count, new_order.total_ticket_count)

    payment = SejPayment(url = hostname + u'/order/updateorder.do', secret_key = secret_key)
    params = create_sej_request_data(
        order_no=new_order.order_no,
        total_price=new_order.total_price,
        ticket_price=new_order.ticket_price,
        commission_fee=new_order.commission_fee,
        payment_type = code_from_payment_type[int(new_order.payment_type)],
        ticketing_fee=new_order.ticketing_fee,
        payment_due_at=new_order.payment_due_at,
        ticketing_start_at=new_order.ticketing_start_at,
        ticketing_due_at=new_order.ticketing_due_at,
        regrant_number_due_at=new_order.regrant_number_due_at,
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
            ],
        shop_id=new_order.shop_id
        )
    params['X_upd_riyu']        = '%02d' % update_reason.v
    if new_order.billing_number is not None:
        params['X_haraikomi_no']    = new_order.billing_number
    if new_order.exchange_number is not None:
        params['X_hikikae_no']      = new_order.exchange_number
    payment.request(params, 0)
    ret = payment.response

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
        raise SejError(
            message=ret.get('Error_Msg', None),
            order_no=new_order.order_no,
            error_code=int(error_type),
            error_field=ret.get('Error_Field', None)
            )

    assert (not new_order.order_no) or new_order.order_no == ret.get('X_shop_order_id')
    assert (not new_order.billing_number) or new_order.billing_number == ret.get('X_haraikomi_no')
    assert (not new_order.exchange_number) or new_order.exchange_number == ret.get('X_hikikae_no')
    if int(new_order.payment_type) != int(SejPaymentType.PrepaymentOnly):
        assert (not new_order.total_ticket_count) or new_order.total_ticket_count == int(ret.get('X_ticket_cnt', 0))
        assert (not new_order.ticket_count) or new_order.ticket_count == int(ret.get('X_ticket_hon_cnt', 0))
    assert (not new_order.exchange_sheet_url) or new_order.exchange_sheet_url == ret.get('X_url_info')
    assert (not new_order.exchange_sheet_number) or new_order.exchange_sheet_number == ret.get('iraihyo_id_00')

    new_order.updated_at                = datetime.now()

    for idx in range(1, 21):
        ticket = ticket_dict.get(idx)
        barcode_number = ret.get('X_barcode_no_%02d' % idx)
        if int(new_order.payment_type) == int(SejPaymentType.PrepaymentOnly):
            assert not barcode_number, '%d: %r' % (idx, ret)
        else:
            assert (not barcode_number and not ticket) or (barcode_number and ticket), '%d: %r / %r' % (idx, ret, ticket_dict)
            if not ticket:
                continue
            ticket.barcode_number = barcode_number

def request_fileget(
        notification_type,
        date,
        shop_id = u'30520',
        secret_key = u'E6PuZ7Vhe7nWraFW',
        hostname = sej_hostname):
    """ファイル取得先 https://inticket.sej.co.jp/order/getfile.do
    """

    params = JavaHashMap()

    params['X_shop_id'] = shop_id
    params['X_data_type'] = "%02d" % notification_type
    params['X_date'] = date.strftime('%Y%m%d')

    payment = SejPayment(url = hostname + u'/order/getfile.do', secret_key = secret_key)
    body = payment.request_file(params, True)

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
