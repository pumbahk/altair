# -*- coding:utf-8 -*-

"""
"""

from zope.interface import Interface, Attribute
from altair.app.ticketing.core.interfaces import (
    IOrderLike,
    IOrderedProductLike,
    IOrderedProductItemLike,
    IShippingAddress
    )

class IGetCart(Interface):
    def __call__(request):
        """ get IPaymentCart impl from request """

class IPaymentCart(IOrderLike):
    performance           = Attribute(u"")
    has_different_amount  = Attribute(u"")
    different_amount      = Attribute(u"")
    name                  = Attribute(u"")
    order                 = Attribute(u"")

    def finish():
        """ finish cart lifecycle"""

class IPaymentPreparer(Interface):
    def prepare(request, cart):
        """ 決済処理の前処理を行う
        """

class IPaymentPreparerFactory(Interface):
    def __call__(request, payment_delivery_pair):
        """ 決済・引取方法に対応する前処理を取得する
        """

class IDeliveryPlugin(Interface):
    """ 配送処理プラグイン """
    def prepare(request, cart):
        """ 前処理 """

    def finish(request, cart):
        """ 確定処理 """

    def finished(request, order):
        """ 確定済みか判定する"""

    def cancel(request, order):
        """ キャンセル """

    def refresh(request, order):
        """ 内容変更 """

class IPaymentPlugin(Interface, IPaymentPreparer):
    """ 決済プラグイン"""
    def prepare(request, cart):
        """ 前処理 """

    def finish(request, cart):
        """ 確定処理 """

    def sales(request, cart):
        """ 売上確定処理 """

    def finished(request, order):
        """ *売上*確定済みか判定する (メソッド名がミスリードなのは歴史的経緯) """

    def cancel(request, order):
        """ キャンセル """

    def refresh(request, order):
        """ 注文金額変更 """

class IPaymentDeliveryPlugin(Interface):
    """ 決済配送を一度に行うプラグイン"""
    def prepare(request, cart):
        """ 前処理 """

    def finish(request, cart):
        """ 確定処理 """

    def refresh(request, order):
        """ 内容変更 """

class IOrderPayment(Interface):
    """ 完了画面の決済ビューレットのコンテキスト"""
    order = Attribute(u"注文内容")

class IOrderDelivery(Interface):
    """ 完了画面の配送ビューレットのコンテキスト"""
    order = Attribute(u"注文内容")


class IDeliveryErrorEvent(Interface):
    exception = Attribute(u"error")
    request = Attribute(u"request")
    order = Attribute(u"order caused error")

class IPayment(Interface):
    def call_prepare(self):
        pass

    def call_delegator(self):
        pass

    def call_validate(self):
        pass

    def call_payment(self):
        pass

    def call_delivery(self, order):
        pass
