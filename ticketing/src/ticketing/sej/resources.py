# -*- coding: utf-8 -*-

from ticketing.utils import StandardEnum

class TicketingApiResource(object):
    def __init__(self, request):
        self.request = request

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
    Ticket                  = 2
    # 2:本券(チケットバーコード無し)
    TicketWithBarcode       = 1
    # 3:本券以外(チケットバーコード有り)
    ExtraTicket             = 4
    # 4:本券以外(チケットバーコード無し)
    ExtraTicketWithBarcode  = 3

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

class SejNotificationType(StandardEnum):
    # '01':入金発券完了通知
    PaymentComplete = 1
    # '31':SVC強制取消通知
    CancelFromSVC = 31
    # '72':再付番通知
    ReGrant = 72
    # '73':発券期限切れ
    TicketingExpire = 73
    # 91
    InstantPaymentInfo = 91



class SejError(Exception):

    error_type  = 0
    error_msg   = ''
    error_field = ''

    def __init__(self, error_type, error_msg, error_field, error_body):

        self.error_type = error_type
        self.error_field = error_field
        self.error_msg = error_msg

    def __str__(self):
        return "Error_Type=%d&Error_Msg=%s&Error_Field=%s" % (self.error_type, self.error_type, self.error_field)

class SejServerError(Exception):

    status_code  = 0
    reason      = ''
    body        = ''

    def __init__(self, status_code, reason, body):

        self.status_code = status_code
        self.reason = reason
        self.body = body

    def __str__(self):
        return "status_code=%d&reason=%s: body: %s" % (self.status_code, self.reason, self.body)

def make_sej_response(params):
    import urllib2
    def make_senb_data(data):
        return '<SENBDATA>%s</SENBDATA>' % data

    return make_senb_data('&'.join(["%s=%s" % (k, urllib2.quote(v)) for k, v in params.items()]) + '&') + \
           make_senb_data('DATA=END')

class SejResponseError(Exception):

    code = 0
    reason = ''
    params = dict()

    def __init__(self, code, reason, params):
        self.code = code
        self.reason = reason
        self.params = params

    def response(self):
        return make_sej_response(self.params)


