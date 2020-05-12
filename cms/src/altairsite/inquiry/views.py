# -*- coding: utf-8 -*-
from datetime import datetime

from altair.i18n.api import set_locale_cookie
from altair.mobile.api import is_mobile_request
from altairsite.config import usersite_view_config
from altairsite.mobile.core.helper import log_info
from altairsite.smartphone.page.forms import RtInquiryForm, StInquiryForm
from pyramid.httpexceptions import HTTPNotFound

from .api import send_inquiry_mail
from .message import SupportMailRT, CustomerMailRT, CustomerMailST, SupportMailST
from .session import InquirySession
from ..separation import selectable_renderer

def pc_access(info, request):
    # workaround.
    return not is_mobile_request(request)


@usersite_view_config(route_name='locale', request_method="GET", custom_predicates=(pc_access,))
def set_cookie(request):
    return set_locale_cookie(request)


@usersite_view_config(route_name='usersite.inquiry', request_method="GET",
                      custom_predicates=(pc_access,),
                      renderer=selectable_renderer('altaircms:templates/usersite/inquiry/%(prefix)s/inquiry.html'))
def move_inquiry(request):
    log_info("move_inquiry", "start")

    form = get_org_form(request)
    if not form:
        return HTTPNotFound()
    form.admission_time.data = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    session = InquirySession(request=request)
    session.put_inquiry_session()
    log_info("move_inquiry", "end")
    return {'form': form}


@usersite_view_config(route_name='usersite.inquiry', request_method="POST",
                      custom_predicates=(pc_access,),
                      renderer=selectable_renderer('altaircms:templates/usersite/inquiry/%(prefix)s/inquiry.html'))
def send_inquiry(request):
    log_info("send_inquiry", "start")

    form = get_org_form(request)
    session = InquirySession(request=request)
    if not session.exist_inquiry_session():
        return {
            "form": form,
            "result": True
        }

    if not form.validate():
        return {"form": form, 'result': False}

    ret = send_inquiry_mail_org(request)

    session.delete_inquiry_session()

    log_info("send_inquiry", "end")

    return {'form': form, 'result': ret}


def send_inquiry_mail_org(request):
    ret = True

    if request.organization.short_name == "RT":
        ret = send_inquiry_mail_rt(request)

    if request.organization.short_name == "ST":
        ret = send_inquiry_mail_st(request)

    return ret


def send_inquiry_mail_rt(request):
    form = RtInquiryForm(request.POST)
    ret = True

    customer_mail = CustomerMailRT(form.data['username'], form.data['username_kana'], form.data['zip_no']
                                 , form.data['address'], form.data['tel'], form.data['mail'], form.data['reception_number'],
                                 form.data['category']
                                 , form.data['title'], form.data['body'])
    support_mail = SupportMailRT(form.data['username'], form.data['username_kana'], form.data['zip_no']
                               , form.data['address'], form.data['tel'], form.data['mail'], form.data['reception_number'],
                               form.data['category']
                               , form.data['title'], form.data['body'], request.environ.get("HTTP_USER_AGENT"))

    ret = send_inquiry_mail(request=request, title=u"楽天チケット　お問い合わせフォーム[PC]", body=support_mail.create_mail(),
                      recipients=[request.inquiry_mailaddress])
    if ret:
        ret = send_inquiry_mail(request=request, title=u"楽天チケット　お問い合わせ", body=customer_mail.create_mail(),
                            recipients=[form.mail.data])
    return ret


def send_inquiry_mail_st(request):
    form = StInquiryForm(request.POST)
    ret = True

    customer_mail = CustomerMailST(form.data['username'], form.data['username_kana'], form.data['mail']
                                 , form.data['zip_no'], form.data['address'], form.data['tel']
                                 , form.data['reception_number'], form.data['app_status'], form.data['event_name']
                                 , form.data['start_date'], form.data['category'], form.data['body'])

    support_mail = SupportMailST(form.data['username'], form.data['username_kana'], form.data['mail']
                                 , form.data['zip_no'], form.data['address'], form.data['tel']
                                 , form.data['reception_number'], form.data['app_status'], form.data['event_name']
                                 , form.data['start_date'], form.data['category'], form.data['body'], request.environ.get("HTTP_USER_AGENT"))


    ret = send_inquiry_mail(request=request, title=u"SMA TICKET　お問い合わせフォーム[PC]", body=support_mail.create_mail(),
                      recipients=[request.inquiry_mailaddress])
    if ret:
        ret = send_inquiry_mail(request=request, title=u"SMA TICKET　お問い合わせ", body=customer_mail.create_mail(),
                            recipients=[form.mail.data])
    return ret


def get_org_form(request):
    form = None

    if request.organization.short_name == "RT":
        form = RtInquiryForm(request.POST)

    if request.organization.short_name == "ST":
        form = StInquiryForm(request.POST)

    return form
