# -*- coding: utf-8 -*-
"""ファミポートに送信するレスポンスの情報を保持する

変数名はタグ名に合わせる
"""

from .utils import FamiPortResponseType

class FamiPortResponse(object):
    # __slots__ = ()

    def __init__(self, *args, **kwds):
        pass

    @property
    def response_type(self):
        return self._responseType

    @property
    def encrypt_fields(self):
        return self._encryptFields

    @property
    def encrypt_key(self):
        return self._encrypt_key

class FamiPortReservationInquiryResponse(FamiPortResponse):
    """予約済み予約照会
    """

    # __slots__ = ('resultCode', 'replyClass', 'replyCode', 'barCodeNo', 'totalAmount', 'ticketPayment', 'systemFee',
    #             'ticketingFee', 'ticketCountTotal', 'ticketCount', 'kogyoName', 'koenDate', 'name', 'nameInput', 'phoneInput')

    def __init__(self, *args, **kwds):
        self.resultCode = None  # 処理結果
        self.replyClass = None  # 応答結果区分
        self.replyCode = None  # 応答結果
        self.barCodeNo = None  # 支払番号
        self.totalAmount = None  # 合計金額
        self.ticketPayment = None  # チケット料金
        self.systemFee = None  # システム利用料
        self.ticketingFee = None  # 店頭発券手数料
        self.ticketCountTotal = None  # チケット枚数
        self.ticketCount = None  # 本券購入枚数
        self.kogyoName = None  # 興行名
        self.koenDate = None  # 公園日時
        self.name = None # お客様氏名
        self.nameInput = None  # 氏名要求フラグ
        self.phoneInput = None  # 電話番号要求フラグ
        self._responseType = FamiPortResponseType.ReservationInquiry
        self._encryptFields = ['name']
        self._encrypt_key = self.barCodeNo



class FamiPortPaymentTicketingResponse(FamiPortResponse):
    """予約済み入金発券
    """

    # __slots__ = ('resultCode', 'storeCode', 'sequenceNo', 'barCodeNo', 'orderId', 'replyClass', 'replyCode', 'playGuideId', 'playGuideName',
    #             'orderTicketNo', 'exchangeTicketNo', 'ticketingStart', 'ticketingEnd', 'totalAmount', 'ticketPayment',
    #             'systemFee', 'ticketingFee', 'ticketCountTotal', 'ticketCount', 'kogyoName', 'koenDate', 'ticket')

    def __init__(self, *args, **kwds):
        self.resultCode = None  # 処理結果
        self.storeCode = None  # 店舗コード
        self.sequenceNo = None  # 処理通番
        self.barCodeNo = None  # 支払番号
        self.orderId = None  # 注文ID
        self.replyClass = None  # 応答結果区分
        self.replyCode = None  # 応答結果
        self.playGuideId = None  # クライアントID
        self.playGuideName = None  # クライアント漢字名称

        ##
        self.orderTicketNo = None  # 払込票番号
        self.exchangeTicketNo = None  # 引換票番号
        self.ticketingStart = None  # 発券開始日時
        self.ticketingEnd = None  # 発券期限日時
        self.totalAmount = None  # 合計金額
        self.ticketPayment = None  # チケット料金
        self.systemFee = None  # システム利用料
        self.ticketingFee = None  # 店頭発券手数料
        self.ticketCountTotal = None  # チケット枚数
        self.ticketCount = None  # 本券購入枚数
        self.kogyoName = None  # 興行名
        self.koenDate = None  # 公演日時

        ##
        self.ticket = []  # チケット情報 (FamiPortTicketのリスト)

        self._responseType = FamiPortResponseType.PaymentTicketing
        self._encryptFields = []
        self._encrypt_key = None


class FamiPortTicket(object):
    """チケット情報

    FamiPortPaymentTicketingResponseに含まれる情報です。
    このクラスに対応する単体のレスポンスはありません。
    """

    # __slots__ = ('barCodeNo', 'ticketClass', 'templateCode', 'ticketData')

    def __init__(self, *args, **kwds):
        self.barCodeNo = None  # チケットバーコード番号
        self.ticketClass = None  # チケット区分
        self.templateCode = None  # テンプレートコード
        self.ticketData = None  # 券面データ


class FamiPortPaymentTicketingCompletionResponse(FamiPortResponse):
    """予約済み入金発券完了
    """

    # __slots__ = ('resultCode', 'storeCode', 'sequenceNo', 'barCodeNo', 'orderId', 'replyCode')

    def __init__(self, *args, **kwds):
        self.resultCode = None  # 処理結果
        self.storeCode = None  # 店舗コード
        self.sequenceNo = None  # 処理通番
        self.barCodeNo = None  # 支払番号
        self.orderId = None  # 注文ID
        self.replyCode = None  # 応答結果
        self._responseType = FamiPortResponseType.PaymentTicketingCompletion
        self._encryptFields = []
        self._encrypt_key = None


class FamiPortPaymentTicketingCancelResponse(FamiPortResponse):
    """予約済み入金発券取消
    """

    # __slots__ = ('resultCode', 'storeCode', 'sequenceNo', 'barCodeNo', 'orderId', 'replyCode')

    def __init__(self, *args, **kwds):
        self.resultCode = None  # 処理結果
        self.storeCode = None  # 店舗コード
        self.sequenceNo = None  # 処理通番
        self.barCodeNo = None  # 支払番号
        self.orderId = None  # 注文ID
        self.replyCode = None  # 応答結果
        self._responseType = FamiPortResponseType.PaymentTicketingCancel
        self._encryptFields = []
        self._encrypt_key = None


class FamiPortInformationResponse(FamiPortResponse):
    """予約済み案内
    """

    # __slots__ = ('resultCode', 'infoKubun', 'infoMessage')

    def __init__(self, *args, **kwds):
        self.resultCode = None  # 処理結果
        self.infoKubun = None  # 案内区分
        self.infoMessage = None  # 案内文言
        self._responseType = FamiPortResponseType.Information
        self._encryptFields = []
        self._encrypt_key = None


class FamiPortCustomerInformationResponse(FamiPortResponse):
    """顧客情報取得
    """

    # __slots__ = ('resultCode', 'replyCode', 'name', 'memberId', 'address1', 'address2', 'identifyNo')

    def __init__(self, *args, **kwds):
        self.resultCode = None  # 処理結果
        self.replyCode = None  # 応答結果
        self.name = None  # 氏名
        self.memberId = None  # 会員ID
        self.address1 = None  # 住所1
        self.address2 = None  # 住所2
        self.identifyNo = None  # 半券個人識別番号
        self._requestType = FamiPortResponseType.CustomerInformation
        self._encryptFields = ['name', 'memberId', 'address1', 'address2', 'identifyNo']
        self._encrypt_key = 'test_key' # TODO get FamiPortPaymentTicketingResponse.orderId in some way