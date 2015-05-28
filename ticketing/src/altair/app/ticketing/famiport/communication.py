# encoding: utf-8
from enum import Enum, IntEnum
import sqlalchemy as sa
from sqlalchemy import orm
import sqlahelper
from altair.models import Identifier, WithTimestamp

Base = sqlahelper.get_base()

class FamiPortRequestType(IntEnum):
    ReservationInquiry         = 1 # 予約済み予約照会
    PaymentTicketing           = 2 # 予約済み入金発券
    PaymentTicketingCompletion = 3 # 予約済み入金発券完了
    PaymentTicketingCancel     = 4 # 予約済み入金発券取消
    Information                = 5 # 予約済み案内
    CustomerInformation        = 6 # 予約済み顧客情報取得

class FamiPortResponseType(IntEnum):
    ReservationInquiry         = 1 # 予約済み予約照会
    PaymentTicketing           = 2 # 予約済み入金発券
    PaymentTicketingCompletion = 3 # 予約済み入金発券完了
    PaymentTicketingCancel     = 4 # 予約済み入金発券取消
    Information                = 5 # 予約済み案内
    CustomerInformation        = 6 # 予約済み顧客情報取得

class ResultCodeEnum(Enum):
    Normal = '00' # 正常
    BusinessDivisionError = '11' # 業務区分エラー
    ServinceUnavailable = '14' # サービス時間帯エラー
    TimeoutError = '15' # タイムアウトエラー
    OtherError = '99' # その他エラー

class InformationResultCodeEnum(Enum):
    NoInformation = '00' # 案内なし(正常)
    WithInformation = '01' # 案内あり(正常)
    ServiceUnavailable = '90' # サービス不可時案内
    OtherError = '99' # その他エラー

class InfoKubunEnum(IntEnum):
    Reserved = 1 # 予済み
    DirectSales = 2 # 直販

class ReplyClassEnum(IntEnum):
    CashOnDelivery = 1 # 代引き
    Prepayment = 2 # 前払い（後日渡し）の前払い時
    Paid = 3 # 代済発券と前払い(後日渡し)の後日渡し時
    PrepaymentOnly = 4 # 前払いのみ

class ReplyCodeEnum(Enum):
    Normal = '00' # 正常応答
    SearchKeyError = '01' # 検索キーエラー
    PaymentDueError = '02' # 支払期限エラー
    AlreadyPaidError = '03' # 支払済みエラー
    PaymentAlreadyCanceledError = '04' # 支払取消済み
    TicketAlreadyIssuedError = '07' # 発券済みエラー
    TicketingDueError = '08' # 発券期限エラー
    TicketingAlreadyCanceledError = '09' # 発券取消済みエラー
    PaymentCancelError = '13' # 入金中止エラー
    TicketingBeforeStartError = '14' # 発券開始前エラー
    TicketingCancelError = '15' # 発券中止エラー
    CustomerNamePrintInformationError = '70' # 顧客名印字情報取得エラー
    OtherError = '99' # その他エラー

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

    id = sa.Column(Identifier, primary_key=True, autoincrement=True)
    storeCode = sa.Column(sa.Unicode(6))  # 店舗コード
    ticketingDate = sa.Column(sa.Unicode(14))  # 利用日時
    reserveNumber = sa.Column(sa.Unicode(13))  # 予約番号
    authNumber = sa.Column(sa.Unicode(13))  # 認証番号

    _requestType = FamiPortRequestType.ReservationInquiry
    _encryptedFields = ()


class FamiPortPaymentTicketingRequest(Base, WithTimestamp, FamiPortRequest):
    """予約済み入金発券
    """
    __tablename__ = 'FamiPortPaymentTicketingRequest'

    id = sa.Column(Identifier, primary_key=True, autoincrement=True)
    storeCode = sa.Column(sa.Unicode(6))  # 店舗コード
    mmkNo = sa.Column(sa.Unicode(1))  # 発券ファミポート番号
    ticketingDate = sa.Column(sa.Unicode(14))  # 利用日時
    sequenceNo = sa.Column(sa.Unicode(11))  # 処理通番
    playGuideId = sa.Column(sa.Unicode(24), nullable=False, default=u'')  # クライアントID
    barCodeNo = sa.Column(sa.Unicode(13))  # 支払番号
    customerName = sa.Column(sa.Unicode(255))  # カナ氏名
    phoneNumber = sa.Column(sa.Unicode(255))  # 電話番号

    _requestType = FamiPortRequestType.PaymentTicketing
    _encryptedFields = ['customerName', 'phoneNumber']


class FamiPortPaymentTicketingCompletionRequest(Base, WithTimestamp, FamiPortRequest):
    """予約済み入金発券完了
    """
    __tablename__ = 'FamiPortPaymentTicketingCompletionRequest'

    id = sa.Column(Identifier, primary_key=True, autoincrement=True)
    storeCode = sa.Column(sa.Unicode(6))  # 店舗コード
    mmkNo = sa.Column(sa.Unicode(1))  # 発券ファミポート番号
    ticketingDate = sa.Column(sa.Unicode(14))  # 利用日時
    sequenceNo = sa.Column(sa.Unicode(11))  # 処理通番
    barCodeNo = sa.Column(sa.Unicode(13))  # 支払番号
    playGuideId = sa.Column(sa.Unicode(24))  # クライアントID
    orderId = sa.Column(sa.Unicode(12))  # 注文ID
    totalAmount = sa.Column(sa.Unicode(8))  # 入金金額

    _requestType = FamiPortRequestType.PaymentTicketingCompletion
    _encryptedFields = []


class FamiPortPaymentTicketingCancelRequest(Base, WithTimestamp, FamiPortRequest):
    """予約済み入金発券取消
    """
    __tablename__ = 'FamiPortPaymentTicketingCancelRequest'

    id = sa.Column(Identifier, primary_key=True, autoincrement=True)
    storeCode = sa.Column(sa.Unicode(6))  # 店舗コード
    mmkNo = sa.Column(sa.Unicode(1))  # 発券ファミポート番号
    ticketingDate = sa.Column(sa.Unicode(14))  # 利用日時
    sequenceNo = sa.Column(sa.Unicode(11))  # 処理通番
    barCodeNo = sa.Column(sa.Unicode(13))  # 支払番号
    playGuideId = sa.Column(sa.Unicode(24))  # クライアントID
    orderId = sa.Column(sa.Unicode(12))  # 注文ID
    cancelCode = sa.Column(sa.Unicode(2))  # 取消理由

    _requestType = FamiPortRequestType.PaymentTicketingCancel
    _encryptedFields = []


class FamiPortInformationRequest(Base, WithTimestamp, FamiPortRequest):
    """予約済み案内
    """
    __tablename__ = 'FamiPortInformationRequest'

    id = sa.Column(Identifier, primary_key=True, autoincrement=True)
    infoKubun = sa.Column(sa.Unicode(1))  # 案内種別
    storeCode = sa.Column(sa.Unicode(6))  # 店舗コード
    kogyoCode = sa.Column(sa.Unicode(6))  # 興行コード
    kogyoSubCode = sa.Column(sa.Unicode(4))  # 興行サブコード
    koenCode = sa.Column(sa.Unicode(3))  # 公演コード
    uketsukeCode = sa.Column(sa.Unicode(3))  # 受付コード
    playGuideId = sa.Column(sa.Unicode(24))  # クライアントID
    authCode = sa.Column(sa.Unicode(100))  # 認証コード
    reserveNumber = sa.Column(sa.Unicode(13))  # 予約照会番号

    _requestType = FamiPortRequestType.Information
    _encryptedFields = []


class FamiPortCustomerInformationRequest(Base, WithTimestamp, FamiPortRequest):
    """顧客情報取得
    """
    __tablename__ = 'FamiPortCustomerInformationRequest'

    id = sa.Column(Identifier, primary_key=True, autoincrement=True)
    storeCode = sa.Column(sa.Unicode(6))  # 店舗コード
    mmkNo = sa.Column(sa.Unicode(1))  # 発券Famiポート番号
    ticketingDate = sa.Column(sa.Unicode(14))  # 利用日時
    sequenceNo = sa.Column(sa.Unicode(11))  # 処理通番
    barCodeNo = sa.Column(sa.Unicode(13))  # バーコード情報
    playGuideId = sa.Column(sa.Unicode(24))  # クライアントID
    orderId = sa.Column(sa.Unicode(12))  # 注文ID
    totalAmount = sa.Column(sa.Unicode(8))  # 入金金額

    _requestType = FamiPortRequestType.CustomerInformation
    _encryptedFields = []


class FamiPortResponse(object):
    def __str__(self):
        value_list = []
        for attribute_name in self._serialized_attrs:
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
    def encrypted_fields(self):
        return self._encryptedFields

    @property
    def encrypt_key(self):
        return self._encrypt_key

class FamiPortTicketResponse(Base, WithTimestamp, FamiPortResponse):
    """チケット情報

    FamiPortPaymentTicketingResponseに含まれる情報です。
    このクラスに対応する単体のレスポンスはありません。
    """
    __tablename__ = 'FamiPortTicketResponse'
    _serialized_attrs = (
        'barCodeNo',
        'ticketClass',
        'templateCode',
        'ticketData',
        )
    _serialized_collection_attrs = ()
    _encryptedFields = []

    id = sa.Column(Identifier, primary_key=True, autoincrement=True)
    famiport_payment_ticketing_response_id = sa.Column(Identifier, sa.ForeignKey('FamiPortPaymentTicketingResponse.id'))
    barCodeNo = sa.Column(sa.Unicode(13), nullable=False, default=u'')  # チケットバーコード番号
    ticketClass = sa.Column(sa.Unicode(1), nullable=False, default=u'')  # チケット区分
    templateCode = sa.Column(sa.Unicode(10), nullable=False, default=u'')  # テンプレートコード
    ticketData = sa.Column(sa.Unicode(4000), nullable=False, default=u'')  # 券面データ

    famiport_payment_ticketing_response = orm.relationship('FamiPortPaymentTicketingResponse', backref='tickets')

class FamiPortReservationInquiryResponse(Base, WithTimestamp, FamiPortResponse):
    """予約済み予約照会
    """
    __tablename__ = 'FamiPortReservationInquiryResponse'
    _serialized_attrs = (
        'resultCode',
        'replyClass',
        'replyCode',
        'barCodeNo',
        'totalAmount',
        'ticketPayment',
        'systemFee',
        'ticketingFee',
        'ticketCountTotal',
        'ticketCount',
        'kogyoName',
        'koenDate',
        'name',
        'nameInput',
        'phoneInput'
        )
    _serialized_collection_attrs = ()
    _responseType = FamiPortResponseType.ReservationInquiry
    _encryptedFields = ['name']

    id = sa.Column(Identifier, primary_key=True, autoincrement=True)
    resultCode = sa.Column(sa.Unicode(2), nullable=False, default=u'')  # 処理結果
    replyClass = sa.Column(sa.Unicode(1), nullable=False, default=u'')  # 応答結果区分
    replyCode = sa.Column(sa.Unicode(2), nullable=False, default=u'')  # 応答結果
    playGuideId = sa.Column(sa.Unicode(24), nullable=False, default=u'')  # クライアントID
    barCodeNo = sa.Column(sa.Unicode(13), nullable=False, default=u'')  # 支払番号
    totalAmount = sa.Column(sa.Unicode(8), nullable=False, default=u'')  # 合計金額
    ticketPayment = sa.Column(sa.Unicode(8), nullable=False, default=u'')  # チケット料金
    systemFee = sa.Column(sa.Unicode(8), nullable=False, default=u'')  # システム利用料
    ticketingFee = sa.Column(sa.Unicode(8), nullable=False, default=u'')  # 店頭発券手数料
    ticketCountTotal = sa.Column(sa.Unicode(2), nullable=False, default=u'')  # チケット枚数
    ticketCount = sa.Column(sa.Unicode(2), nullable=False, default=u'')  # 本券購入枚数
    kogyoName = sa.Column(sa.Unicode(40), nullable=False, default=u'')  # 興行名
    koenDate = sa.Column(sa.Unicode(12), nullable=False, default=u'')  # 公園日時
    name = sa.Column(sa.Unicode(42), nullable=False, default=u'')  # お客様氏名
    nameInput = sa.Column(sa.Unicode(1), nullable=False, default=u'')  # 氏名要求フラグ
    phoneInput = sa.Column(sa.Unicode(1), nullable=False, default=u'')  # 電話番号要求フラグ

    @property
    def _encrypt_key(self):
        return self.barCodeNo


class FamiPortPaymentTicketingResponse(Base, WithTimestamp, FamiPortResponse):
    """予約済み入金発券
    """
    __tablename__ = 'FamiPortPaymentTicketingResponse'
    _serialized_attrs = (
        'resultCode',
        'storeCode',
        'sequenceNo',
        'barCodeNo',
        'orderId',
        'replyClass',
        'replyCode',
        'playGuideId',
        'playGuideName',
        'orderTicketNo',
        'exchangeTicketNo',
        'ticketingStart',
        'ticketingEnd',
        'totalAmount',
        'ticketPayment',
        'systemFee',
        'ticketingFee',
        'ticketCountTotal',
        'ticketCount',
        'kogyoName',
        'koenDate',
        )
    _serialized_collection_attrs = (
        ('tickets', 'ticket'),
        )
    _responseType = FamiPortResponseType.PaymentTicketing
    _encryptedFields = []
    _encrypt_key = None

    id = sa.Column(Identifier, primary_key=True, autoincrement=True)
    resultCode = sa.Column(sa.Unicode(2), nullable=False, default=u'')  # 処理結果
    storeCode = sa.Column(sa.Unicode(6), nullable=False, default=u'')  # 店舗コード
    sequenceNo = sa.Column(sa.Unicode(11), nullable=False, default=u'')  # 処理通番
    barCodeNo = sa.Column(sa.Unicode(13), nullable=False, default=u'')  # 支払番号
    orderId = sa.Column(sa.Unicode(12), nullable=False, default=u'')  # 注文ID
    replyClass = sa.Column(sa.Unicode(1), nullable=False, default=u'')  # 応答結果区分
    replyCode = sa.Column(sa.Unicode(2), nullable=False, default=u'')  # 応答結果
    playGuideId = sa.Column(sa.Unicode(24), nullable=False, default=u'')  # クライアントID
    playGuideName = sa.Column(sa.Unicode(50), nullable=False, default=u'')  # クライアント漢字名称
    orderTicketNo = sa.Column(sa.Unicode(13), nullable=False, default=u'')  # 払込票番号
    exchangeTicketNo = sa.Column(sa.Unicode(13), nullable=False, default=u'')  # 引換票番号
    ticketingStart = sa.Column(sa.Unicode(12), nullable=False, default=u'')  # 発券開始日時
    ticketingEnd = sa.Column(sa.Unicode(12), nullable=False, default=u'')  # 発券期限日時
    totalAmount = sa.Column(sa.Unicode(8), nullable=False, default=u'')  # 合計金額
    ticketPayment = sa.Column(sa.Unicode(8), nullable=False, default=u'')  # チケット料金
    systemFee = sa.Column(sa.Unicode(8), nullable=False, default=u'')  # システム利用料
    ticketingFee = sa.Column(sa.Unicode(8), nullable=False, default=u'')  # 店頭発券手数料
    ticketCountTotal = sa.Column(sa.Unicode(2), nullable=False, default=u'')  # チケット枚数
    ticketCount = sa.Column(sa.Unicode(2), nullable=False, default=u'')  # 本券購入枚数
    kogyoName = sa.Column(sa.Unicode(40), nullable=False, default=u'')  # 興行名
    koenDate = sa.Column(sa.Unicode(12), nullable=False, default=u'')  # 公演日時


class FamiPortPaymentTicketingCompletionResponse(Base, WithTimestamp, FamiPortResponse):
    """予約済み入金発券完了
    """
    __tablename__ = 'FamiPortPaymentTicketingCompletionResponse'
    _serialized_attrs = (
        'resultCode',
        'storeCode',
        'sequenceNo',
        'barCodeNo',
        'orderId',
        'replyCode',
        )
    _serialized_collection_attrs = ()

    id = sa.Column(Identifier, primary_key=True, autoincrement=True)
    resultCode = sa.Column(sa.Unicode(2), nullable=False, default=u'')  # 処理結果
    storeCode = sa.Column(sa.Unicode(6), nullable=False, default=u'')  # 店舗コード
    sequenceNo = sa.Column(sa.Unicode(11), nullable=False, default=u'')  # 処理通番
    barCodeNo = sa.Column(sa.Unicode(13), nullable=False, default=u'')  # 支払番号
    orderId = sa.Column(sa.Unicode(12), nullable=False, default=u'')  # 注文ID
    replyCode = sa.Column(sa.Unicode(2), nullable=False, default=u'')  # 応答結果

    _responseType = FamiPortResponseType.PaymentTicketingCompletion
    _encryptedFields = []
    _encrypt_key = None


class FamiPortPaymentTicketingCancelResponse(Base, WithTimestamp, FamiPortResponse):
    """予約済み入金発券取消
    """
    __tablename__ = 'FamiPortPaymentTicketingCancelResponse'
    _serialized_attrs = (
        'resultCode',
        'storeCode',
        'sequenceNo',
        'barCodeNo',
        'orderId',
        'replyCode',
        )
    _serialized_collection_attrs = ()
    _responseType = FamiPortResponseType.PaymentTicketingCancel
    _encryptedFields = []
    _encrypt_key = None

    id = sa.Column(Identifier, primary_key=True, autoincrement=True)
    resultCode = sa.Column(sa.Unicode(2), nullable=False, default=u'')  # 処理結果
    storeCode = sa.Column(sa.Unicode(6), nullable=False, default=u'')  # 店舗コード
    sequenceNo = sa.Column(sa.Unicode(11), nullable=False, default=u'')  # 処理通番
    barCodeNo = sa.Column(sa.Unicode(13), nullable=False, default=u'')  # 支払番号
    orderId = sa.Column(sa.Unicode(12), nullable=False, default=u'')  # 注文ID
    replyCode = sa.Column(sa.Unicode(2), nullable=False, default=u'')  # 応答結果

class FamiPortInformationResponse(Base, WithTimestamp, FamiPortResponse):
    """予約済み案内
    """
    __tablename__ = 'FamiPortInformationResponse'
    _serialized_attrs = (
        'resultCode',
        'infoKubun',
        'infoMessage'
        )
    _serialized_collection_attrs = ()
    _responseType = FamiPortResponseType.Information
    _encryptedFields = []
    _encrypt_key = None

    id = sa.Column(Identifier, primary_key=True, autoincrement=True)
    resultCode = sa.Column(sa.Unicode(2), nullable=False, default=u'')  # 処理結果
    infoKubun = sa.Column(sa.Unicode(1), nullable=False, default=u'')  # 案内区分
    infoMessage = sa.Column(sa.Unicode(500), nullable=False, default=u'')  # 案内文言


class FamiPortCustomerInformationResponse(Base, WithTimestamp, FamiPortResponse):
    """顧客情報取得
    """
    __tablename__ = 'FamiPortCustomerInformationResponse'
    _serialized_attrs = (
        'resultCode',
        'replyCode',
        'name',
        'memberId',
        'address1',
        'address2',
        'identifyNo'
        )
    _serialized_collection_attrs = ()
    _responseType = FamiPortResponseType.CustomerInformation
    _encryptedFields = ['name', 'memberId', 'address1', 'address2', 'identifyNo']
    _encrypt_key = None

    id = sa.Column(Identifier, primary_key=True, autoincrement=True)
    resultCode = sa.Column(sa.Unicode(2), nullable=False, default=u'')  # 処理結果
    replyCode = sa.Column(sa.Unicode(2), nullable=False, default=u'')  # 応答結果
    name = sa.Column(sa.Unicode(42), nullable=False, default=u'')  # 氏名
    memberId = sa.Column(sa.Unicode(100), nullable=False, default=u'')  # 会員ID
    address1 = sa.Column(sa.Unicode(200), nullable=False, default=u'')  # 住所1
    address2 = sa.Column(sa.Unicode(200), nullable=False, default=u'')  # 住所2
    identifyNo = sa.Column(sa.Unicode(16), nullable=False, default=u'')  # 半券個人識別番号

    def _set_encryptKey(self, encrypt_key):
        self._encrypt_key = encrypt_key

    @property
    def encrypt_key(self):
        return self._encrypt_key

