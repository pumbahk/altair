# -*- coding: utf-8 -*-
from pyramid_mailer.message import Message
from pyramid_mailer import get_mailer
from altairsite.config import usersite_view_config
from altairsite.inquiry.forms import InquiryForm
from altairsite.mobile.core.helper import log_info, log_error


##workaround.
def pc_access(info, request):
    return hasattr(request, "is_mobile") and request.is_mobile == False

@usersite_view_config(route_name='usersite.inquiry', request_method="GET",
             custom_predicates=(lambda _, request: is_nonmobile(request), ), 
             renderer='altaircms:templates/usersite/inquiry.html')
def move_inquiry(request):
    log_info("move_inquiry", "start")
    form = InquiryForm()
    log_info("move_inquiry", "end")
    return {'form':form}

@usersite_view_config(route_name='usersite.inquiry', request_method="POST",
             custom_predicates=(lambda _, request: is_nonmobile(request), ), 
             renderer='altaircms:templates/usersite/inquiry.html')
def send_inquiry(request):
    log_info("send_inquiry", "start")

    form = InquiryForm(request.POST)

    if not form.validate():
        return {"form": form}

    log_info("send_inquiry", "send mail start")
    form.send.data = "Success"
    try:
        send_mail(request=request, title=u'楽天チケット　お問い合わせフォーム', body=create_mail_body(form), recipients=[request.inquiry_mailaddress])
    except Exception as e:
        log_error("send_inquiry", str(e))
        form.send.data = "Failed"
    log_info("send_inquiry", "send mail end")

    log_info("send_inquiry", "send mail for customer start")
    try:
        send_mail(request=request, title=u'楽天チケット　お問い合わせ', body=create_mail_body_for_customer(form), recipients=[form.mail.data])
    except Exception as e:
        log_error("send_inquiry", str(e))
    log_info("send_inquiry", "send mail for customer end")

    log_info("send_inquiry", "end")
    return {'form':form}

def send_mail(request, title, body, recipients):
    mailer = get_mailer(request)
    message = Message(subject=title,
                      sender=request.sender_mailaddress,
                      recipients=recipients,
                      body=body)
    mailer.send(message)

def create_mail_body(form):
    body = form.username.data + u"さんからのお問合せです。\n"
    body = body + u"メールアドレス：" + form.mail.data + u"\n"
    body = body + u"予約受付番号：" + form.num.data + u"\n\n"

    body = body + u"---------------------------------------\n"
    body = body + u"カテゴリ：" + form.category.data + u"\n"
    body = body + u"件名：" + form.title.data + u"\n"
    body = body + u"---------------------------------------\n"
    body = body + u"内容：" + form.body.data
    return body

def create_mail_body_for_customer(form):
    body = form.username.data + u"様\n\n"

    body = body + u"いつも楽天チケットをご利用頂き、誠にありがとうございます。\n"
    body = body + u"この度は、弊社にお問い合わせを頂き、ありがとうございました。以下の内容で、お問い合わせを受け付けました。\n\n"

    body = body + u"予約受付番号：" + form.num.data + u"\n"
    body = body + u"カテゴリ：" + form.category.data + u"\n"
    body = body + u"件名：" + form.title.data + u"\n"
    body = body + u"内容：" + form.body.data + u"\n\n"

    body = body + u"お問い合わせ頂いた内容については、弊社カスタマーサポート担当より、3営業日以内にご返答させていただきます。\n"
    body = body + u"また、お預かりするお客様の個人情報は、『個人情報保護方針』に基いて厳重に管理し、お問い合わせ・ご相談への対応以外には使用いたしません。\n"
    body = body + u"よろしくお願いいたします。\n\n"

    body = body + u"---------\n"
    body = body + u"楽天チケット\n"
    body = body + u"カスタマーサポート担当\n"
    body = body + u"運営会社：（株）チケットスター\n"
    return body
