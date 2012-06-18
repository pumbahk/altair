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

