# -*- coding: utf-8 -*-
from pyramid_mailer.message import Message
from pyramid_mailer import get_mailer
from pyramid.view import view_config
from altairsite.inquiry.forms import InquiryForm
from altairsite.mobile.core.helper import log_info, log_error

@view_config(route_name='inquirypage', request_method="GET",
             renderer='altaircms:templates/usersite/inquiry.html')
def move_inquiry(request):

    log_info("move_inquiry", "start")
    form = InquiryForm()
    log_info("move_inquiry", "end")
    return {'form':form}

@view_config(route_name='inquirypage', request_method="POST",
             renderer='altaircms:templates/usersite/inquiry.html')
def send_inquiry(request):
    log_info("send_inquiry", "start")

    form = InquiryForm(request.POST)

    if form.validate():
        form.send.data = "Success"
        try:
            log_info("send_inquiry", "send mail start")
            mailer = get_mailer(request)
            message = Message(subject=u'楽天チケット[PC]　お問合せフォーム',
                              sender=request.sender_mailaddress,
                              recipients=[request.inquiry_mailaddress],
                              body=_create_mail_body(form))
            mailer.send(message)
            log_info("send_inquiry", "send mail end")
        except Exception as e:
            log_error("send_inquiry", str(e))
            form.send.data = "Failed"

    log_info("send_inquiry", "end")
    return {'form':form}

def _create_mail_body(form):
    body = form.name.data + u"さんからのお問合せです。\n"
    body = body + u"メールアドレス：" + form.mail.data + u"\n"
    body = body + u"予約受付番号：" + form.num.data + u"\n\n"
    body = body + u"---------------------------------------\n"
    body = body + u"カテゴリ：" + form.category.data + u"\n"
    body = body + u"件名：" + form.title.data + u"\n"
    body = body + u"---------------------------------------\n"
    body = body + u"内容：" + form.body.data
    return body
