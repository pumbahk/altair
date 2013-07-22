# -*- coding:utf-8 -*-

""" API呼び出しフック
"""

import functools
from zope.interface import Interface, Attribute

def notify_event(request, factory, order_no, result):
    return factory(order_no, result).notify(request)



class IMulticheckoutEvent(Interface):
    """ イベントインターフェイス """

    api = Attribute(u"イベント発生元API")
    order_no = Attribute(u"注文番号")
    result = Attribute(u"API Result")

    def notify(request):
        """ shortcut to notify this event"""


class MulticheckoutEvent(object):
    api = u""
    def __init__(self, order_no, result):
        self.order_no = order_no
        self.result = result

    @classmethod
    def notify(cls, request, order_no, result):
        event = cls(order_no, result)
        return request.registry.notify(event)


class Secure3DEnrolEvent(MulticheckoutEvent):
    """ 3Dセキュア認証開始イベント """

    api = u"secure3d_enrol"


class Secure3DAuthEvent(MulticheckoutEvent):
    """ 3Dセキュア認証実行イベント """

    api = u"secure3d_auth"


class CheckoutAuthSecure3DEvent(MulticheckoutEvent):
    """ 3Dセキュア認証オーソリ依頼イベント """

    api = u"checkout_auth_secure3d"


class CheckoutSalesSecure3DEvent(MulticheckoutEvent):
    """ 3Dセキュア認証売上確定イベント """

    api = u"checkout_sales_secure3d"


class CheckoutAuthCancelEvent(MulticheckoutEvent):
    """ オーソリキャンセルイベント """
    
    api = u"checkout_auth_cancel"


class CheckoutSalesPartCancelEvent(MulticheckoutEvent):
    """ 売上一部キャンセルイベント """

    api = u"checkout_sales_part_cancel"


class CheckoutSalesCancelEvent(MulticheckoutEvent):
    """ 売上キャンセルイベント"""

    api = u"checkout_sales_cancel"


class CheckoutInquiryEvent(MulticheckoutEvent):
    """ 取引照会イベント """

    api = u"checkout_inquiry"


class CheckoutAuthSecureCodeEvent(MulticheckoutEvent):
    """セキュアコードオーソリ依頼イベント"""

    api = u"checkout_auth_secure_code"


class CheckoutSalesSecureCodeEvent(MulticheckoutEvent):
    """ セキュアコード売上確定イベント """

    api = u"checkout_sales_secure_code"
