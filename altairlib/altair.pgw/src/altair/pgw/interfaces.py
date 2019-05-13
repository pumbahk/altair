# -*- coding:utf-8 -*-
from zope.interface import Interface, Attribute


class IPgwAPICommunicator(Interface):
    """
    PGW APIと通信を行うクライアントクラスです。
    以下のAPIへのリクエストを行います。
    /Payment/V1/Authorize
    /Payment/V1/Capture
    /Payment/V1/AuthorizeAndCapture
    /Payment/V1/Find
    /Payment/V1/CancelOrRefund
    /Payment/V1/Modify
    /3DSecureEnrollment/V1/Check
    """
    def request_authorize(self):
        pass

    def request_capture(self):
        pass

    def request_authorize_and_capture(self):
        pass

    def request_find(self):
        pass

    def request_cancel_or_refund(self):
        pass

    def request_modify(self):
        pass

    def request_3d_secure_enrollment_check(self):
        pass


class IPgwAPICommunicatorFactory(Interface):
    """
    PGW APIクライアントを呼び出すためのFactoryクラスです。 　
    """
    def __call__(self):
        pass
