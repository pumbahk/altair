# -*- coding:utf-8 -*-

import hashlib, time, re, urllib2
import logging
from datetime import datetime
from ticketing.utils import JavaHashMap, StandardEnum

from models import SejTicket

import sqlahelper

DBSession = sqlahelper.get_session()

sej_hostname = u'https://pay.r1test.com/'

class SejError(Exception):

    error_type  = 0
    error_msg   = ''
    error_field = ''

    def __init__(self, error_type, error_msg, error_field):

        self.error_type = error_type
        self.error_field = error_field
        self.error_msg = error_msg

    def __str__(self):
        return "Error_Type=%d&Error_Msg=%s&Error_Field=%s" % (self.error_type, self.error_type, self.error_field)

class SejServerError(Exception):

    status_code  = 0
    reason      = ''

    def __init__(self, status_code, reason):

        self.status_code = status_code
        self.reason = reason

    def __str__(self):
        return "status_code=%d&reason=%s" % (self.status_code, self.reason)

class SejFileParser(object):

    class SejFileParserRow(object):
        cursor = 0
        #
        def __init__(self, row):
            self.row = row
        #
        def get_col(self, num):
            row = self.row[self.cursor:self.cursor+num]
            self.cursor = self.cursor + num
            return row

    rec_segment = ''
    shop_id     = ''
    filename    = ''
    date        = ''
    row_length      = 0

    def parse_header(self, data):
        row = SejFileParser.SejFileParserRow(data)
        self.rec_segment = row.get_col(1)
        if self.rec_segment != 'H':
            raise Exception("Invalid header type : %s" % self.rec_segment)
        self.shop_id     = row.get_col(5)
        self.filename    = row.get_col(30)
        self.date        = row.get_col(8)
        self.row_length  = int(row.get_col(4))

    def parse_row(self, row):
        raise Exception("stub: method not implements.")

    def parse(self, data):
        self.parse_header(data)
        total_length = len(data)

        if total_length % self.row_length == 0:
            raise Exception('Invalid row length  row:%d total:%d' % (self.row_length, total_length))

        values = []

        for start_at in range(start=self.row_length, step=self.row_length, stop=len(data)):
            row = data[start_at ,start_at + self.row_length]
            values.append(self.parse_row(row))

        return values

class SejInstantPaymentFileParser(SejFileParser):

    def parse_row(self, row):
        row = SejFileParser.SejFileParserRow(row)
        data = {
            'segment' : row.get_col(1),
            'shop_id' : row.get_col(5),
            'order_id' : row.get_col(12),
            'payment_type' : row.get_col(2),
            'bill_number' : row.get_col(2),
            'exchange_number' : row.get_col(13),
            'price' : row.get_col(13),
            'ticket_total_num' : row.get_col(6),
            'ticket_num' : row.get_col(2),
            'return_num' : row.get_col(2),
            'cancel_reason' : row.get_col(2),
            'process_date' : row.get_col(14),
            'checksum' : row.get_col(32)
        }
        return data

class SejExpiredFileParser(SejFileParser):

    def parse_row(self, row):
        row = SejFileParser.SejFileParserRow(row)
        data = {
            'segment' : row.get_col(1),
            'shop_id' : row.get_col(5),
            'order_id' : row.get_col(12),
            'expire_type' : row.get_col(2),
            'process_type' : row.get_col(2),
            'expired_at' : row.get_col(12),
            'bill_number' : row.get_col(13),
            'exchange_number' : row.get_col(13),
            'checksum' : row.get_col(32),
            'un_use' : row.get_col(8),
        }
        return data

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

    def request(self, params, retry_mode):
        request_params = self.create_request_params(params, self.secret_key)
        ret = self.send_request(request_params, 0, retry_mode)
        return ret


    def check_sign(self):
        pass

    def create_request_params(self, params, private_key):
        xcode = self.create_hash_from_x_start_params(params, private_key)
        params['xcode'] = xcode
        return params

    def create_md5hash_from_dict(self, kv, private_key):
        tmp_keys = JavaHashMap()
        key_array = list(kv.iterkeys())
        for key, value in kv.iteritems():
            tmp_keys[key.lower()] = value
        key_array.sort()
        buffer = [tmp_keys[key.lower()] for key in key_array]
        buffer.append(private_key)
        buffer = u','.join(buffer)
        logging.debug('hash:' + buffer)
        return hashlib.md5(buffer.encode(encoding="UTF-8")).hexdigest()

    def create_hash_from_x_start_params(self, params, salt_key):

        falsify_props = dict()
        for name,param in params.iteritems():
            if name.startswith('X_'):
                falsify_props[name] = param

        hash = self.create_md5hash_from_dict(falsify_props, salt_key)

        return hash

    def send_request(self, request_params, mode, retry_flg):
        for count in range(self.retry_count):
            if count > 0:
                time.sleep(self.retry_interval)
            ret_val = self._send_request(request_params, mode, retry_flg);
            if ret_val != 120 and ret_val != 5:
                return ret_val

        return 0

    def _send_request(self, request_params, mode, retry_flg):

        if retry_flg:
            request_params['retry_cnt'] = '1'

        req = urllib2.Request(self.url)
        buffer = ["%s=%s" % (name, urllib2.quote(param.encode('shift_jis'))) for name, param in request_params.iteritems()]
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
        logging.debug(body)

        if status == 200:
            raise SejServerError(status_code=200, reason="Script syntax error")

        # ステータス800，902，910以外の場合は終了　戻り値：0
        if status != 800 and status != 902 and status != 910:
            raise SejServerError(status_code=200, reason=reason)
        # キャンセルかつステータス800の場合は終了　戻り値：0
        if status == 800 and mode == 1:
            raise SejServerError(status_code=200, reason=reason)


        self.response = self.parse(body, "SENBDATA")

        if status >= 900:
            raise SejServerError(status_code=status, reason=reason)
        if status != 800:
            raise SejServerError(status_code=status, reason=reason)

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


class SejPaymentType(StandardEnum):
    # 01:代引き
    CashOnDelivery  = 1
    # 02:前払い(後日発券)
    Prepayment      = 2
    # 03:代済発券
    Paid            = 3
    # 04:前払いのみ
    PrepaymentOnly  = 4

def need_ticketing(type):
    if SejPaymentType.PrepaymentOnly == type :
        return False
    else:
        return True

class SejTicketType(StandardEnum):
    # 1:本券(チケットバーコード有り)
    Ticket                  = 1
    # 2:本券(チケットバーコード無し)
    TicketWithBarcode       = 2
    # 3:本券以外(チケットバーコード有り)
    ExtraTicket             = 3
    # 4:本券以外(チケットバーコード無し)
    ExtraTicketWithBarcode  = 4

def is_ticket(type):

    if type == SejTicketType.Ticket or \
       type == SejTicketType.TicketWithBarcode:
        return True
    else:
        return False

class SejOrderUpdateReason(StandardEnum):
    # 項目変更
    Change = 1
    # 公演中止
    Stop = 2

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
        ticketing_fee,
        payment_type,
        payment_due_datetime = None,
        ticketing_start_datetime = None,
        ticketing_due_datetime = None,
        ticketing_sub_due_datetime = None,
        tickets = [],
        shop_id = u'30520',
        secret_key = u'E6PuZ7Vhe7nWraFW',
        hostname = sej_hostname
        ):
    '''
        決済要求 https://inticket.sej.co.jp/order/order.do
    '''

    if type(payment_type) is not SejPaymentType:
        raise ValueError('payment_type')

    if tickets is list:
        raise ValueError('tickets')

    payment = SejPayment(url = hostname + '/order/order.do', secret_key = secret_key)
    params = JavaHashMap()
    # ショップID Sejから割り当てられるshop_id
    params['X_shop_id']         = shop_id
    # ショップ名称
    params['shop_namek']        = shop_name
    # 連絡先1
    params['X_renraku_saki']    = contact_01
    # 連絡先2
    params['renraku_saki']      = contact_02
    # 注文ID
    params['X_shop_order_id']   = order_id
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

    # 合計金額 = チケット代金 + チケット購入代金+発券代金の場合
    params['X_goukei_kingaku']  = u'%06d' % total

    if payment_type != SejPaymentType.Paid:
        # コンビニでの決済を行う場合の支払い期限の設定
        params['X_pay_lmt']         = payment_due_datetime.strftime('%Y%m%d%H%M')

    # チケット代金
    params['X_ticket_daikin']   = u'%06d' % ticket_total
    # チケット購入代金
    params['X_ticket_kounyu_daikin'] = u'%06d' % commission_fee

    if payment_type == SejPaymentType.Prepayment or payment_type == SejPaymentType.Paid:
        # 支払いと発券が異なる場合、発券開始日時と発券期限を指定できる。
        if ticketing_start_datetime is not None:
            params['X_hakken_mise_date'] = ticketing_start_datetime.strftime('%Y%m%d%H%M')
            # 発券開始日時状態フラグ
            params['X_hakken_mise_date_sts'] = u'01'
        if ticketing_due_datetime is not None:
            # 発券開始日時状態フラグ
            params['X_hakken_lmt']      = ticketing_due_datetime.strftime('%Y%m%d%H%M')
            # 発券期限日時状態フラグ
            params['X_hakken_lmt_sts']  = u'01'

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
        params['X_saifuban_hakken_lmt'] = ticketing_sub_due_datetime.strftime('%Y%m%d%H%M')

    params['X_hakken_daikin']       = u'%06d' % ticketing_fee
    params['X_ticket_cnt']          = u'%02d' % len(tickets)
    params['X_ticket_hon_cnt']      = u'%02d' % ticket_num

    idx = 1
    for ticket in tickets:
        if need_ticketing(payment_type):
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

    sejTicket = SejTicket()

    sejTicket.shori_kbn     = payment_type.v
    sejTicket.haraikomi_no  = ret.get('X_haraikomi_no')
    sejTicket.ticket_count  = int(ret.get('X_ticket_cnt', 0))
    sejTicket.ticket_hon_count  \
                            = int(ret.get('X_ticket_hon_cnt', 0))
    sejTicket.url_info      = ret.get('X_url_info')
    sejTicket.order_id      = ret.get('X_shop_order_id')
    sejTicket.iraihyo_id_00 = ret.get('iraihyo_id_00')
    sejTicket.order_at      = datetime.now()
    sejTicket.request_params = dict()
    for k, v in params.iteritems():
        sejTicket.request_params[k] = v
    for idx in range(1,sejTicket.ticket_count):
        code = ret.get('X_barcode_no_%02d' % idx)
        if code:
            sejTicket.attributes['X_barcode_no_%02d' % idx] = code

    DBSession.add(sejTicket)
    DBSession.flush()

    return sejTicket

def request_sej_exchange_sheet(order_id, shop_id = u'30520', secret_key = u'E6PuZ7Vhe7nWraFW'):
    sejTicket = SejTicket.query.filter_by(order_id = order_id).one()

    params = JavaHashMap()
    params['iraihyo_id_00'] = sejTicket.iraihyo_id_00

    req = urllib2.Request(u'order/hi.do')
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

    if status == 200:
        body = res.read()
        return body

    raise Exception('not found')

def request_cancel(
        order_id,
        haraikomi_no,
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
    params['X_haraikomi_no']    = haraikomi_no

    payment.request(params, 0)
    ret = payment.response

    error_type = ret.get('Error_Type', None)
    if error_type:
        raise SejError(
            error_type=int(error_type),
            error_msg=ret.get('Error_Msg', None),
            error_field=ret.get('Error_Field', None))

    sejTicket = SejTicket.query.filter_by(order_id = order_id, haraikomi_no = haraikomi_no).one()
    sejTicket.cancel_at = datetime.now()
    DBSession.merge(sejTicket)
    DBSession.flush()

    return sejTicket

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
        ticketing_sub_due_datetime = None,
        tickets = [],
        condition = {},
        shop_id = u'30520',
        secret_key = u'E6PuZ7Vhe7nWraFW',
):
    '''
    注文情報更新 https://inticket.sej.co.jp/order/updateorder.do
    '''
    if type(update_reason) is not SejOrderUpdateReason:
        raise ValueError('update_reason')

    if type(payment_type) is not SejPaymentType:
        raise ValueError('payment_type')

    if tickets is list:
        raise ValueError('tickets')

    # payment = SejPayment(url = u'https://pay.r1test.com/order/updateorder.do', secret_key = secret_key)
    payment = SejPayment(url = u'http://sv2.ticketstar.jp/test.php', secret_key = secret_key)
    params = JavaHashMap()
    params['X_upd_riyu']        = update_reason.v
    # ショップID Sejから割り当てられるshop_id
    params['X_shop_id']         = condition.get('shop_id')
    # 注文ID
    params['X_shop_order_id']   = condition.get('order_id')
    # 払込票番号
    params['X_haraikomi_no']    = condition.get('haraikomi_no')
    # 引換票番号
    params['X_hikikae_no']      = condition.get('hikikae_no')

    # 合計金額 = チケット代金 + チケット購入代金+発券代金の場合
    params['X_goukei_kingaku']  = u'%06d' % total

    if payment_type != SejPaymentType.Paid:
        # コンビニでの決済を行う場合の支払い期限の設定
        params['X_pay_lmt']         = payment_due_datetime.strftime('%Y%m%d%H%M')

    # チケット代金
    params['X_ticket_daikin']   = u'%06d' % ticket_total
    # チケット購入代金
    params['X_ticket_kounyu_daikin'] = u'%06d' % commission_fee

    if payment_type == SejPaymentType.Prepayment or payment_type == SejPaymentType.Paid:
        # 支払いと発券が異なる場合、発券開始日時と発券期限を指定できる。
        if ticketing_start_datetime is not None:
            params['X_hakken_mise_date'] = ticketing_start_datetime.strftime('%Y%m%d%H%M')
            # 発券開始日時状態フラグ
            params['X_hakken_mise_date_sts'] = u'01'
        if ticketing_due_datetime is not None:
            # 発券開始日時状態フラグ
            params['X_hakken_lmt']      = ticketing_due_datetime.strftime('%Y%m%d%H%M')
            # 発券期限日時状態フラグ
            params['X_hakken_lmt_sts']  = u'01'

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
        params['X_saifuban_hakken_lmt'] = ticketing_sub_due_datetime.strftime('%Y%m%d%H%M')

    params['X_hakken_daikin']       = u'%06d' % ticketing_fee
    params['X_ticket_cnt']          = u'%02d' % len(tickets)
    params['X_ticket_hon_cnt']      = u'%02d' % ticket_num

    idx = 1
    for ticket in tickets:
        if need_ticketing(payment_type):
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

    sejTicket = SejTicket()

    sejTicket.shori_kbn     = payment_type.v
    sejTicket.haraikomi_no  = ret.get('X_haraikomi_no')
    sejTicket.ticket_count  = int(ret.get('X_ticket_cnt', 0))
    sejTicket.url_info      = ret.get('X_url_info')
    sejTicket.order_id      = ret.get('X_shop_order_id')
    sejTicket.iraihyo_id_00 = ret.get('iraihyo_id_00')
    sejTicket.order_at      = datetime.now()
    for idx in range(1,sejTicket.ticket_count):
        code = ret.get('X_barcode_no_%02d' % idx)
        if code:
            sejTicket.attributes['X_barcode_no_%02d' % idx] = code
    sejTicket.request_params = dict()
    for k, v in params.iteritems():
        sejTicket.request_params[k] = v
    DBSession.add(sejTicket)
    DBSession.flush()

    return sejTicket


def request_fileget(params):
    '''
    ファイル取得先 https://inticket.sej.co.jp/order/getfile.do
    '''
    payment = SejPayment(secret_key = secret_key, url="https://inticket.sej.co.jp/order/getfile.do")
    return payment.request(params)

'''

    払込票表示 https://inticket.sej.co.jp/order/hi.do
    '''
