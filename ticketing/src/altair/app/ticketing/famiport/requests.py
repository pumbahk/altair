# -*- coding: utf-8 -*-
"""ファミポートから送られてくるリクエストの情報を保持する

変数名はタグ名に合わせる
"""

from .communication import FamiPortRequestType

class FamiPortRequest(object):
    @property
    def request_type(self):
        return self._requestType

    @request_type.setter
    def request_type(self, requestType):
        self._requestType = requestType

    @property
    def encrypted_fields(self):
        return self._encryptedFields

class FamiPortReservationInquiryRequest(FamiPortRequest):
    """予約済み予約照会
    """
    def __init__(self, *args, **kwds):
        self.storeCode = None  # 店舗コード
        self.ticketingDate = None  # 利用日時
        self.reserveNumber = None  # 予約番号
        self.authNumber = None  # 認証番号
        self._requestType = FamiPortRequestType.ReservationInquiry
        self._encryptedFields = []


class FamiPortPaymentTicketingRequest(FamiPortRequest):
    """予約済み入金発券
    """
    def __init__(self, *args, **kwds):
        self.storeCode = None  # 店舗コード
        self.mmkNo = None  # 発券ファミポート番号
        self.ticketingDate = None  # 利用日時
        self.sequenceNo = None  # 処理通番
        self.playGuideId = None  # クライアントID
        self.barCodeNo = None  # 支払番号
        self.customerName = None  # カナ氏名
        self.phoneNumber = None  # 電話番号
        self._requestType = FamiPortRequestType.PaymentTicketing
        self._encryptedFields = ['customerName', 'phoneNumber']


class FamiPortPaymentTicketingCompletionRequest(FamiPortRequest):
    """予約済み入金発券完了
    """
    def __init__(self, *args, **kwds):
        self.storeCode = None  # 店舗コード
        self.mmkNo = None  # 発券ファミポート番号
        self.ticketingDate = None  # 利用日時
        self.sequenceNo = None  # 処理通番
        self.barCodeNo = None  # 支払番号
        self.playGuideId = None  # クライアントID
        self.orderId = None  # 注文ID
        self.totalAmount = None  # 入金金額
        self._requestType = FamiPortRequestType.PaymentTicketingCompletion
        self._encryptedFields = []


class FamiPortPaymentTicketingCancelRequest(FamiPortRequest):
    """予約済み入金発券取消
    """
    def __init__(self, *args, **kwds):
        self.storeCode = None  # 店舗コード
        self.mmkNo = None  # 発券ファミポート番号
        self.ticketingDate = None  # 利用日時
        self.sequenceNo = None  # 処理通番
        self.barCodeNo = None  # 支払番号
        self.playGuideId = None  # クライアントID
        self.orderId = None  # 注文ID
        self.cancelCode = None  # 取消理由
        self._requestType = FamiPortRequestType.PaymentTicketingCancel
        self._encryptedFields = []


class FamiPortInformationRequest(FamiPortRequest):
    """予約済み案内
    """
    def __init__(self, *args, **kwds):
        self.infoKubun = None  # 案内種別
        self.storeCode = None  # 店舗コード
        self.kogyoCode = None  # 興行コード
        self.kogyoSubCode = None  # 興行サブコード
        self.koenCode = None  # 公演コード
        self.uketsukeCode = None  # 受付コード
        self.playGuideId = None  # クライアントID
        self.authCode = None  # 認証コード
        self.reserveNumber = None  # 予約照会番号
        self._requestType = FamiPortRequestType.Information
        self._encryptedFields = []


class FamiPortCustomerInformationRequest(FamiPortRequest):
    """顧客情報取得
    """
    def __init__(self, *args, **kwds):
        self.storeCode = None  # 店舗コード
        self.mmkNo = None  # 発券Famiポート番号
        self.ticketingDate = None  # 利用日時
        self.sequenceNo = None  # 処理通番
        self.barCodeNo = None  # バーコード情報
        self.playGuideId = None  # クライアントID
        self.orderId = None  # 注文ID
        self.totalAmount = None  # 入金金額
        self.requestType = FamiPortRequestType.CustomerInformation
