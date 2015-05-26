# -*- coding: utf-8 -*-
import time
import random
import hashlib
import sqlalchemy as sa
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import scoped_session, sessionmaker
import sqlahelper
from altair.models import Identifier, WithTimestamp
from .utils import (
    FamiPortRequestType,
    FamiPortResponseType,
    InformationResultCodeEnum,
    )
from .exc import FamiPortNumberingError


Base = sqlahelper.get_base()

# 内部トランザクション用
_session = scoped_session(sessionmaker())


def create_random_sequence_number(length, prefix=''):
    seq = prefix
    while len(seq) < length:
        seq += hashlib.md5((str(time.time()) + str(random.random())).encode()).hexdigest()
    return seq[:length]


class FamiPortOrderNoSequence(Base, WithTimestamp):
    __tablename__ = 'FamiPortOrderNoSequence'

    id = sa.Column(Identifier, primary_key=True)

    @classmethod
    def get_next_value(cls, name):
        seq = cls()
        _session.add(seq)
        _session.flush()
        return seq.id


class FamiPortOrderIdentifierSequence(Base, WithTimestamp):
    __tablename__ = 'FamiPortOrderIdentifierSequence'

    id = sa.Column(Identifier, primary_key=True)

    @classmethod
    def get_next_value(cls, name=''):
        seq = cls()
        _session.add(seq)
        _session.flush()
        return seq.id


class FamiPortOrderTicketNoSequence(Base, WithTimestamp):
    __tablename__ = 'FamiPortOrderTicketNoSequence'

    id = sa.Column(Identifier, primary_key=True)
    value = sa.Column(sa.String(12), nullable=False, unique=True)

    @classmethod
    def get_next_value(cls, *args, **kwds):
        for ii in range(15):  # retry count
            try:
                return cls._get_next_value(*args, **kwds)
            except InvalidRequestError:
                pass
        raise FamiPortNumberingError()

    @classmethod
    def _get_next_value(cls, name=''):
        seq = cls(value=create_random_sequence_number(13, name))
        _session.add(seq)
        _session.flush()
        return seq.value


class FamiPortExchangeTicketNoSequence(Base, WithTimestamp):
    __tablename__ = 'FamiPortExchangeTicketNoSequence'

    id = sa.Column(Identifier, primary_key=True)
    value = sa.Column(sa.String(12), nullable=False, unique=True)

    @classmethod
    def get_next_value(cls, *args, **kwds):
        for ii in range(15):  # retry count
            try:
                return cls._get_next_value(*args, **kwds)
            except InvalidRequestError:
                pass
        raise FamiPortNumberingError()

    @classmethod
    def _get_next_value(cls, name=''):
        seq = cls(value=create_random_sequence_number(13, name))
        _session.add(seq)
        _session.flush()
        return seq.value


class FamiPortReserveNumberSequence(Base, WithTimestamp):
    __tablename__ = 'FamiPortReserveNumberSequence'

    id = sa.Column(Identifier, primary_key=True)
    value = sa.Column(sa.String(12), nullable=False, unique=True)

    @classmethod
    def get_next_value(cls, *args, **kwds):
        for ii in range(15):  # retry count
            try:
                return cls._get_next_value(*args, **kwds)
            except InvalidRequestError:
                pass
        raise FamiPortNumberingError()

    @classmethod
    def _get_next_value(cls, name=''):
        seq = cls(value=create_random_sequence_number(13, name))
        _session.add(seq)
        _session.flush()
        return seq.value


class FamiPortOrder(Base, WithTimestamp):
    __tablename__ = 'FamiPortOrder'

    id = sa.Column(Identifier, primary_key=True)
    order_no = sa.Column(sa.String(255), nullable=False)
    barcode_no = sa.Column(sa.String(255), nullable=False)

    name = sa.Column(sa.Unicode(42), nullable=False)  # 氏名
    playguide_id = sa.Column(sa.String, default='', nullable=False)  # クライアントID
    famiport_order_identifier = sa.Column(sa.String, nullable=False)  # 予約番号
    reserve_number = sa.Column(sa.String)  # 予約番号
    barcode_no = sa.Column(sa.String)  # 支払番号
    exchange_number = sa.Column(sa.String)  # 引換票番号(後日予済アプリで発券するための予約番号)
    total_amount = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False)  # 入金金額
    ticket_payment = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False)  # チケット料金
    system_fee = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False)  # システム利用料
    ticketing_fee = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False)  # 店頭発券手数料
    koen_date = sa.Column(sa.DateTime, nullable=True)  # 公演日時
    kogyo_name = sa.Column(sa.Unicode(40), nullable=False)  # 興行名
    ticket_total_count = sa.Column(sa.Integer, nullable=False)  # 本件購入枚数
    ticket_count = sa.Column(sa.Integer, nullable=False)  # 本件購入枚数
    name_input = sa.Column(sa.Boolean, nullable=False, default=0)  # 氏名要求フラグ
    phone_input = sa.Column(sa.Boolean, nullable=False, default=0)  # 電話番号要求フラグ
    phone_number = sa.Column(sa.Unicode(12), nullable=False)  # 電話番号
    address_1 = sa.Column(sa.Unicode(200), nullable=False, default=u'')  # 住所1
    address_2 = sa.Column(sa.Unicode(200), nullable=False, default=u'')  # 住所2
    auth_number = sa.Column(sa.String(13))  # 認証番号

    @classmethod
    def get_from_orderId(cls, orderId):
        FamiPortOrder.filter_by() # TODO filter by orderId

    @classmethod
    def get_by_reserveNumber(cls, reserveNumber):
        FamiPortOrder.filter_by().one() # TODO filter by reserveNumber


class FamiPortInformationMessage(Base, WithTimestamp):
    __tablename__ = 'FamiPortInformationMessage'
    __table_args__ = (sa.UniqueConstraint('result_code'),)

    id = sa.Column(Identifier, primary_key=True)
    result_code = sa.Column(sa.Enum('WithInformation', 'ServiceUnavailable'), unique=True, nullable=False)
    message = sa.Column(sa.Unicode(length=1000), nullable=True)

    @classmethod
    def create(cls, result_code, message):
        return cls(result_code=result_code, message=message)

    def save(self):
        _session.add(self)
        _session.flush()

    @classmethod
    def get_message(cls, information_result_code, default_message=None):
        if not isinstance(information_result_code, InformationResultCodeEnum):
            return None
        query = _session.query(FamiPortInformationMessage).filter_by(result_code=information_result_code.name)
        famiport_information_message = query.first()
        if famiport_information_message:
            return famiport_information_message.message
        else:
            return default_message


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


class FamiPortReservationInquiryRequest(Base, WithTimestamp, FamiPortRequest):
    """予約済み予約照会
    """
    __tablename__ = 'FamiPortReservationInquiryRequest'

    id = sa.Column(Identifier, primary_key=True)
    storeCode = sa.Column(sa.String)  # 店舗コード
    ticketingDate = sa.Column(sa.String)  # 利用日時
    reserveNumber = sa.Column(sa.String)  # 予約番号
    authNumber = sa.Column(sa.String)  # 認証番号

    _requestType = FamiPortRequestType.ReservationInquiry
    _encryptedFields = ()


class FamiPortPaymentTicketingRequest(Base, WithTimestamp, FamiPortRequest):
    """予約済み入金発券
    """
    __tablename__ = 'FamiPortPaymentTicketingRequest'

    id = sa.Column(Identifier, primary_key=True)
    storeCode = sa.Column(sa.String)  # 店舗コード
    mmkNo = sa.Column(sa.String)  # 発券ファミポート番号
    ticketingDate = sa.Column(sa.String)  # 利用日時
    sequenceNo = sa.Column(sa.String)  # 処理通番
    playGuideId = sa.Column(sa.String, nullable=False, default='')  # クライアントID
    barCodeNo = sa.Column(sa.String)  # 支払番号
    customerName = sa.Column(sa.String)  # カナ氏名
    phoneNumber = sa.Column(sa.String)  # 電話番号

    _requestType = FamiPortRequestType.PaymentTicketing
    _encryptedFields = ['customerName', 'phoneNumber']


class FamiPortPaymentTicketingCompletionRequest(Base, WithTimestamp, FamiPortRequest):
    """予約済み入金発券完了
    """
    __tablename__ = 'FamiPortPaymentTicketingCompletionRequest'

    id = sa.Column(Identifier, primary_key=True)
    storeCode = sa.Column(sa.String)  # 店舗コード
    mmkNo = sa.Column(sa.String)  # 発券ファミポート番号
    ticketingDate = sa.Column(sa.String)  # 利用日時
    sequenceNo = sa.Column(sa.String)  # 処理通番
    barCodeNo = sa.Column(sa.String)  # 支払番号
    playGuideId = sa.Column(sa.String)  # クライアントID
    orderId = sa.Column(sa.String)  # 注文ID
    totalAmount = sa.Column(sa.String)  # 入金金額

    _requestType = FamiPortRequestType.PaymentTicketingCompletion
    _encryptedFields = []


class FamiPortPaymentTicketingCancelRequest(Base, WithTimestamp, FamiPortRequest):
    """予約済み入金発券取消
    """
    __tablename__ = 'FamiPortPaymentTicketingCancelRequest'

    id = sa.Column(Identifier, primary_key=True)
    storeCode = sa.Column(sa.String)  # 店舗コード
    mmkNo = sa.Column(sa.String)  # 発券ファミポート番号
    ticketingDate = sa.Column(sa.String)  # 利用日時
    sequenceNo = sa.Column(sa.String)  # 処理通番
    barCodeNo = sa.Column(sa.String)  # 支払番号
    playGuideId = sa.Column(sa.String)  # クライアントID
    orderId = sa.Column(sa.String)  # 注文ID
    cancelCode = sa.Column(sa.String)  # 取消理由

    _requestType = FamiPortRequestType.PaymentTicketingCancel
    _encryptedFields = []


class FamiPortInformationRequest(Base, WithTimestamp, FamiPortRequest):
    """予約済み案内
    """
    __tablename__ = 'FamiPortInformationRequest'

    id = sa.Column(Identifier, primary_key=True)
    infoKubun = sa.Column(sa.String)  # 案内種別
    storeCode = sa.Column(sa.String)  # 店舗コード
    kogyoCode = sa.Column(sa.String)  # 興行コード
    kogyoSubCode = sa.Column(sa.String)  # 興行サブコード
    koenCode = sa.Column(sa.String)  # 公演コード
    uketsukeCode = sa.Column(sa.String)  # 受付コード
    playGuideId = sa.Column(sa.String)  # クライアントID
    authCode = sa.Column(sa.String)  # 認証コード
    reserveNumber = sa.Column(sa.String)  # 予約照会番号

    _requestType = FamiPortRequestType.Information
    _encryptedFields = []


class FamiPortCustomerInformationRequest(Base, WithTimestamp, FamiPortRequest):
    """顧客情報取得
    """
    __tablename__ = 'FamiPortCustomerInformationRequest'

    id = sa.Column(Identifier, primary_key=True)
    storeCode = sa.Column(sa.String)  # 店舗コード
    mmkNo = sa.Column(sa.String)  # 発券Famiポート番号
    ticketingDate = sa.Column(sa.String)  # 利用日時
    sequenceNo = sa.Column(sa.String)  # 処理通番
    barCodeNo = sa.Column(sa.String)  # バーコード情報
    playGuideId = sa.Column(sa.String)  # クライアントID
    orderId = sa.Column(sa.String)  # 注文ID
    totalAmount = sa.Column(sa.String)  # 入金金額

    _requestType = FamiPortRequestType.CustomerInformation
    _encryptedFields = []


class FamiPortResponse(object):

    def __str__(self):
        value_list = []
        for attribute_name in self.__slots__:
            attribute = getattr(self, attribute_name)
            if attribute:
                if not isinstance(attribute, (str, unicode)):  # noqa
                    value = attribute.value
                else:
                    value = attribute
            else:
                value = None
            value_list.append((attribute_name, value))
        return '\n'.join([str(_value) for _value in value_list])

    @property
    def response_type(self):
        return self._responseType

    @property
    def encrypt_fields(self):
        return self._encryptFields

    @property
    def encrypt_key(self):
        return self._encrypt_key


class FamiPortTicket(Base, WithTimestamp):
    """チケット情報

    FamiPortPaymentTicketingResponseに含まれる情報です。
    このクラスに対応する単体のレスポンスはありません。
    """
    __tablename__ = 'FamiPortTicket'

    id = sa.Column(Identifier, primary_key=True)
    barCodeNo = sa.Column(sa.String, nullable=False, default='')  # チケットバーコード番号
    ticketClass = sa.Column(sa.String, nullable=False, default='')  # チケット区分
    templateCode = sa.Column(sa.String, nullable=False, default='')  # テンプレートコード
    ticketData = sa.Column(sa.String, nullable=False, default='')  # 券面データ


class FamiPortReservationInquiryResponse(Base, WithTimestamp, FamiPortResponse):
    """予約済み予約照会
    """
    __tablename__ = 'FamiPortReservationInquiryResponse'

    id = sa.Column(Identifier, primary_key=True)
    resultCode = sa.Column(sa.String, nullable=False, default='')  # 処理結果
    replyClass = sa.Column(sa.String, nullable=False, default='')  # 応答結果区分
    replyCode = sa.Column(sa.String, nullable=False, default='')  # 応答結果
    playGuideId = sa.Column(sa.Unicode, nullable=False, default=u'')  # クライアントID
    barCodeNo = sa.Column(sa.String, nullable=False, default='')  # 支払番号
    totalAmount = sa.Column(sa.String, nullable=False, default='')  # 合計金額
    ticketPayment = sa.Column(sa.String, nullable=False, default='')  # チケット料金
    systemFee = sa.Column(sa.String, nullable=False, default='')  # システム利用料
    ticketingFee = sa.Column(sa.String, nullable=False, default='')  # 店頭発券手数料
    ticketCountTotal = sa.Column(sa.String, nullable=False, default='')  # チケット枚数
    ticketCount = sa.Column(sa.String, nullable=False, default='')  # 本券購入枚数
    kogyoName = sa.Column(sa.Unicode, nullable=False, default=u'')  # 興行名
    koenDate = sa.Column(sa.String, nullable=False, default='')  # 公園日時
    name = sa.Column(sa.Unicode, nullable=False, default=u'')  # お客様氏名
    nameInput = sa.Column(sa.String, nullable=False, default='')  # 氏名要求フラグ
    phoneInput = sa.Column(sa.String, nullable=False, default='')  # 電話番号要求フラグ

    _responseType = FamiPortResponseType.ReservationInquiry
    _encryptFields = ['name']

    @property
    def _encrypt_key(self):
        return self.barCodeNo


class FamiPortPaymentTicketingResponse(Base, WithTimestamp, FamiPortResponse):
    """予約済み入金発券
    """
    __tablename__ = 'FamiPortPaymentTicketingResponse'

    id = sa.Column(Identifier, primary_key=True)
    resultCode = sa.Column(sa.String, nullable=False, default='')  # 処理結果
    storeCode = sa.Column(sa.String, nullable=False, default='')  # 店舗コード
    sequenceNo = sa.Column(sa.String, nullable=False, default='')  # 処理通番
    barCodeNo = sa.Column(sa.String, nullable=False, default='')  # 支払番号
    orderId = sa.Column(sa.String, nullable=False, default='')  # 注文ID
    replyClass = sa.Column(sa.String, nullable=False, default='')  # 応答結果区分
    replyCode = sa.Column(sa.String, nullable=False, default='')  # 応答結果
    playGuideId = sa.Column(sa.Unicode, nullable=False, default=u'')  # クライアントID
    playGuideName = sa.Column(sa.Unicode, nullable=False, default=u'')  # クライアント漢字名称
    orderTicketNo = sa.Column(sa.String, nullable=False, default='')  # 払込票番号
    exchangeTicketNo = sa.Column(sa.String, nullable=False, default='')  # 引換票番号
    ticketingStart = sa.Column(sa.String, nullable=False, default='')  # 発券開始日時
    ticketingEnd = sa.Column(sa.String, nullable=False, default='')  # 発券期限日時
    totalAmount = sa.Column(sa.Unicode, nullable=False, default=u'')  # 合計金額
    ticketPayment = sa.Column(sa.Unicode, nullable=False, default=u'')  # チケット料金
    systemFee = sa.Column(sa.Unicode, nullable=False, default=u'')  # システム利用料
    ticketingFee = sa.Column(sa.Unicode, nullable=False, default=u'')  # 店頭発券手数料
    ticketCountTotal = sa.Column(sa.Unicode, nullable=False, default=u'')  # チケット枚数
    ticketCount = sa.Column(sa.Unicode, nullable=False, default=u'')  # 本券購入枚数
    kogyoName = sa.Column(sa.Unicode, nullable=False, default=u'')  # 興行名
    koenDate = sa.Column(sa.String, nullable=False, default='')  # 公演日時
    barCodeNo = sa.Column(sa.String(13), nullable=False, default='')  # チケットバーコード番号
    ticketClass = sa.Column(sa.String(1), nullable=False, default='')  # チケット区分
    templateCode = sa.Column(sa.String(10), nullable=False, default='')  # テンプレートコード
    ticketData = sa.Column(sa.Unicode(4000), nullable=False, default=u'')  # 券面データ
    ticket = sa.Column(sa.String, nullable=False, default='')  # チケット情報 (FamiPortTicketのリスト)

    _responseType = FamiPortResponseType.PaymentTicketing
    _encryptFields = []
    _encrypt_key = None


class FamiPortPaymentTicketingCompletionResponse(Base, WithTimestamp, FamiPortResponse):
    """予約済み入金発券完了
    """
    __tablename__ = 'FamiPortPaymentTicketingCompletionResponse'

    id = sa.Column(Identifier, primary_key=True)
    resultCode = sa.Column(sa.String, nullable=False, default='')  # 処理結果
    storeCode = sa.Column(sa.String, nullable=False, default='')  # 店舗コード
    sequenceNo = sa.Column(sa.String, nullable=False, default='')  # 処理通番
    barCodeNo = sa.Column(sa.String, nullable=False, default='')  # 支払番号
    orderId = sa.Column(sa.String, nullable=False, default='')  # 注文ID
    replyCode = sa.Column(sa.String, nullable=False, default='')  # 応答結果

    _responseType = FamiPortResponseType.PaymentTicketingCompletion
    _encryptFields = []
    _encrypt_key = None


class FamiPortPaymentTicketingCancelResponse(Base, WithTimestamp, FamiPortResponse):
    """予約済み入金発券取消
    """
    __tablename__ = 'FamiPortPaymentTicketingCancelResponse'

    id = sa.Column(Identifier, primary_key=True)
    resultCode = sa.Column(sa.String, nullable=False, default='')  # 処理結果
    storeCode = sa.Column(sa.String, nullable=False, default='')  # 店舗コード
    sequenceNo = sa.Column(sa.String, nullable=False, default='')  # 処理通番
    barCodeNo = sa.Column(sa.String, nullable=False, default='')  # 支払番号
    orderId = sa.Column(sa.String, nullable=False, default='')  # 注文ID
    replyCode = sa.Column(sa.String, nullable=False, default='')  # 応答結果

    _responseType = FamiPortResponseType.PaymentTicketingCancel
    _encryptFields = []
    _encrypt_key = None


class FamiPortInformationResponse(Base, WithTimestamp, FamiPortResponse):
    """予約済み案内
    """
    __tablename__ = 'FamiPortInformationResponse'

    id = sa.Column(Identifier, primary_key=True)
    resultCode = sa.Column(sa.String, nullable=False, default='')  # 処理結果
    infoKubun = sa.Column(sa.String, nullable=False, default='')  # 案内区分
    infoMessage = sa.Column(sa.Unicode, nullable=False, default=u'')  # 案内文言

    _responseType = FamiPortResponseType.Information
    _encryptFields = []
    _encrypt_key = None


class FamiPortCustomerInformationResponse(Base, WithTimestamp, FamiPortResponse):
    """顧客情報取得
    """
    __tablename__ = 'FamiPortCustomerInformationResponse'

    id = sa.Column(Identifier, primary_key=True)
    resultCode = sa.Column(sa.String, nullable=False, default='')  # 処理結果
    replyCode = sa.Column(sa.String, nullable=False, default='')  # 応答結果
    name = sa.Column(sa.Unicode, nullable=False, default=u'')  # 氏名
    memberId = sa.Column(sa.Unicode, nullable=False, default=u'')  # 会員ID
    address1 = sa.Column(sa.Unicode, nullable=False, default=u'')  # 住所1
    address2 = sa.Column(sa.Unicode, nullable=False, default=u'')  # 住所2
    identifyNo = sa.Column(sa.Unicode, nullable=False, default=u'')  # 半券個人識別番号

    _responseType = FamiPortResponseType.CustomerInformation
    _encryptFields = ['name', 'memberId', 'address1', 'address2', 'identifyNo']
    _encrypt_key = None

    def _set_encryptKey(self, encrypt_key):
        self._encrypt_key = encrypt_key

    @property
    def encrypt_key(self):
        return self._encrypt_key
