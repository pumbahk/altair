# -*- coding:utf-8 -*-
from pyramid.view import render_view_to_response
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

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
