# -*- coding:utf-8 -*-

""" TBA
"""
#from ticketing.mails.interfaces import ICompleteMailDelivery, ICompleteMailPayment
#from ticketing.mails.interfaces import IOrderCancelMailDelivery, IOrderCancelMailPayment
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


class ICartPayment(Interface):
    """ 確認画面の決済ビューレットのコンテキスト"""
    cart = Attribute(u"カート")


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
