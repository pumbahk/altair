# -*- coding: utf-8 -*-
import re
import urllib2
import hashlib
import logging
from datetime import datetime

from .exceptions import SejRequestError
from .resources import is_ticket, need_ticketing, SejTicketType, SejPaymentType
from .utils import JavaHashMap

log = logging.getLogger('sej_payment')
ascii_regex = re.compile(r'[^\x20-\x7E]')

def make_sej_response(params):
    def make_senb_data(data):
        return '<SENBDATA>%s</SENBDATA>' % data

    return make_senb_data('&'.join(["%s=%s" % (k, urllib2.quote(v)) for k, v in params.items()]) + '&') + \
           make_senb_data('DATA=END')

def parse_sej_response(body, tag_name):
    regex_tags = re.compile(r"<" + tag_name + ">([^<>]+)</"+tag_name+">")
    regex_params = re.compile(r"([^&=]+)=([^&=]+)")
    matches = regex_tags.findall(body)
    key_value = {}
    for match in matches:
        for key,val in regex_params.findall(match):
            key_value[key] = val
    return key_value

def create_sej_request(url, request_params):
    req = urllib2.Request(url)

    buffer = ["%s=%s" % (name, urllib2.quote(unicode(param).encode('shift_jis', 'xmlcharrefreplace'))) for name, param in request_params.iteritems()]
    data = "&".join(buffer)

    log.info("[request]%s" % data)

    req.add_data(data)
    req.add_header('User-Agent', 'SejPaymentForJava/2.00')
    req.add_header('Connection', 'close')

    return req

def create_md5hash_from_dict(kv, secret_key):
    tmp_keys = JavaHashMap()
    key_array = list(kv.iterkeys())
    for key, value in kv.iteritems():
        tmp_keys[key.lower()] = value
    key_array.sort()
    buffer = [tmp_keys[key.lower()] for key in key_array]
    buffer.append(secret_key)
    buffer = u','.join(buffer)
    logging.debug('hash:' + buffer)
    return hashlib.md5(buffer.encode(encoding="UTF-8")).hexdigest()

def create_hash_from_x_start_params(params, secret_key):

    falsify_props = dict()
    for name,param in params.iteritems():
        if name.startswith('X_'):
            result = ascii_regex.search(param)
            if result:
                raise SejRequestError(u"%s is must be ascii (%s)" % (name, param))

            falsify_props[name] = param

    hash = create_md5hash_from_dict(falsify_props, secret_key)

    return hash

def create_request_params(params, secret_key):
    xcode = create_hash_from_x_start_params(params, secret_key)
    params['xcode'] = xcode
    return params


def create_sej_request_data(
        order_id,
        total,
        ticket_total,
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
    params['X_shop_order_id']   = order_id

    if payment_type != SejPaymentType.Paid and payment_due_at:
        # コンビニでの決済を行う場合の支払い期限の設定
        params['X_pay_lmt']         = payment_due_at.strftime('%Y%m%d%H%M')

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
        if ticketing_start_at is not None:
            params['X_hakken_mise_date'] = ticketing_start_at.strftime('%Y%m%d%H%M')
            # 発券開始日時状態フラグ
        else:
            params['X_hakken_mise_date_sts'] = u'1'

        if ticketing_due_at is not None:
            # 発券開始日時状態フラグ
            params['X_hakken_lmt']      = ticketing_due_at.strftime('%Y%m%d%H%M')
            # 発券期限日時状態フラグ
        else:
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
