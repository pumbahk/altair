# -*- coding: utf-8 -*-
"""ファミポートから送られてくるリクエストの情報を保持する

変数名はタグ名に合わせる
"""


class FamiPortReservationInquiryRequest(object):
    """予約済み予約照会
    """
    def __init__(self, *args, **kwds):
        self.storeCode = None  # 店舗コード
        self.ticketingDate = None  # 利用日時
        self.reserveNumber = None  # 予約番号
        self.authNumber = None  # 認証番号


class FamiPortPaymentTicketingRequest(object):
    """予約済み入金発券
    """
    def __init__(self, *args, **kwds):
        self.storeCode = None  # 店舗コード
        self.mmkNo = None  # 発券ファミポート番号
        self.ticketingDate = None  # 利用日時
        self.sequenceNo = None  # 処理通番
        self.barCodeNo = None  # バーコード情報
        self.customerName = None  # カナ氏名
        self.phoneNumber = None  # 電話番号


class FamiPortPaymentTicketingCompletionRequest(object):
    """予約済み入金発券完了
    """
    def __init__(self, *args, **kwds):
        self.storeCode = None  # 店舗コード
        self.mmkNo = None  # 発券ファミポート番号
        self.ticketingDate = None  # 利用日時
        self.sequenceNo = None  # 処理通番
        self.requestClass = None  # 要求区分
        self.barCodeNo = None  # バーコード情報
        self.playGuideId = None  # クライアントID
        self.orderId = None  # 注文ID
        self.totalAmount = None  # 入金金額


class FamiPortPaymentTicketingCancelRequest(object):
    """予約済み入金発券取消
    """
    def __init__(self, *args, **kwds):
        self.storeCode = None  # 店舗コード
        self.mmkNo = None  # 発券ファミポート番号
        self.ticketingDate = None  # 利用日時
        self.sequenceNo = None  # 処理通番
        self.requestClass = None  # 要求区分
        self.barCodeNo = None  # バーコード情報
        self.playGuideId = None  # クライアントID
        self.orderId = None  # 注文ID
        self.cancelCode = None  # 取消理由


class FamiPortInformationRequest(object):
    """予約済み案内
    """
    def __init__(self, *args, **kwds):
        self.infoKubun = None  # 案内種別
        self.storeCode = None  # 店舗コード
        self.kogyoCode = None  # 興行コード
        self.kogyoSubCode = None  # 興行サブコード
        self.koenCode = None  # 公演コード
        self.uketsukeCode = None  # 受付コード
        self.authCode = None  # 認証コード
        self.reserveNumber = None  # 予約照会番号
