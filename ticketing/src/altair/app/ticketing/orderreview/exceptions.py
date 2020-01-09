# -*- coding:utf-8 -*-


class InvalidForm(Exception):
    def __init__(self, form, errors=[]):
        self.form = form
        self.errors = errors


class OAuthRequiredSettingError(Exception):
    pass


class QRTicketUnpaidException(Exception):
    """ 未入金の状態でSkidataQRにアクセスする場合に発生 """
    pass


class QRTicketOutOfIssuingStartException(Exception):
    """ 発券開始日時より前にSkidataQRにアクセスする場合に発生 """
    pass


class QRTicketCanceledException(Exception):
    """ 予約/購入がキャンセルされた状態でSkidataQRにアクセスする場合に発生 """
    pass


class QRTicketRefundedException(Exception):
    """ 予約/購入が払戻された状態でSkidataQRにアクセスする場合に発生 """
    pass
