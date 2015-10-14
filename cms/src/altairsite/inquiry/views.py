# -*- coding: utf-8 -*-
from altair.mobile.api import is_mobile_request

from . api import send_inquiry_mail
from . message import SupportMail, CustomerMail
from . session import InquirySession

from altairsite.config import usersite_view_config
from altairsite.smartphone.page.forms import InquiryForm
from altairsite.mobile.core.helper import log_info, log_error

##workaround.
def pc_access(info, request):
    return not is_mobile_request(request)

@usersite_view_config(route_name='usersite.inquiry', request_method="GET",
             custom_predicates=(pc_access, ),
             renderer='altaircms:templates/usersite/inquiry.html')
def move_inquiry(request):
    log_info("move_inquiry", "start")
    form = InquiryForm()
    session = InquirySession(request=request)
    session.put_inquiry_session();
    log_info("move_inquiry", "end")
    return {'form':form}

@usersite_view_config(route_name='usersite.inquiry', request_method="POST",
             custom_predicates=(pc_access, ),
             renderer='altaircms:templates/usersite/inquiry.html')
def send_inquiry(request):
    log_info("send_inquiry", "start")
    form = InquiryForm(request.POST)

    session = InquirySession(request=request)
    if not session.exist_inquiry_session():
        return {
            "form": form,
            "result": True
        }

    if not form.validate():
        return {"form": form}

    customer_mail = CustomerMail(form.data['username'], form.data['username_kana'], form.data['zip_no']
        , form.data['address'], form.data['tel'], form.data['mail'], form.data['num'], form.data['category']
        , form.data['title'], form.data['body'])
    support_mail = SupportMail(form.data['username'], form.data['username_kana'], form.data['zip_no']
        , form.data['address'], form.data['tel'], form.data['mail'], form.data['num'], form.data['category']
        , form.data['title'], form.data['body'], request.environ.get("HTTP_USER_AGENT"))

    send_inquiry_mail(request=request, title=u"楽天チケット　お問い合わせフォーム[PC]", body=support_mail.create_mail(), recipients=[request.inquiry_mailaddress])
    ret = send_inquiry_mail(request=request, title=u"楽天チケット　お問い合わせ", body=customer_mail.create_mail(), recipients=[form.mail.data])

    session.delete_inquiry_session()

    log_info("send_inquiry", "end")
    return {'form': form, 'result': ret}
