# -*- coding:utf-8 -*-

import hashlib, time, re, urllib2
import logging

import tempfile
from zlib import decompress, compress
from datetime import datetime
from dateutil.parser import parse

from .utils import JavaHashMap
from .models import SejOrder, SejTicket, SejNotification, SejCancelEvent, SejCancelTicket

from .resources import make_sej_response, is_ticket, need_ticketing
from .resources import SejNotificationType, SejOrderUpdateReason, SejPaymentType, SejTicketType
from .resources import SejResponseError, SejServerError, SejError

import sqlahelper

from lxml import etree
import re

DBSession = sqlahelper.get_session()

class SejTicketDataXml():

    xml = ''

    def __init__(self, xml):
        self.xml = xml

    def __unicode__(self):
        from cStringIO import StringIO
        s = StringIO(self.xml)
        x = etree.parse(s)
        xml =  re.sub(
            r'''(<\?xml[^>]*)encoding=(?:'[^']*'|"[^"]"|[^> ?]*)\?>''',
            r"\1encoding='Shift_JIS' ?>", etree.tostring(x, encoding='UTF-8', xml_declaration=True))
        return xml.decode("utf-8")

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
        request_params = self.create_request_params(params)
        req = urllib2.Request(self.url)
        buffer = ["%s=%s" % (name, urllib2.quote(unicode(param).encode('shift_jis', 'xmlcharrefreplace'))) for name, param in request_params.iteritems()]
        data = "&".join(buffer)

        req.add_data(data)
        req.add_header('User-Agent', 'SejPaymentForJava/2.00')
        req.add_header('Connection', 'close')


        try:
            res = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            res = e
        except urllib2.URLError, e:
            print e.args
            return

        status = res.code
        reason = res.msg
        body = res.read()


        if status != 800:
            raise SejServerError(status_code=status, reason=reason, body=body)

        return body



    def request(self, params, retry_mode):
        request_params = self.create_request_params(params)
        ret = self.send_request(request_params, 0, retry_mode)
        return ret

    def create_request_params(self, params):
        xcode = self.create_hash_from_x_start_params(params)
        params['xcode'] = xcode
        return params

    def create_md5hash_from_dict(self, kv):
        tmp_keys = JavaHashMap()
        key_array = list(kv.iterkeys())
        for key, value in kv.iteritems():
            tmp_keys[key.lower()] = value
        key_array.sort()
        buffer = [tmp_keys[key.lower()] for key in key_array]
        buffer.append(self.secret_key)
        buffer = u','.join(buffer)
        logging.debug('hash:' + buffer)
        return hashlib.md5(buffer.encode(encoding="UTF-8")).hexdigest()

    def create_hash_from_x_start_params(self, params):

        falsify_props = dict()
        for name,param in params.iteritems():
            if name.startswith('X_'):
                falsify_props[name] = param

        hash = self.create_md5hash_from_dict(falsify_props)

        return hash

    def send_request(self, request_params, mode, retry_flg):
        for count in range(self.retry_count):
            if count > 0:
                time.sleep(self.retry_interval)
            ret_val = self._send_request(request_params, mode, retry_flg)
            if ret_val != 120 and ret_val != 5:
                return ret_val

        return 0

    def _send_request(self, request_params, mode, retry_flg):
        if retry_flg:
            request_params['retry_cnt'] = '1'

        req = urllib2.Request(self.url)
        buffer = ["%s=%s" % (name, urllib2.quote(unicode(param).encode('shift_jis', 'xmlcharrefreplace'))) for name, param in request_params.iteritems()]
        data = "&".join(buffer)
        print data

        self.log.info("[request]%s" % data)

        req.add_data(data)
        req.add_header('User-Agent', 'SejPaymentForJava/2.00')
        req.add_header('Connection', 'close')

        try:
            res = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            res = e
        except urllib2.URLError, e:
            print e.args
            return

        status = res.code
        reason = res.msg
        body = res.read()
        print body

        self.log.info("[response]%s" % body)

        if status == 200:
            raise SejServerError(status_code=200, reason="Script syntax error", body=body)

        # ステータス800，902，910以外の場合は終了　戻り値：0
        if status != 800 and status != 902 and status != 910:
            raise SejServerError(status_code=status, reason=reason, body=body)
        # キャンセルかつステータス800の場合は終了　戻り値：0
        if status == 800 and mode == 1:
            raise SejServerError(status_code=status, reason=reason, body=body)

        self.response = self.parse(body, "SENBDATA")

        if status >= 900:
            raise SejServerError(status_code=status, reason=reason, body=body)
        if status != 800:
            raise SejServerError(status_code=status, reason=reason, body=body)

        return True

    def parse(self, body, tag_name):
        regex_tags = re.compile(r"<" + tag_name + ">([^<>]+)</"+tag_name+">")
        regex_params = re.compile(r"([^&=]+)=([^&=]+)")
        matches = regex_tags.findall(body)
        key_value = {}
        for match in matches:
            for key,val in regex_params.findall(match):
                key_value[key] = val
        return key_value


def _create_sej_request(
        order_id,
        total,
        ticket_total,
        commission_fee,
        payment_type,
        ticketing_fee,
        payment_due_datetime,
        ticketing_start_datetime,
        ticketing_due_datetime,
        regrant_number_datetime,
        tickets,
        shop_id):

    params = JavaHashMap()
    # ショップID Sejから割り当てられるshop_id

    params['X_shop_id']         = shop_id
    # ショップ名称
    # 注文ID
    params['X_shop_order_id']   = order_id

    if payment_type != SejPaymentType.Paid and payment_due_datetime:
        # コンビニでの決済を行う場合の支払い期限の設定
        params['X_pay_lmt']         = payment_due_datetime.strftime('%Y%m%d%H%M')

    # チケット代金
    x_ticket_daikin = ticket_total if payment_type != SejPaymentType.Paid else 0
    params['X_ticket_daikin']   = u'%06d' % x_ticket_daikin
    # チケット購入代金
    x_ticket_kounyu_daikin = commission_fee if payment_type != SejPaymentType.Paid else 0
    params['X_ticket_kounyu_daikin'] = u'%06d' % x_ticket_kounyu_daikin
    # 発券代金
    x_hakken_daikin = ticketing_fee if payment_type != SejPaymentType.PrepaymentOnly else 0
    params['X_hakken_daikin']       = u'%06d' % x_hakken_daikin

    # 合計金額 = チケット代金 + チケット購入代金+発券代金の場合
    x_goukei_kingaku = x_ticket_daikin + x_ticket_kounyu_daikin + x_hakken_daikin
    params['X_goukei_kingaku']  = u'%06d' % x_goukei_kingaku

    assert x_goukei_kingaku == x_ticket_daikin + x_ticket_kounyu_daikin + x_hakken_daikin
    if payment_type == SejPaymentType.Paid:
        assert x_ticket_daikin + x_ticket_kounyu_daikin == 0

    # 前払い
    if payment_type == SejPaymentType.Prepayment or payment_type == SejPaymentType.Paid:
        # 支払いと発券が異なる場合、発券開始日時と発券期限を指定できる。
        if ticketing_start_datetime is not None:
            params['X_hakken_mise_date'] = ticketing_start_datetime.strftime('%Y%m%d%H%M')
            # 発券開始日時状態フラグ
        else:
            params['X_hakken_mise_date_sts'] = u'1'
        if ticketing_due_datetime is not None:
            # 発券開始日時状態フラグ
            params['X_hakken_lmt']      = ticketing_due_datetime.strftime('%Y%m%d%H%M')
            # 発券期限日時状態フラグ
        else:
            params['X_hakken_lmt_sts'] = u'1'

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
        params['X_saifuban_hakken_lmt'] = regrant_number_datetime.strftime('%Y%m%d%H%M')
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
        payment_due_datetime = None,
        ticketing_start_datetime = None,
        ticketing_due_datetime = None,
        regrant_number_datetime = None,
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
    params = _create_sej_request(
        order_id=order_id,
        total=total,
        ticket_total=ticket_total,
        commission_fee=commission_fee,
        payment_type=payment_type,
        ticketing_fee=ticketing_fee,
        payment_due_datetime=payment_due_datetime,
        ticketing_start_datetime=ticketing_start_datetime,
        ticketing_due_datetime=ticketing_due_datetime,
        regrant_number_datetime=regrant_number_datetime,
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
            error_field=ret.get('Error_Field', None))

    sej_order = SejOrder()

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

def request_sej_exchange_sheet(sej_order_id, shop_id = u'30520', secret_key = u'E6PuZ7Vhe7nWraFW'):
    sej_order = SejOrder.query.filter_by(id = sej_order_id).one()

    params = JavaHashMap()
    params['iraihyo_id_00'] = sej_order.exchange_sheet_number
    url = sej_order.exchange_sheet_url

    req = urllib2.Request(url)
    buffer = ["%s=%s" % (name, urllib2.quote(param.encode('shift_jis'))) for name, param in params.iteritems()]
    data = "&".join(buffer)

    req.add_data(data)
    req.add_header('User-Agent', 'SejPaymentForJava/2.00')
    req.add_header('Connection', 'close')

    try:
        res = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        res = e
    except urllib2.URLError, e:
        print e.args
        return

    status = res.code
    reason = res.msg
    print res.read()

    if status == 200:
        body = res.read()
        return body

    raise Exception('not found')

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
            error_field=ret.get('Error_Field', None))

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
        payment_due_datetime = None,
        ticketing_start_datetime = None,
        ticketing_due_datetime = None,
        regrant_number_datetime = None,
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
    params = _create_sej_request(
        order_id=condition.get('order_id'),
        total=total,
        ticket_total=ticket_total,
        commission_fee=commission_fee,
        payment_type=payment_type,
        ticketing_fee=ticketing_fee,
        payment_due_datetime=payment_due_datetime,
        ticketing_start_datetime=ticketing_start_datetime,
        ticketing_due_datetime=ticketing_due_datetime,
        regrant_number_datetime=regrant_number_datetime,
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

    sej_order.payment_type              = payment_type.v
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

    order_buffer = {}
    for ticket in sej_order.tickets:
        order_buffer[ticket.ticket_idx] = ticket

    idx = 1
    for ticket in tickets:
        sej_ticket = order_buffer.get(idx)
        if not sej_ticket:
            break
        sej_ticket.ticket_idx           = idx
        sej_ticket.ticket_type          = ticket.get('ticket_type').v
        sej_ticket.event_name           = ticket.get('event_name')
        sej_ticket.performance_name     = ticket.get('performance_name')
        sej_ticket.performance_datetime = ticket.get('performance_datetime')
        sej_ticket.ticket_template_id   = ticket.get('ticket_template_id')
        sej_ticket.ticket_data_xml      = ticket.get('xml').xml
        code = ret.get('X_barcode_no_%02d' % idx)
        if code:
            ticket.barcode_number = code

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
    #params['X_tuchi_kbn'] = "%02d" % notification_type.v
    params['X_data_type'] = "%02d" % notification_type.v
    params['X_date'] = date.strftime('%Y%m%d')

    payment = SejPayment(url = hostname + u'/order/getfile.do', secret_key = secret_key)
    body = payment.request_file(params, True)

    return decompress(body)

def callback_notification(params,
                          secret_key = u'E6PuZ7Vhe7nWraFW'):


    hash_map = JavaHashMap()
    for k,v in params.items():
        hash_map[k] = v

    payment = SejPayment(url = '', secret_key = secret_key)
    hash = payment.create_hash_from_x_start_params(hash_map)
    '''
    if hash != params.get('xcode'):
        raise SejResponseError(
            400, 'Bad Request',dict(status='400', Error_Type='00', Error_Msg='Bad Value', Error_Field='xcode'))

    '''

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

    def process_payment_complete(notification_type):
        '''3-1.入金発券完了通知'''
        n.notification_type     = notification_type
        n.process_number        = hash_map['X_shori_id']
        n.shop_id               = hash_map['X_shop_id']
        n.payment_type          = int(hash_map['X_shori_kbn'])
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
        n.signature                     = hash_map['xcode']

        return make_sej_response(dict(status='800' if not retry_data else '810'))

    def process_re_grant(notification_type):
        '''3-2.SVC強制取消通知'''
        n.notification_type             = notification_type
        n.process_number                = hash_map['X_shori_id']
        n.shop_id                       = hash_map['X_shop_id']
        n.payment_type                  = int(hash_map['X_shori_kbn'])
        n.order_id                      = hash_map['X_shop_order_id']
        n.billing_number                = hash_map['X_haraikomi_no']
        n.exchange_number               = hash_map['X_hikikae_no']
        n.payment_type_new              = hash_map['X_shori_kbn_new']
        n.billing_number_new            = hash_map['X_haraikomi_no_new']
        n.exchange_number_new           = hash_map['X_hikikae_no_new']
        n.ticketing_due_datetime_new    = parse(hash_map['X_lmt_time_new'])
        n.barcode_numbers = dict()
        n.barcode_numbers['barcodes'] = list()
        for idx in range(1,20):
            n.barcode_numbers['barcodes'].append(hash_map['X_barcode_no_new_%02d' % idx])
        n.processed_at          = parse(hash_map['X_shori_time'])
        n.signature                     = hash_map['xcode']

        return make_sej_response(dict(status='800' if not retry_data else '810'))

    def process_expire(notification_type):

        n.process_number                = hash_map['X_shori_id']
        n.notification_type             = notification_type
        n.shop_id                       = hash_map['X_shop_id']
        n.order_id                      = hash_map['X_shop_order_id']
        n.ticketing_due_datetime_new    = parse(hash_map['X_lmt_time'])
        n.billing_number                = hash_map['X_haraikomi_no']
        n.exchange_number               = hash_map['X_hikikae_no']
        n.processed_at                  = parse(hash_map['X_shori_time'])
        n.signature                     = hash_map['xcode']

        n.barcode_numbers               = dict()
        n.barcode_numbers['barcodes']   = list()

        for idx in range(1,20):
            n.barcode_numbers['barcodes'].append(hash_map['X_barcode_no_new_%02d' % idx])

        return make_sej_response(dict(status='800' if not retry_data else '810'))

    def dummy(notification_type):
        raise SejResponseError(
             422, 'Bad Request',dict(status='422', Error_Type='01', Error_Msg='Bad Value', Error_Field='X_tuchi_type'))

    ret = {
        SejNotificationType.PaymentComplete.v   : process_payment_complete,
        SejNotificationType.CancelFromSVC.v     : process_payment_complete,
        SejNotificationType.ReGrant.v           : process_re_grant,
        SejNotificationType.TicketingExpire.v   : process_expire,
    }.get(int(params['X_tuchi_type']), dummy)(int(params['X_tuchi_type']))

    DBSession.flush()

    return ret


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
            cancel_event.un_use_01,
            cancel_event.un_use_02,
            cancel_event.un_use_03,
            cancel_event.un_use_04,
            cancel_event.un_use_05,
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
                ticket.shop_id,
                ticket.event_code_01,
                ticket.event_code_02,
                ticket.order_id,
                unicode(ticket.ticket_barcode_number),
                unicode(ticket.refund_ticket_amount),
                unicode(ticket.refund_amount),
            ])

    zi = ZipInfo(tpbticket_file_name, time.localtime()[:6])
    zi.external_attr = 0666 << 16L
    w = zf.start_entry(zi)
    w.write(unicode(output.getvalue(),'utf8').encode('CP932'))
    w.close()


    zf.close()
    return
