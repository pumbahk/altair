#-*- coding: utf-8 -*-
from .interface import IMailMessage
from zope.interface import implements


# 楽天チケット
class SupportMailRT:

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


class CustomerMailRT:

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


# SMAチケット
class SupportMailST:

    implements(IMailMessage)

    def __init__(self, username, username_kana, mail, zip_no, address, tel, num, app_status, event_name, start_date, category, body, user_agent):
        self.username = username
        self.username_kana = username_kana
        self.mail = mail
        self.zip_no = zip_no
        self.address = address
        self.tel = tel
        self.num = num
        self.app_status = app_status
        self.event_name = event_name
        self.start_date = start_date
        self.category = category
        self.body = body

    def create_mail(self):
        result = self.username + "(" + self.username_kana+ ")" + u"さんからのお問合せです。\n"
        result = result + u"メールアドレス：" + str(self.mail) + u"\n"
        result = result + u"住所：〒" + self.zip_no + u"\n" + self.address + u"\n"
        result = result + u"電話番号：" + str(self.tel) + u"\n"

        result = result + u"---------------------------------------\n"
        result = result + u"受付番号：" + str(self.num) + u"\n\n"
        result = result + u"申し込み状況：" + self.app_status + u"\n\n"
        result = result + u"公演・イベント名：" + self.event_name + u"\n\n"
        result = result + u"開催日時：" + self.start_date + u"\n\n"
        result = result + u"お問い合わせ項目：" + self.category + u"\n"
        result = result + u"---------------------------------------\n"
        result = result + u"お問い合わせ内容：" + self.body + u"\n\n"

        result = result + self.user_agent + u"\n\n"
        return result


class CustomerMailST:

    implements(IMailMessage)

    def __init__(self, username, username_kana, mail, zip_no, address, tel, num, app_status, event_name, start_date, category, body):
        self.username = username
        self.username_kana = username_kana
        self.mail = mail
        self.zip_no = zip_no
        self.address = address
        self.tel = tel
        self.num = num
        self.app_status = app_status
        self.event_name = event_name
        self.start_date = start_date
        self.category = category
        self.body = body

    def create_mail(self):
        result = self.username + u"様\n\n"

        result = result + u"いつもSMAチケットをご利用頂き、誠にありがとうございます。\n"
        result = result + u"この度は、弊社にお問い合わせを頂き、ありがとうございました。以下の内容で、お問い合わせを受け付けました。\n\n"

        result = result + u"受付番号：" + str(self.num) + u"\n"
        result = result + u"申し込み状況：" + self.app_status + u"\n"
        result = result + u"公演・イベント名：" + self.event_name + u"\n"
        result = result + u"開催日時：" + str(self.start_date) + u"\n"
        result = result + u"お問い合わせ項目：" + self.category + u"\n"
        result = result + u"お問い合わせ内容：" + self.body + u"\n\n"
        result = result + u"お問い合わせ頂いた内容については、弊社カスタマーサポート担当より、基本的に返信メールにて、3営業日内に回答させていただきます。\n"
        result = result + u"※購入されたチケットの変更・キャンセルの依頼についてはお受けできません。\n"
        result = result + u"その他（SMAアーティスト・SMAVOICE・UCFC等）各種会員サイトに関しては、別サイトになりますので、お答えできない場合がございます。\n"
        result = result + u"また、お預かりするお客様の個人情報は、『個人情報保護方針』に基いて厳重に管理し、お問い合わせ・ご相談への対応以外には使用いたしません。\n"
        result = result + u"よろしくお願いいたします。\n\n"

        result = result + u"---------\n"
        result = result + u"SMAチケット\n"
        result = result + u"カスタマーサポート担当\n"
        result = result + u"運営会社：（株）ソニー・ミュージックアーティスツ\n"
        return result
