# -*- coding: utf-8 -*-

from enum import IntEnum
from cryptography.fernet import Fernet

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
        return self.fernet.decrypt(encrypted_data)