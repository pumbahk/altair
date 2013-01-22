# -*- coding:utf-8 -*-

from pyramid.renderers import get_renderer
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

def get_accepted_mail_subject(request):
    return unicode(request.registry.settings["lots.accepted_mail_subject"], 'utf-8')

def get_accepted_mail_sender(request):
    return unicode(request.registry.settings["lots.accepted_mail_sender"], 'utf-8')

def get_elected_mail_subject(request):
    return unicode(request.registry.settings["lots.elected_mail_subject"], 'utf-8')

def get_elected_mail_sender(request):
    return unicode(request.registry.settings["lots.elected_mail_sender"], 'utf-8')

def get_rejected_mail_subject(request):
    return unicode(request.registry.settings["lots.elected_mail_subject"], 'utf-8')

def get_rejected_mail_sender(request):
    return unicode(request.registry.settings["lots.elected_mail_sender"], 'utf-8')

def create_mail_body(request, vars, tmpl_name_key):
    tmpl_name = request.registry.settings[tmpl_name_key]
    tmpl = get_renderer(tmpl_name).implementation()
    return tmpl.render(**vars)

def _send_mail(request, message):
    mailer = get_mailer(request)    
    mailer.send(message)

def send_accepted_mail(request, lot_entry):
    """ 申し込み完了メール
    """

    recipients = [lot_entry.shipping_address.email_1]
    subject = get_accepted_mail_subject(request)
    sender = get_accepted_mail_sender(request)
    vars = dict(lot_entry=lot_entry, lot=lot_entry.lot, 
        shipping_address=lot_entry.shipping_address,
        entry_review_url=request.route_url('lots.review.index'))
    body = create_mail_body(request, vars, 'lots.accepted_mail_template')

    message = Message(sender=sender,
                      recipients=recipients,
                      subject=subject,
                      body=body)
    _send_mail(request, message)
    return message

def send_elected_mail(request, elected_entry):
    """ 当選通知メール
    """
    lot_entry = elected_entry.lot_entry
    recipients = [lot_entry.shipping_address.email_1]
    subject = get_subject(request)
    sender = get_sender(request)
    vars = dict(lot_entry=lot_entry, lot=lot_entry.lot, shipping_address=lot_entry.shipping_address)
    body = create_mail_body(request, vars, 'lots.elected_mail_template')

    message = Message(sender=sender,
                      recipients=recipients,
                      subject=subject,
                      body=body)
    _send_mail(request, message)
    return message

def send_rejected_mail(request, rejected_entry):
    """ 落選通知メール
    """
    
    lot_entry = rejected_entry.lot_entry
    recipients = [lot_entry.shipping_address.email_1]
    subject = get_subject(request)
    sender = get_sender(request)
    vars = dict(lot_entry=lot_entry, lot=lot_entry.lot)
    body = create_mail_body(request, vars, 'lots.rejected_mail_template')

    message = Message(sender=sender,
                      recipients=recipients,
                      subject=subject,
                      body=body)
    _send_mail(request, message)
    return message
