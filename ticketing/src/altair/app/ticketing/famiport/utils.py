# -*- coding: utf-8 -*-

from enum import Enum, IntEnum
from cryptography.fernet import Fernet
from xml.etree import ElementTree
from xml.dom import minidom

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
    TimeoutError = '15' # タイムアウトエラー
    OtherError = '99' # その他エラー

class InformationResultCodeEnum(Enum):
    NoInformation = '00' # 案内なし(正常)
    WithInformation = '01' # 案内あり(正常)
    ServinceUnavailable = '90' # サービス不可時案内
    OtherError = '99' # その他エラー

class CustomerInformationResultCodeEnum(Enum):
    Normal = '00' # 正常応答
    BusinessDivisionError = '11' # 業務区分エラー
    ServinceUnavailable = '14' # サービス時間帯エラー
    TimeoutError = '15' # タイムアウトエラー
    OtherError = '99' # その他エラー

class ReplyClassEnum(Enum):
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

class FamiPortCrypt:
    def __init__(self, key):
        self.fernet = Fernet(key)

    def encrypt(self, plain_data):
        """
        Encrypt plain_data with the given key in init
        :param plain_data:
        :return: encrypted data
        """

        return self.fernet.encrypt(plain_data)

    def decrypt(self, encrypted_data):
        """
        Decrypt encrypted_data with the given key in init
        :param encrypted data:
        :return: decrypted data
        """
        # TODO 復号化する項目をBase64で文字列からバイト配列に変換
        return self.fernet.decrypt(encrypted_data)

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")
