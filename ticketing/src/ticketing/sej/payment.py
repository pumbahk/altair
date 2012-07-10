# -*- coding:utf-8 -*-

import hashlib, time, re, urllib2
import logging

import tempfile
from zlib import decompress
from datetime import datetime
from dateutil.parser import parse

from .utils import JavaHashMap
from .models import SejOrder, SejTicket, SejNotification

from .helpers import make_sej_response, parse_sej_response, create_sej_request, create_request_params, create_sej_request_data, create_hash_from_x_start_params
from .resources import SejNotificationType, SejOrderUpdateReason, SejPaymentType, SejTicketType
from .exceptions import SejResponseError, SejServerError, SejError

import sqlahelper

DBSession = sqlahelper.get_session()

sej_hostname = u'https://pay.r1test.com/'

class SejPayment(object):

    url = ''
    secret_key = ''

    time_out = 120
    retry_count = 3
    retry_interval = 5

    response = {}

    log = logging.getLogger('sej_payment')

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
            return

        status = res.code
        reason = res.msg
        body = res.read()

        if status != 800:
            raise SejServerError(status_code=status, reason=reason, body=body)

        return body

    def request(self, params, retry_mode):
        request_params = create_request_params(params, self.secret_key)
        ret = self.send_request(request_params, 0, retry_mode)
        return ret


    def send_request(self, request_params, mode, retry_flg):
        for count in range(self.retry_count):
            if count > 0:
                time.sleep(self.retry_interval)
            if self._send_request(request_params, mode, retry_flg):
                return True
            else:
                retry_flg=1
        return False

    def _send_request(self, request_params, mode, retry_flg):
        if retry_flg:
            request_params['retry_cnt'] = '1'
        print self.url
        req = create_sej_request(self.url, request_params)

        try:
            res = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            res = e
        except urllib2.URLError, e:
            #print e.args
            return

        status = res.code
        reason = res.msg
        body = res.read()

        self.log.info("[response]%s" % body)
        print ("[response]%s" % body)

        if status == 200:
            # status == 200 はSyntaxErrorなんだって！
            raise SejServerError(status_code=200, reason="Script syntax error", body=body)

        if (status == 800 and mode != 1) or status == 902 or status == 910:
            self.response = parse_sej_response(body, "SENBDATA")
        else:
            raise SejServerError(status_code=status, reason=reason, body=body)

        return True

def request_order(
        shop_name,
        contact_01,
        contact_02,
        order_id,
        username,
        username_kana,
        tel,
        zip,
        email,
        total,
        ticket_total,
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

    if tickets is list:
        raise ValueError('tickets')

    payment = SejPayment(url = hostname + '/order/order.do', secret_key = secret_key)
    params = create_sej_request_data(
        order_id=order_id,
        total=total,
        ticket_total=ticket_total,
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
    params['user_namek']        = username
    # お客様氏名カナ
    params['user_name_kana']    = username_kana
    # お客様電話番号
    params['X_user_tel_no']     = tel
    #　お客様郵便番号
    params['X_user_post']       = zip
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

    error_type = ret.get('Error_Type', None)
    if error_type:
        raise SejError(
            error_type=int(error_type),
            error_msg=ret.get('Error_Msg', None),
            error_field=ret.get('Error_Field', None),
        error_body='')

    sej_order = SejOrder()
    sej_order.shop_id                   = shop_id
    sej_order.shop_name                 = shop_name
    sej_order.contact_01                = contact_01
    sej_order.contact_02                = contact_02
    sej_order.user_name                 = username
    sej_order.user_name_kana            = username_kana
    sej_order.tel                       = tel
    sej_order.zip_code                  = zip
    sej_order.email                     = email

    sej_order.payment_type              = payment_type.v
    sej_order.billing_number            = ret.get('X_haraikomi_no')
    sej_order.total_ticket_count        = int(ret.get('X_ticket_cnt', 0))
    sej_order.ticket_count              = int(ret.get('X_ticket_hon_cnt', 0))
    sej_order.exchange_sheet_url        = ret.get('X_url_info')
    sej_order.order_id                  = ret.get('X_shop_order_id')
    sej_order.exchange_sheet_number     = ret.get('iraihyo_id_00')
    sej_order.exchange_number           = ret.get('X_hikikae_no')
    sej_order.order_at                  = datetime.now()
    sej_order.total_price               = int(params.get('X_goukei_kingaku',0))
    sej_order.ticket_price              = int(params.get('X_ticket_daikin',0))
    sej_order.commission_fee            = int(params.get('X_ticket_kounyu_daikin',0))
    sej_order.ticketing_fee             = int(params.get('X_hakken_daikin',0))

    sej_order.payment_due_at            = payment_due_at
    sej_order.ticketing_start_at        = ticketing_start_at
    sej_order.ticketing_due_at          = ticketing_due_at
    sej_order.regrant_number_due_at     = regrant_number_due_at

    sej_order.attributes = dict()
    idx = 1
    for ticket in tickets:
        sej_ticket = SejTicket()
        sej_ticket.ticket_idx           = idx
        sej_ticket.ticket_type          = ticket.get('ticket_type').v
        sej_ticket.event_name           = ticket.get('event_name')
        sej_ticket.performance_name     = ticket.get('performance_name')
        sej_ticket.performance_datetime = ticket.get('performance_datetime')
        sej_ticket.ticket_template_id   = ticket.get('ticket_template_id')
        sej_ticket.ticket_data_xml      = ticket.get('xml').xml
        code = ret.get('X_barcode_no_%02d' % idx)
        if code:
            sej_ticket.barcode_number = code

        sej_order.tickets.append(sej_ticket)

        idx+=1

    DBSession.add(sej_order)
    DBSession.flush()

    return sej_order

def request_cancel_order(
        order_id,
        billing_number,
        exchange_number,
        shop_id = u'30520',
        secret_key = u'E6PuZ7Vhe7nWraFW',
        hostname = sej_hostname
    ):
    '''
    注文キャンセル https://inticket.sej.co.jp/order/cancelorder.do
    '''
    payment = SejPayment(url = hostname + u'/order/cancelorder.do', secret_key = secret_key)
    params = JavaHashMap()
    params['X_shop_id']         = shop_id
    params['X_shop_order_id']   = order_id
    if billing_number:
        params['X_haraikomi_no']    = billing_number
    if exchange_number:
        params['X_hikikae_no']      = exchange_number

    payment.request(params, 0)
    ret = payment.response

    error_type = ret.get('Error_Type', None)
    if error_type:
        raise SejError(
            error_type=int(error_type),
            error_msg=ret.get('Error_Msg', None),
            error_field=ret.get('Error_Field', None),
            error_body=u''
        )

    sej_order = SejOrder.query.filter_by(order_id = order_id, billing_number = billing_number, exchange_number=exchange_number).one()
    sej_order.cancel_at = datetime.now()
    DBSession.merge(sej_order)
    DBSession.flush()

    return sej_order

def request_update_order(
        update_reason,
        total,
        ticket_total,
        commission_fee,
        ticketing_fee,
        payment_type,
        payment_due_at = None,
        ticketing_start_at = None,
        ticketing_due_at = None,
        regrant_number_due_at = None,
        tickets = list(),
        condition = dict(),
        shop_id = u'30520',
        secret_key = u'E6PuZ7Vhe7nWraFW',
        hostname = sej_hostname
):
    """
    注文情報更新 https://inticket.sej.co.jp/order/updateorder.do
    """
    if type(update_reason) is not SejOrderUpdateReason:
        raise ValueError('update_reason')

    if type(payment_type) is not SejPaymentType:
        raise ValueError('payment_type')

    if tickets is list:
        raise ValueError('tickets')

    sej_order = SejOrder.query.filter_by(
        order_id = condition.get('order_id'),
        billing_number = condition.get('billing_number'),
        exchange_number=condition.get('exchange_number')).one()

    if not sej_order:
        raise ValueError('order not found')

    payment = SejPayment(url = hostname + u'/order/updateorder.do', secret_key = secret_key)
    params = create_sej_request_data(
        order_id=condition.get('order_id'),
        total=total,
        ticket_total=ticket_total,
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
    params['X_upd_riyu']        = '%02d' % update_reason.v
    if condition.get('billing_number'):
        params['X_haraikomi_no']    = condition.get('billing_number')
    if condition.get('exchange_number'):
        params['X_hikikae_no']      = condition.get('exchange_number')
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

    error_type = ret.get('Error_Type', None)
    if error_type:
        raise SejError(
            error_type=int(error_type),
            error_msg=ret.get('Error_Msg', None),
            error_field=ret.get('Error_Field', None))

    sej_order.payment_type              = '%d' % payment_type.v
    sej_order.billing_number            = ret.get('X_haraikomi_no')
    sej_order.total_ticket_count        = int(ret.get('X_ticket_cnt', 0))
    sej_order.ticket_count              = int(ret.get('X_ticket_hon_cnt', 0))
    sej_order.exchange_sheet_url        = ret.get('X_url_info')
    sej_order.order_id                  = ret.get('X_shop_order_id')
    sej_order.exchange_sheet_number     = ret.get('iraihyo_id_00')
    sej_order.exchange_number           = ret.get('X_hikikae_no')
    sej_order.total_price               = int(params.get('X_goukei_kingaku',0))
    sej_order.ticket_price              = int(params.get('X_ticket_daikin',0))
    sej_order.commission_fee            = int(params.get('X_ticket_kounyu_daikin',0))
    sej_order.ticketing_fee             = int(params.get('X_hakken_daikin',0))
    sej_order.updated_at                = datetime.now()

    sej_order.payment_due_at            = payment_due_at
    sej_order.ticketing_start_at        = ticketing_start_at
    sej_order.ticketing_due_at          = ticketing_due_at
    sej_order.regrant_number_due_at     = regrant_number_due_at

    order_buffer = {}
    for ticket in sej_order.tickets:
        order_buffer[ticket.ticket_idx] = ticket

    idx = 1
    for ticket in tickets:
        sej_ticket = order_buffer.get(idx)
        if not sej_ticket:
            break
        sej_ticket.ticket_idx           = idx
        sej_ticket.ticket_type          = "%d" % ticket.get('ticket_type').v
        sej_ticket.event_name           = ticket.get('event_name')
        sej_ticket.performance_name     = ticket.get('performance_name')
        sej_ticket.performance_datetime = ticket.get('performance_datetime')
        sej_ticket.ticket_template_id   = ticket.get('ticket_template_id')
        sej_ticket.ticket_data_xml      = ticket.get('xml').xml
        code = ret.get('X_barcode_no_%02d' % idx)
        if code:
            sej_ticket.barcode_number = code

        idx += 1


    DBSession.merge(sej_order)
    DBSession.flush()

    return sej_order


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
    params['X_data_type'] = "%02d" % notification_type.v
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
                ticket.order_id,
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
