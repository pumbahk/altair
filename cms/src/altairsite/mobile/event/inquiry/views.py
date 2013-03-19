# -*- coding: utf-8 -*-
from pyramid.view import view_config
from altairsite.mobile.core.const import get_category_name
from altairsite.mobile.event.inquiry.forms import InquiryForm
from altairsite.mobile.core.helper import log_info, log_error
from pyramid_mailer.message import Message
from pyramid_mailer import get_mailer
from pyramid.httpexceptions import HTTPNotFound

@view_config(route_name='inquiry', request_method="GET", request_type="altairsite.mobile.tweens.IMobileRequest",
             renderer='altairsite.mobile:templates/inquiry/inquiry.mako')
def move_inquiry(request):
    log_info("move_inquiry", "start")
    form = InquiryForm()
    log_info("move_inquiry", "end")
    return {'form':form}

@view_config(route_name='inquiry', request_method="POST", request_type="altairsite.mobile.tweens.IMobileRequest",
             renderer='altairsite.mobile:templates/inquiry/inquiry.mako')
def send_inquiry(request):
    log_info("send_inquiry", "start")

    form = InquiryForm(request.POST)

    if form.validate():
        form.send.data = True
        try:
            log_info("send_inquiry", "send mail start")
            mailer = get_mailer(request)
            message = Message(subject=u'楽天チケット[MOB]　お問合せフォーム',
                              sender=request.sender_mailaddress,
                              recipients=[request.inquiry_mailaddress],
                              body=_create_mail_body(form))
            mailer.send(message)
            log_info("send_inquiry", "send mail end")
        except Exception as e:
            log_error("send_inquiry", str(e))
            raise HTTPNotFound

    log_info("send_inquiry", "end")
    return {'form':form}

def _create_mail_body(form):
    body = form.name.data + u"さんからのお問合せです。\n"
    body = body + u"メールアドレス：" + form.mail.data + u"\n"
    body = body + u"予約受付番号：" + form.num.data + u"\n\n"
    body = body + u"---------------------------------------\n"
    body = body + u"カテゴリ：" + get_category_name(form.category.data) + u"\n"
    body = body + u"件名：" + form.title.data + u"\n"
    body = body + u"---------------------------------------\n"
    body = body + u"内容：" + form.body.data
    return body