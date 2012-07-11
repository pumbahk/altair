# -*- coding:utf-8 -*-

""" TBA
"""


from zope.interface import Interface, Attribute

class IPaymentMethodManager(Interface):
    def get_url(payment_method_id):
        """ 決済フォームURL
        """

    def add_url(payment_method_id, url):
        """ 決済フォームURL登録
        """


class ICartDelivery(Interface):
    """ 確認画面の配送ビューレットのコンテキスト"""
    order = Attribute(u"注文内容")

class IOrderDelivery(Interface):
    """ 完了画面の配送ビューレットのコンテキスト"""
    order = Attribute(u"注文内容")

class ICartPayment(Interface):
    """ 確認画面の決済ビューレットのコンテキスト"""
    cart = Attribute(u"カート")

class IOrderPayment(Interface):
    """ 完了画面の決済ビューレットのコンテキスト"""
    cart = Attribute(u"カート")

class IDeliveryPlugin(Interface):
    """ 配送処理プラグイン """
    def prepare(request, cart):
        """ 前処理 """

    def finish(request, cart):
        """ 確定処理 """


class IPaymentPlugin(Interface):
    """ 決済プラグイン"""

    def prepare(request, cart):
        """ 前処理 """

    def finish(request, cart):
        """ 確定処理 """

class IPaymentDeliveryPlugin(Interface):
    """ 決済配送を一度に行うプラグイン"""
    def prepare(request, cart):
        """ 前処理 """

    def finish(request, cart):
        """ 確定処理 """

class IMobileRequest(Interface):
    """ mobile request interface"""
