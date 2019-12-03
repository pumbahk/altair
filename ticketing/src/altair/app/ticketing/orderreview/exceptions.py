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
