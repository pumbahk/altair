# -*- coding:utf-8 -*-
from zope.interface import Interface, Attribute

class ITraverser(Interface):
    data = Attribute(u"traversed mail information")
    def visit(target):
        """ start traverse """

class ITraverserFactory(Interface):
    def __call__(request, subject):
        pass

class IMailSettingDefault(Interface):
    def get_bcc(request, traverser, organization):
        pass

    def get_sender(request, traverser, organization):
        pass

class IMailUtility(Interface):
    def build_message(request, order):
        """orderからメールオブジェクト作成"""
        
    def send_mail(request, order, override=None):
        """ orderからメールを作成して送信"""
        
    def preview_text(request, order):
        """ orderから送信されるメールのpreviewを作成"""

class IPurchaseInfoMail(Interface):
    request = Attribute("request")

    def build_mail_body(order, traverser):
        pass

    def build_message_from_mail_body(order, traverser, mail_body):
        pass

    def build_message(order, traverser):
        pass

class ICompleteMail(IPurchaseInfoMail):
    """完了メールを送る
    """

class ICancelMail(IPurchaseInfoMail):
    """ 購入キャンセルメールを送る
    """

class ICompleteMailPayment(Interface):
    """ 完了メールの配送ビューレットのコンテキスト"""
    request = Attribute("r")
    order = Attribute(u"注文内容")

class ICompleteMailDelivery(Interface):
    """ 完了メールの配送ビューレットのコンテキスト"""
    request = Attribute("r")
    order = Attribute(u"注文内容")

class IOrderCancelMailPayment(Interface):
    """ 購入キャンセルメールの配送ビューレットのコンテキスト"""
    request = Attribute("r")
    order = Attribute(u"注文内容")

class IOrderCancelMailDelivery(Interface):
    """ 購入キャンセルメールの配送ビューレットのコンテキスト"""
    request = Attribute("r")
    order = Attribute(u"注文内容")

class ILotsAcceptedMailPayment(Interface):
    """ 抽選申し込み完了メールの配送ビューレットのコンテキスト"""
    request = Attribute("r")
    order = Attribute(u"抽選注文")

class ILotsAcceptedMailDelivery(Interface):
    """ 抽選申し込み完了メールの配送ビューレットのコンテキスト"""
    request = Attribute("r")
    order = Attribute(u"抽選注文")

class ILotsElectedMailPayment(Interface):
    """ 抽選通知メールの配送ビューレットのコンテキスト"""
    request = Attribute("r")
    order = Attribute(u"抽選注文")

class ILotsElectedMailDelivery(Interface):
    """ 抽選通知メールの配送ビューレットのコンテキスト"""
    request = Attribute("r")
    order = Attribute(u"抽選注文")

class ILotsRejectedMailPayment(Interface):
    """ 抽選落選通知メールの配送ビューレットのコンテキスト"""
    request = Attribute("r")
    order = Attribute(u"抽選注文")

class ILotsRejectedMailDelivery(Interface):
    """ 抽選落選通知メールの配送ビューレットのコンテキスト"""
    request = Attribute("r")
    order = Attribute(u"抽選注文")
