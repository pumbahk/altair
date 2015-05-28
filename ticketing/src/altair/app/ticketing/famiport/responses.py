# -*- coding: utf-8 -*-
"""ファミポートに送信するレスポンスの情報を保持する

変数名はタグ名に合わせる
"""

from .communication import FamiPortResponseType

class FamiPortResponse(object):

    def __str__(self):
        value_list = []
        for attribute_name in self.__slots__:
            attribute = getattr(self, attribute_name)
            if attribute:
                if not isinstance(attribute, (str, unicode)):
                    value = attribute.value
                else:
                    value = attribute
            else:
                value = None
            value_list.append((attribute_name, value))
        return '\n'.join([str(value) for value in value_list])

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

    __slots__ = ('resultCode', 'replyClass', 'replyCode', 'barCodeNo', 'totalAmount', 'ticketPayment', 'systemFee',
                 'ticketingFee', 'ticketCountTotal', 'ticketCount', 'kogyoName', 'koenDate', 'name', 'nameInput', 'phoneInput')

    def __init__(self, resultCode=None, replyClass=None, replyCode=None, playGuideId=None, barCodeNo=None, totalAmount=None, ticketPayment=None, \
                 systemFee=None, ticketingFee=None, ticketCountTotal=None, ticketCount=None, kogyoName=None, koenDate=None, name=None, nameInput=None, phoneInput=None):
        self.resultCode = resultCode  # 処理結果
        self.replyClass = replyClass  # 応答結果区分
        self.replyCode = replyCode  # 応答結果
        self.playGuideId = playGuideId  # クライアントID
        self.barCodeNo = barCodeNo  # 支払番号
        self.totalAmount = totalAmount  # 合計金額
        self.ticketPayment = ticketPayment  # チケット料金
        self.systemFee = systemFee  # システム利用料
        self.ticketingFee = ticketingFee  # 店頭発券手数料
        self.ticketCountTotal = ticketCountTotal  # チケット枚数
        self.ticketCount = ticketCount  # 本券購入枚数
        self.kogyoName = kogyoName  # 興行名
        self.koenDate = koenDate  # 公園日時
        self.name = name # お客様氏名
        self.nameInput = nameInput  # 氏名要求フラグ
        self.phoneInput = phoneInput  # 電話番号要求フラグ

        self._responseType = FamiPortResponseType.ReservationInquiry
        self._encryptFields = ['name']
        self._encrypt_key = self.barCodeNo



class FamiPortPaymentTicketingResponse(FamiPortResponse):
    """予約済み入金発券
    """

    __slots__ = ('resultCode', 'storeCode', 'sequenceNo', 'barCodeNo', 'orderId', 'replyClass', 'replyCode', 'playGuideId', 'playGuideName',
                 'orderTicketNo', 'exchangeTicketNo', 'ticketingStart', 'ticketingEnd', 'totalAmount', 'ticketPayment',
                 'systemFee', 'ticketingFee', 'ticketCountTotal', 'ticketCount', 'kogyoName', 'koenDate', 'ticket')

    def __init__(self, resultCode=None, storeCode=None, sequenceNo=None, barCodeNo=None, orderId=None, replyClass=None, replyCode=None, playGuideId=None, playGuideName=None, \
                 orderTicketNo=None, exchangeTicketNo=None, ticketingStart=None, ticketingEnd=None, totalAmount=None, ticketPayment=None, systemFee=None, ticketingFee=None, \
                 ticketCountTotal=None, ticketCount=None, kogyoName=None, koenDate=None, ticket=None):
        self.resultCode = resultCode  # 処理結果
        self.storeCode = storeCode  # 店舗コード
        self.sequenceNo = sequenceNo  # 処理通番
        self.barCodeNo = barCodeNo  # 支払番号
        self.orderId = orderId  # 注文ID
        self.replyClass = replyClass  # 応答結果区分
        self.replyCode = replyCode  # 応答結果
        self.playGuideId = playGuideId  # クライアントID
        self.playGuideName = playGuideName  # クライアント漢字名称

        ##
        self.orderTicketNo = orderTicketNo  # 払込票番号
        self.exchangeTicketNo = exchangeTicketNo  # 引換票番号
        self.ticketingStart = ticketingStart  # 発券開始日時
        self.ticketingEnd = ticketingEnd  # 発券期限日時
        self.totalAmount = totalAmount  # 合計金額
        self.ticketPayment = ticketPayment  # チケット料金
        self.systemFee = systemFee  # システム利用料
        self.ticketingFee = ticketingFee  # 店頭発券手数料
        self.ticketCountTotal = ticketCountTotal  # チケット枚数
        self.ticketCount = ticketCount  # 本券購入枚数
        self.kogyoName = kogyoName  # 興行名
        self.koenDate = koenDate  # 公演日時

        ##
        self.ticket = ticket  # チケット情報 (FamiPortTicketのリスト)

        self._responseType = FamiPortResponseType.PaymentTicketing
        self._encryptFields = []
        self._encrypt_key = None


class FamiPortTicket(object):
    """チケット情報

    FamiPortPaymentTicketingResponseに含まれる情報です。
    このクラスに対応する単体のレスポンスはありません。
    """

    __slots__ = ('barCodeNo', 'ticketClass', 'templateCode', 'ticketData')

    def __init__(self, barCodeNo=None, ticketClass=None, templateCode=None, ticketData=None):
        self.barCodeNo = barCodeNo  # チケットバーコード番号
        self.ticketClass = ticketClass  # チケット区分
        self.templateCode = templateCode  # テンプレートコード
        self.ticketData = ticketData  # 券面データ


class FamiPortPaymentTicketingCompletionResponse(FamiPortResponse):
    """予約済み入金発券完了
    """

    __slots__ = ('resultCode', 'storeCode', 'sequenceNo', 'barCodeNo', 'orderId', 'replyCode')

    def __init__(self, resultCode=None, storeCode=None, sequenceNo=None, barCodeNo=None, orderId=None, replyCode=None):
        self.resultCode = resultCode  # 処理結果
        self.storeCode = storeCode  # 店舗コード
        self.sequenceNo = sequenceNo  # 処理通番
        self.barCodeNo = barCodeNo  # 支払番号
        self.orderId = orderId  # 注文ID
        self.replyCode = replyCode  # 応答結果

        self._responseType = FamiPortResponseType.PaymentTicketingCompletion
        self._encryptFields = []
        self._encrypt_key = None


class FamiPortPaymentTicketingCancelResponse(FamiPortResponse):
    """予約済み入金発券取消
    """

    __slots__ = ('resultCode', 'storeCode', 'sequenceNo', 'barCodeNo', 'orderId', 'replyCode')

    def __init__(self, resultCode=None, storeCode=None, sequenceNo=None, barCodeNo=None, orderId=None, replyCode=None):
        self.resultCode = resultCode  # 処理結果
        self.storeCode = storeCode  # 店舗コード
        self.sequenceNo = sequenceNo  # 処理通番
        self.barCodeNo = barCodeNo  # 支払番号
        self.orderId = orderId  # 注文ID
        self.replyCode = replyCode  # 応答結果

        self._responseType = FamiPortResponseType.PaymentTicketingCancel
        self._encryptFields = []
        self._encrypt_key = None


class FamiPortInformationResponse(FamiPortResponse):
    """予約済み案内
    """

    __slots__ = ('resultCode', 'infoKubun', 'infoMessage')

    _responseType = FamiPortResponseType.Information
    _encryptFields = []
    _encrypt_key = None

    def __init__(self, resultCode=None, infoKubun=None, infoMessage=None):
        super(FamiPortInformationResponse, self).__init__()
        self.resultCode = resultCode  # 処理結果
        self.infoKubun = infoKubun  # 案内区分
        self.infoMessage = infoMessage  # 案内文言

        self._responseType = FamiPortResponseType.Information
        self._encryptFields = []
        self._encrypt_key = None


class FamiPortCustomerInformationResponse(FamiPortResponse):
    """顧客情報取得
    """

    _encrypt_key = None

    __slots__ = ('resultCode', 'replyCode', 'name', 'memberId', 'address1', 'address2', 'identifyNo')

    def __init__(self, resultCode=None, replyCode=None, name=None, memberId=None, address1=None, address2=None, identifyNo=None):
        self.resultCode = resultCode  # 処理結果
        self.replyCode = replyCode  # 応答結果
        self.name = name  # 氏名
        self.memberId = memberId  # 会員ID
        self.address1 = address1  # 住所1
        self.address2 = address2  # 住所2
        self.identifyNo = identifyNo  # 半券個人識別番号

        self._responseType = FamiPortResponseType.CustomerInformation
        self._encryptFields = ['name', 'memberId', 'address1', 'address2', 'identifyNo']
        self._encrypt_key = None # orderId to be set

    def set_encryptKey(self, encrypt_key):
        self._encrypt_key = encrypt_key

    @property
    def encrypt_key(self):
        return self._encrypt_key
