# -*- coding: utf-8 -*-
import sqlalchemy as sa
from altair.app.ticketing.models import (
    Base,
    BaseModel,
    DBSession,
    Identifier,
    WithTimestamp,
    )
from altair.app.ticketing.orders.api import get_order_by_order_no
from .utils import (
    InformationResultCodeEnum,
    FamiPortRequestType,
    )


class FamiPortOrderNoSequence(Base, BaseModel, WithTimestamp):
    __tablename__ = 'FamiPortOrderNoSequence'

    id = sa.Column(Identifier, primary_key=True)

    @classmethod
    def get_next_value(cls, name):
        seq = cls()
        DBSession.add(seq)
        DBSession.flush()
        return seq.id


class FamiPortOrder(Base, BaseModel, WithTimestamp):
    __tablename__ = 'FamiPortOrder'

    id = sa.Column(Identifier, primary_key=True)
    order_no = sa.Column(sa.String(255), nullable=False)
    barcode_no = sa.Column(sa.String(255), nullable=False)

    name = sa.Column(sa.Unicode(42), nullable=False)  # 氏名
    # storeCode = sa.Column(sa.String)  # 店舗コード
    # ticketingDate = sa.Column(sa.String)  # 利用日時
    # reserveNumber = sa.Column(sa.String)  # 予約番号
    # authNumber = sa.Column(sa.String)  # 認証番号
    # mmkNo = sa.Column(sa.String)  # 発券ファミポート番号
    # sequenceNo = sa.Column(sa.String)  # 処理通番
    playGuideId = sa.Column(sa.String, default='', nullable=False)  # クライアントID
    barCodeNo = sa.Column(sa.String)  # 支払番号
    # customerName = sa.Column(sa.String)  # カナ氏名
    # phoneNumber = sa.Column(sa.String)  # 電話番号
    # requestClass = sa.Column(sa.String)  # 要求区分 TODO Delete the field?
    # orderId = sa.Column(sa.String)  # 注文ID
    totalAmount = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False)  # 入金金額
    ticketPayment = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False)  # チケット料金
    systemFee = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False)  # システム利用料
    ticketingFee = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False)  # 店頭発券手数料
    # cancelCode = sa.Column(sa.String)  # 取消理由
    # infoKubun = sa.Column(sa.String)  # 案内種別
    # storeCode = sa.Column(sa.String)  # 店舗コード
    # kogyoCode = sa.Column(sa.String)  # 興行コード
    # kogyoSubCode = sa.Column(sa.String)  # 興行サブコード
    # koenCode = sa.Column(sa.String)  # 公演コード
    koenDate = sa.Column(sa.DateTime, nullable=True)  # 公演日時
    kogyoName = sa.Column(sa.Unicode(40), nullable=False)  # 興行名
    # uketsukeCode = sa.Column(sa.String)  # 受付コード
    # authCode = sa.Column(sa.String)  # 認証コード
    ticketTotalCount = sa.Column(sa.Integer, nullable=False)  # 本件購入枚数
    ticketCount = sa.Column(sa.Integer, nullable=False)  # 本件購入枚数
    nameInput = sa.Column(sa.Boolean, nullable=False, default=0)  # 氏名要求フラグ
    phoneInput = sa.Column(sa.Boolean, nullable=False, default=0)  # 電話番号要求フラグ
    phoneNumber = sa.Column(sa.Unicode(12), nullable=False)  # 電話番号

    @property
    def get_totalAmount(self):
        order = get_order_by_order_no(self.order_no)
        return 0 if order.paid_at else order.total_amount


class FamiPortInformationMessage(Base, BaseModel, WithTimestamp):
    __tablename__ = 'FamiPortInformationMessage'
    __table_args__ = (sa.UniqueConstraint('result_code'),)

    id = sa.Column(Identifier, primary_key=True)
    result_code = sa.Column(sa.Enum('WithInformation', 'ServiceUnavailable'), unique=True, nullable=False)
    message = sa.Column(sa.Unicode(length=1000), nullable=True)

    @classmethod
    def create(cls, result_code, message):
        return cls(result_code=result_code, message=message)

    @classmethod
    def get_message(cls, information_result_code, default_message=None):
        if not isinstance(information_result_code, InformationResultCodeEnum):
            return None
        query = FamiPortInformationMessage.filter_by(result_code=information_result_code.name)
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


class FamiPortReservationInquiryRequest(Base, BaseModel, WithTimestamp, FamiPortRequest):
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


class FamiPortPaymentTicketingRequest(Base, BaseModel, WithTimestamp, FamiPortRequest):
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


class FamiPortPaymentTicketingCompletionRequest(Base, BaseModel, WithTimestamp, FamiPortRequest):
    """予約済み入金発券完了
    """
    __tablename__ = 'FamiPortPaymentTicketingCompletionRequest'

    id = sa.Column(Identifier, primary_key=True)
    storeCode = sa.Column(sa.String)  # 店舗コード
    mmkNo = sa.Column(sa.String)  # 発券ファミポート番号
    ticketingDate = sa.Column(sa.String)  # 利用日時
    sequenceNo = sa.Column(sa.String)  # 処理通番
    requestClass = sa.Column(sa.String)  # 要求区分 TODO Delete the field?
    barCodeNo = sa.Column(sa.String)  # 支払番号
    playGuideId = sa.Column(sa.String)  # クライアントID
    orderId = sa.Column(sa.String)  # 注文ID
    totalAmount = sa.Column(sa.String)  # 入金金額

    _requestType = FamiPortRequestType.PaymentTicketingCompletion
    _encryptedFields = []


class FamiPortPaymentTicketingCancelRequest(Base, BaseModel, WithTimestamp, FamiPortRequest):
    """予約済み入金発券取消
    """
    __tablename__ = 'FamiPortPaymentTicketingCancelRequest'

    id = sa.Column(Identifier, primary_key=True)
    storeCode = sa.Column(sa.String)  # 店舗コード
    mmkNo = sa.Column(sa.String)  # 発券ファミポート番号
    ticketingDate = sa.Column(sa.String)  # 利用日時
    sequenceNo = sa.Column(sa.String)  # 処理通番
    requestClass = sa.Column(sa.String)  # 要求区分 TODO Delete the field?
    barCodeNo = sa.Column(sa.String)  # 支払番号
    playGuideId = sa.Column(sa.String)  # クライアントID
    orderId = sa.Column(sa.String)  # 注文ID
    cancelCode = sa.Column(sa.String)  # 取消理由

    _requestType = FamiPortRequestType.PaymentTicketingCancel
    _encryptedFields = []


class FamiPortInformationRequest(Base, BaseModel, WithTimestamp, FamiPortRequest):
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


class FamiPortCustomerInformationRequest(Base, BaseModel, WithTimestamp, FamiPortRequest):
    """顧客情報取得
    """
    __tablename__ = 'FamiPortCustomerInformationRequest'

    id = sa.Column(Identifier, primary_key=True)
    storeCode = sa.Column(sa.String)  # 店舗コード
    mmkNo = sa.Column(sa.String)  # 発券Famiポート番号
    ticketingDate = sa.Column(sa.String)  # 利用日時
    sequenceNo = sa.Column(sa.String)  # 処理通番
    requestClass = sa.Column(sa.String)  # 要求区分 TODO Delete the field?
    barCodeNo = sa.Column(sa.String)  # バーコード情報
    playGuideId = sa.Column(sa.String)  # クライアントID
    orderId = sa.Column(sa.String)  # 注文ID
    totalAmount = sa.Column(sa.String)  # 入金金額

    _requestType = FamiPortRequestType.CustomerInformation
    _encryptedFields = []
