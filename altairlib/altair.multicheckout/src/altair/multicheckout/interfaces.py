# -*- coding:utf-8 -*-

""" TBA
"""
from zope.interface import Interface, Attribute

class IMultiCheckout(Interface):
    def request_card_check(order_no, card_auth):
        """ 
        """
        
    def request_card_auth(order_no, card_auth):
        """ 
        """

    def request_card_cancel_auth(order_no, card_auth):
        """ 
        """

    def request_card_sales(order_no, card_auth):
        """ 
        """

    def request_card_cancel_sales(order_no, card_auth):
        """ 
        """

    def request_card_inquiry(order_no, card_auth):
        """ 
        """

class ICardBrandDetecter(Interface):
    def __call__(card_number):
        """
        :return: str of brand symbol
        """

class ICancelFilter(Interface):
    def is_cancelable(order_no):
        """ checkf for cancelable """


class IMulticheckoutSetting(Interface):
    shop_name = Attribute(u"マルチチェックアウト店舗名")
    shop_id = Attribute(u"店舗コード")
    auth_id = Attribute(u"API 認証ID")
    auth_password = Attribute(u"API 認証パスワード")

class IMulticheckoutSettingFactory(Interface):
    def __call__(request, override_name):
        """ get IMultiChekoutSetting """

class IMulticheckoutSettingListFactory(Interface):
    def __call__(request):
        """ get list of IMultiChekoutSetting """
