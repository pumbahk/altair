# -*- coding:utf-8 -*-
import logging
from pyramid.view import render_view_to_response
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from altair.app.ticketing.core.api import get_organization, get_organization_setting, is_mobile_request
logger = logging.getLogger(__name__)

def send_qr_mail(request, context, recipient, sender):
    mail_body = get_mailbody_from_viewlet(request, context, "render.mail")
    return _send_mail_simple(request, recipient, sender, mail_body, 
                             subject=u"QRチケットに関しまして", )

def get_mailbody_from_viewlet(request, context, viewname):
    response = render_view_to_response(context, request, name=viewname)
    if response is None:
        raise ValueError
    return response.text

def _send_mail_simple(request, recipient, sender, mail_body, subject=u"QRチケットに関しまして"):
    message = Message(
            subject=subject, 
            recipients=[recipient], 
            #bcc=bcc,
            body=mail_body,
            sender=sender)
    return get_mailer(request).send(message)

def get_contact_url(request, fail_exc=None):
    organization = get_organization(request)
    if organization is None:
        raise fail_exc("organization is not found")
    setting = get_organization_setting(request, organization)
    if is_mobile_request(request):
        if setting.contact_mobile_url is None:
            raise fail_exc("contact url is not found. (organization_id = %s)" % (organization.id))
        return setting.contact_mobile_url
    else:
        if setting.contact_pc_url is None:
            raise fail_exc("contact url is not found. (organization_id = %s)" % (organization.id))
        return setting.contact_pc_url

def safe_get_contact_url(request, default=""):
    try:
        return get_contact_url(request, Exception)
    except Exception as e:
        logger.warn(str(e))
        return default

