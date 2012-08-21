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
    cart = Attribute(u"カート")

class IOrderDelivery(Interface):
    """ 完了画面の配送ビューレットのコンテキスト"""
    order = Attribute(u"注文内容")

class ICompleteMailDelivery(Interface):
    """ 完了メールの配送ビューレットのコンテキスト"""
    order = Attribute(u"注文内容")

class ICartPayment(Interface):
    """ 確認画面の決済ビューレットのコンテキスト"""
    cart = Attribute(u"カート")

class IOrderPayment(Interface):
    """ 完了画面の決済ビューレットのコンテキスト"""
    order = Attribute(u"注文内容")

class ICompleteMailPayment(Interface):
    """ 完了メールの配送ビューレットのコンテキスト"""
    order = Attribute(u"注文内容")

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

class IStocker(Interface):
    def take_stock(performance_id, product_requires):
        """ 在庫取得
        :param product_requires: list of tuple (product_id, quantity)
        :return: list of tuple (StockStatus, quantity)
        """

class IReserving(Interface):
    def reserve_seats(stock_id, quantity):
        """ お任せ席指定 
        :param stock_id: 席の在庫単位
        :param quantity: 数量
        :return: list of seat
        """

class ICartFactory(Interface):
    def create_cart():
        """
        カート作成
        """

class ICompleteMail(Interface):
    """完了メールを送る
    """
    request = Attribute("request")

    def validate():
        """ validate, all delivery method pair can choice mail template for oneself.
        """
        pass

    def build_mail_body(order):
        pass

    def send_mail(order):
        pass
