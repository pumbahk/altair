# -*- coding: utf-8 -*-
from pyramid.view import view_config
from altairsite.inquiry.forms import InquiryForm
from altairsite.mobile.core.helper import log_info, log_error
from altairsite.inquiry.views import send_mail, create_mail_body, create_mail_body_for_customer

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

    if not form.validate():
        return {"form": form}

    log_info("send_inquiry", "send mail start")
    form.send.data = "Success"
    try:
        send_mail(request=request, title=u'楽天チケット[MOB]　お問い合わせフォーム', body=create_mail_body(form), recipients=[request.inquiry_mailaddress])
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
