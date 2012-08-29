# -*- coding:utf-8 -*-
from zope.interface import Interface, Attribute

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

    def build_message(order):
        pass

class ICompleteMailPayment(Interface):
    """ 完了メールの配送ビューレットのコンテキスト"""
    order = Attribute(u"注文内容")

class ICompleteMailDelivery(Interface):
    """ 完了メールの配送ビューレットのコンテキスト"""
    order = Attribute(u"注文内容")
