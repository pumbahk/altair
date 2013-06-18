# -*- coding:utf-8 -*-

"""
"""

from zope.interface import Interface, Attribute

class IGetCart(Interface):
    def __call__(request):
        """ get IPaymentCart impl from request """


class IPaymentCart(Interface):

    performance = Attribute(u"")
    sales_segment = Attribute(u"")
    payment_delivery_pair = Attribute(u"")
    order_no = Attribute(u"")
    total_amount = Attribute(u"")
    
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
        pass

class IPaymentPlugin(Interface, IPaymentPreparer):
    """ 決済プラグイン"""
    def prepare(request, cart):
        """ 前処理 """

    def finish(request, cart):
        """ 確定処理 """

    def finished(request, order):
        """ 確定済みか判定する"""

    def cancel(request, order):
        pass

class IPaymentDeliveryPlugin(Interface):
    """ 決済配送を一度に行うプラグイン"""
    def prepare(request, cart):
        """ 前処理 """

    def finish(request, cart):
        """ 確定処理 """

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
