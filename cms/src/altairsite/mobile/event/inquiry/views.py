# -*- coding: utf-8 -*-
from altairsite.config import mobile_site_view_config
from altairsite.smartphone.page.forms import InquiryForm
from altairsite.mobile.core.helper import log_info
from altairsite.inquiry.api import send_inquiry_mail
from altairsite.inquiry.message import SupportMail, CustomerMail
from altairsite.separation import selectable_renderer

@mobile_site_view_config(route_name='inquiry', request_method="GET", request_type="altair.mobile.interfaces.IMobileRequest",
             renderer=selectable_renderer('altairsite.mobile:templates/%(prefix)s/inquiry/inquiry.mako'))
def move_inquiry(request):
    log_info("move_inquiry", "start")
    form = InquiryForm()
    log_info("move_inquiry", "end")
    return {'form':form}

@mobile_site_view_config(route_name='inquiry', request_method="POST", request_type="altair.mobile.interfaces.IMobileRequest",
             renderer=selectable_renderer('altairsite.mobile:templates/%(prefix)s/inquiry/inquiry.mako'))
def send_inquiry(request):
    log_info("send_inquiry", "start")

    form = InquiryForm(request.POST)

    if not form.validate():
        return {"form": form}

    log_info("send_inquiry", "send mail start")
    form.send.data = "Success"
    customer_mail = CustomerMail(form.data['username'], form.data['username_kana'], form.data['zip_no']
        , form.data['address'], form.data['tel'], form.data['mail'], form.data['num'], form.data['category']
        , form.data['title'], form.data['body'])
    support_mail = SupportMail(form.data['username'], form.data['username_kana'], form.data['zip_no']
        , form.data['address'], form.data['tel'], form.data['mail'], form.data['num'], form.data['category']
        , form.data['title'], form.data['body'], request.environ.get("HTTP_USER_AGENT"))

    send_inquiry_mail(request=request, title=u"楽天チケット　お問い合わせフォーム[モバイル]", body=support_mail.create_mail(), recipients=[request.inquiry_mailaddress])
    ret = send_inquiry_mail(request=request, title=u"楽天チケット　お問い合わせ", body=customer_mail.create_mail(), recipients=[form.mail.data])

    if not ret:
        form.send.data = "Failed"

    log_info("send_inquiry", "end")
    return {'form':form}
