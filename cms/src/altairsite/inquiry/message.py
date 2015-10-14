#-*- coding: utf-8 -*-
from .interface import IMailMessage
from zope.interface import implements

class SupportMail:

    implements(IMailMessage)

    def __init__(self, username, username_kana, zip_no, address, tel, mail, num, category, title, body, user_agent):
        self.username = username
        self.username_kana = username_kana
        self.zip_no = zip_no
        self.address = address
        self.tel = tel
        self.mail = mail
        self.num = num
        self.category = category
        self.title = title
        self.body = body
        self.user_agent = user_agent

    def create_mail(self):
        result = self.username + "(" + self.username_kana+ ")" + u"さんからのお問合せです。\n"
        result = result + u"メールアドレス：" + self.mail + u"\n"
        result = result + u"電話番号：" + self.tel + u"\n"
        result = result + u"住所：〒" + self.zip_no + u"\n" + self.address + u"\n"
        result = result + u"受付番号：" + self.num + u"\n\n"

        result = result + u"---------------------------------------\n"
        result = result + u"カテゴリ：" + self.category + u"\n"
        result = result + u"件名：" + self.title + u"\n"
        result = result + u"---------------------------------------\n"
        result = result + u"内容：" + self.body + u"\n\n"

        result = result + self.user_agent
        return result

class CustomerMail:

    implements(IMailMessage)

    def __init__(self, username, username_kana, zip_no, address, tel, mail, num, category, title, body):
        self.username = username
        self.username_kana = username_kana
        self.zip_no = zip_no
        self.address = address
        self.tel = tel
        self.mail = mail
        self.num = num
        self.category = category
        self.title = title
        self.body = body

    def create_mail(self):
        result = self.username+ u"様\n\n"

        result = result + u"いつも楽天チケットをご利用頂き、誠にありがとうございます。\n"
        result = result + u"この度は、弊社にお問い合わせを頂き、ありがとうございました。以下の内容で、お問い合わせを受け付けました。\n\n"

        result = result + u"受付番号：" + self.num + u"\n"
        result = result + u"カテゴリ：" + self.category + u"\n"
        result = result + u"件名：" + self.title + u"\n"
        result = result + u"内容：" + self.body + u"\n\n"

        result = result + u"お問い合わせ頂いた内容については、弊社カスタマーサポート担当より、基本的に返信メールにて、3営業日内に回答させていただきます。\n"
        result = result + u"(土日祝は原則対応いたしかねます)\n"
        result = result + u"また、お預かりするお客様の個人情報は、『個人情報保護方針』に基いて厳重に管理し、お問い合わせ・ご相談への対応以外には使用いたしません。\n"
        result = result + u"よろしくお願いいたします。\n\n"

        result = result + u"---------\n"
        result = result + u"楽天チケット\n"
        result = result + u"カスタマーサポート担当\n"
        result = result + u"運営会社：（株）チケットスター\n"
        return result
