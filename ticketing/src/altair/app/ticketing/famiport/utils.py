# -*- coding: utf-8 -*-

from enum import IntEnum

class FamiPortRequestType(IntEnum):
    ReservationInquiry         = 1 # 予約済み予約照会
    PaymentTicketing           = 2 # 予約済み入金発券
    PaymentTicketingCompletion = 3 # 予約済み入金発券完了
    PaymentTicketingCancel     = 4 # 予約済み入金発券取消
    Information                = 5 # 予約済み案内