# -*- coding:utf-8 -*-
from zope.interface import Interface, Attribute

class IMailDataStoreGetter(Interface):
    def __call__(request, subject, mtype):
        pass

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
    def get_mailtype_description():
        """メールの種別"""

    def get_subject_info_default():
        """デフォルト値を格納するオブジェクト"""

    def create_or_update_mailinfo(request, data, organization=None, event=None, performance=None, kind=None):
        pass

    def create_fake_object(request, **kwargs):
        """fake object (something) を生成"""

    def build_message(request, something):
        """orderからメールオブジェクト作成"""

    def send_mail(request, something, override=None):
        """ orderからメールを作成して送信"""

    def preview_text(request, something):
        """ orderから送信されるメールのpreviewを作成"""


class IMailBuilder(Interface):
    def build_mail_body(request, something, traverser):
        pass

    def build_message_from_mail_body(request, something, traverser, mail_body):
        pass

    def build_message(request, something, traverser):
        pass

class IPurchaseInfoMail(IMailBuilder):
    pass

class ICompleteMail(IPurchaseInfoMail):
    """完了メールを送る
    """

class ICancelMail(IPurchaseInfoMail):
    """ 購入キャンセルメールを送る
    """

class IRemindMail(IPurchaseInfoMail):
    """ 支払いリマインドメールを送る
    """

class IPointGrantHistoryEntryInfoMail(IMailBuilder):
    pass

class ILotEntryInfoMail(IMailBuilder):
    pass

class ICompleteMailResource(Interface):
    """ 完了メールのビューレットのコンテキスト"""
    request = Attribute("r")
    order = Attribute(u"注文内容")

class IOrderCancelMailResource(Interface):
    """ 購入キャンセルメールのビューレットのコンテキスト"""
    request = Attribute("r")
    order = Attribute(u"注文内容")

class ILotsAcceptedMailResource(Interface):
    """ 抽選申し込み完了メールのビューレットのコンテキスト"""
    request = Attribute("r")
    order = Attribute(u"抽選注文")

class ILotsElectedMailResource(Interface):
    """ 抽選通知メールのビューレットのコンテキスト"""
    request = Attribute("r")
    order = Attribute(u"抽選注文")

class ILotsRejectedMailResource(Interface):
    """ 抽選落選通知メールのビューレットのコンテキスト"""
    request = Attribute("r")
    order = Attribute(u"抽選注文")

class IMessagePartFactory(Interface):
    """ 送信されるメールのメッセージパートを生成する factory """

    def __call__(request, text_body):
        pass

class IFakeObjectFactory(Interface):
    def __call__(request, interface, args):
        pass

class IMailRequest(Interface):
    pass
