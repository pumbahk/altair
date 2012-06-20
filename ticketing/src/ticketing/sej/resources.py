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
code_from_payment_type = {
    SejPaymentType.CashOnDelivery.v : SejPaymentType.CashOnDelivery,
    SejPaymentType.Prepayment.v : SejPaymentType.Prepayment,
    SejPaymentType.Paid.v : SejPaymentType.Paid,
    SejPaymentType.PrepaymentOnly.v : SejPaymentType.PrepaymentOnly,
}

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
code_from_ticket_type = {
    SejTicketType.Ticket.v : SejTicketType.Ticket,
    SejTicketType.TicketWithBarcode.v : SejTicketType.TicketWithBarcode,
    SejTicketType.ExtraTicket.v : SejTicketType.ExtraTicket,
    SejTicketType.ExtraTicketWithBarcode.v : SejTicketType.ExtraTicketWithBarcode,
}

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

code_from_update_reason = {
    SejOrderUpdateReason.Change.v : SejOrderUpdateReason.Change,
    SejOrderUpdateReason.Stop.v : SejOrderUpdateReason.Stop,
}
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

    # 5-1.入金速報
    FileInstantPaymentInfo  = 94
    # 5-2.支払期限切れ
    FilePaymentExpire       = 51
    # 5-3.発券期限切れ
    FileTicketingExpire     = 61
    # 5-4.払戻速報
    FileRefundExpire        = 92
    # 6-1.支払い案内
    FileCheckInfo           = 94
    # 6-2.会計取消(入金)
    FilePaymentCancel       = 95
    # 6-3.会計取消(発券)
    FileTicketingCancel     = 96


code_from_notification_type = {
    SejNotificationType.PaymentComplete.v : SejNotificationType.PaymentComplete,
    SejNotificationType.CancelFromSVC.v : SejNotificationType.CancelFromSVC,
    SejNotificationType.ReGrant.v : SejNotificationType.ReGrant,
    SejNotificationType.TicketingExpire.v : SejNotificationType.TicketingExpire,
    SejNotificationType.InstantPaymentInfo.v : SejNotificationType.InstantPaymentInfo,
    SejNotificationType.FileInstantPaymentInfo.v : SejNotificationType.FileInstantPaymentInfo
}

name_from_notification_type = {
    'PaymentComplete'    : SejNotificationType.PaymentComplete,
    'CancelFromSVC'      : SejNotificationType.CancelFromSVC,
    'ReGrant'            : SejNotificationType.ReGrant,
    'TicketingExpire'    : SejNotificationType.TicketingExpire,
    'InstantPaymentInfo' : SejNotificationType.InstantPaymentInfo
}





