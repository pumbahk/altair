# -*- coding:utf-8 -*-
from zope.interface import Interface, Attribute

class IMailUtility(Interface):
    def build_message(request, order):
        """orderからメールオブジェクト作成"""
        
    def send_mail(request, order, override=None):
        """ orderからメールを作成して送信"""
        
    def preview_text(request, order):
        """ orderから送信されるメールのpreviewを作成"""
    
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

class IOrderCancelMailPayment(Interface):
    """ 購入キャンセルメールの配送ビューレットのコンテキスト"""
    order = Attribute(u"注文内容")

class IOrderCancelMailDelivery(Interface):
    """ 購入キャンセルメールの配送ビューレットのコンテキスト"""
    order = Attribute(u"注文内容")
