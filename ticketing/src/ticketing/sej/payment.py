# -*- coding:utf-8 -*-

import hashlib
import time
import re
from datetime import datetime
import urllib2

from models import SejTicket


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
    '''
        1, 5, 12, 2, 2, 13, 13, 6, 2, 2, 2, 2, 14, 32

    '''
    def parse_row(self, row):
        row = SejFileParserRow(row)
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
        row = SejFileParserRow(row)
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
    '''
        payment = SejPayment(secret_key = '.......')
        payment.request({
            ## ショップIDを設定
            u"X_shop_id": u"myshopid",
            ## 注文IDを設定
            "X_shop_order_id": u"orderid00001",
            ## お客様氏名を設定
            u"user_namek": u"お客様氏名",
            ## お客様氏名カナを設定
            u"user_name_kana": u"フリガナ",
            ## お客様電話番号を設定
            u"X_user_tel_no": u"myusertelno",
            ## 処理区分を設定(例:代引き)
            u"X_shori_kbn": u"01",
            ## 合計金額を設定(例:\12,000)
            u"X_goukei_kingaku": u"012000",
            ## 支払期限日時を設定(例:2010年2月28日 10時45分)
            u"X_pay_lmt": u"201002281045",
            ## チケット代金を設定(例:\9,000)
            u"X_ticket_daikin": u"009000",
            ## チケット購入代金を設定(例:\1,000)
            u"X_ticket_kounyu_daikin": u"001000",
            ## 発券代金を設定(例:\2,000)
            u"X_hakken_daikin": u"002000",
            ## チケット枚数を設定(例:1枚)
            u"X_ticket_cnt": u"01",
            ## 本券購入枚数を設定(例:1枚)
            u"X_ticket_hon_cnt": u"01",
            ## チケット区分を設定(例:1[本券（チケットバーコード有り）])
            u"X_ticket_kbn_01": u"1",
            ## 興行名を設定
            u"kougyo_mei_01": u"興行名称",
            ## 公演名を設定
            u"kouen_mei_01": u"公演名",
            ## 公演日時を設定(例:2010年3月1日9時)
            u"X_kouen_date_01": u"201003010900",
            ## チケットテンプレートを設定
            u"X_ticket_template_01": u"mytemplate",
            ## 券面情報を設定
            u"ticket_text_01": u"<?xml version='1.0' encoding='Shift_JIS' ?><TICKET><MR01>…",
        }, 0 ,1)
    '''

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

    def create_md5hash_from_dict(self, keys, private_key):
        tmp_keys = {}
        key_array = keys.keys()
        for key,value in keys:
            tmp_keys[key.lowercase()] = value
        key_array.sort()
        buffer = ''
        for key in key_array:
            buffer += tmp_keys[key.lowercase()] + ','
        buffer + private_key
        return hashlib.md5(buffer).hexdigest()

    def create_hash_from_x_start_params(self, params, salt_key):
        falsifyProps = []
        for param in params:
            if param.startswith('X_'):
                falsifyProps.append(param)
        hash = self.create_md5hash_from_dict(falsifyProps, salt_key)

    def send_request(self, request_params, mode, retry_flg):
        for count in range(self.retry_count):
            if count > 0:
                time.sleep(self.retry_interval)
            ret_val = self._send_request(mode, mode, retry_flg);
            if ret_val != 120 and ret_val != 5:
                return ret_val

        return 0

    def _send_request(self, request_params, mode, retry_flg):

        if retry_flg:
            request_params['retry_cnt'] = '1'

        req = urllib2.Request(self.url)
        req.add_header('User-Agent', 'SejPaymentForJava/2.00')
        req.add_header('Connection', 'close')
        res = urllib2.urlopen(req)

        status = res.status
        reason = res.reason

        if status == 200:
#           status = 900;
            reason = "Script syntax error"

        # ステータス800，902，910以外の場合は終了　戻り値：0
        if status != 800 and status != 902 and status != 910:
            return status
        # キャンセルかつステータス800の場合は終了　戻り値：0
        if status == 800 and mode == 1:
            return status

        body = res.read()
        self.response = self.parse(body, "SENBDATA")

        if status >= 900:
            return status - 800
        if status != 800:
            return status / 100

        return 0

    def parse(self, body, tag_name):
        regex_tags = re.compile(r"<" + tag_name + ">([^<>]+)</"+tag_name+">")
        regex_params = re.compile(r"([^&=]+)=([^&=]+)")
        matches = regex_tags.findall(body)
        key_value = {}
        for match in matches:
            for key,val in regex_params.findall(match):
                key_value[key] = val
        return key_value

secret_key ='';

def set_secret_key(key):
    secret_key = key

def request_order(params):
    '''
    決済要求 https://inticket.sej.co.jp/order/order.do
    '''
    payment = SejPayment(secret_key = secret_key, url="https://inticket.sej.co.jp/order/order.do")
    return payment.request(params)


def request_cancel(params):
    '''
    注文キャンセル https://inticket.sej.co.jp/order/cancelorder.do
    '''
    payment = SejPayment(secret_key = secret_key, url="https://inticket.sej.co.jp/order/cancelorder.do")
    return payment.request(params)

def request_update_order(params):
    '''
    注文情報更新 https://inticket.sej.co.jp/order/updateorder.do
    '''
    payment = SejPayment(secret_key = secret_key, url="https://inticket.sej.co.jp/order/updateorder.do")
    return payment.request(params)

def request_fileget(params):
    '''
    ファイル取得先 https://inticket.sej.co.jp/order/getfile.do
    '''
    payment = SejPayment(secret_key = secret_key, url="https://inticket.sej.co.jp/order/getfile.do")
    return payment.request(params)

'''

    払込票表示 https://inticket.sej.co.jp/order/hi.do
    '''
