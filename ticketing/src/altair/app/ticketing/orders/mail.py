# -*- coding:utf-8 -*-
import logging
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from pyramid.renderers import render_to_response

from altair.app.ticketing.mails.api import get_mail_utility
from altair.app.ticketing.core.models import MailTypeEnum

logger = logging.getLogger(__name__)

Cancel = MailTypeEnum.PurchaseCancelMail
def on_order_canceled(event):
    get_mail_utility(event.request, Cancel).send_mail(event.request, event.order)

def send_refund_reserve_mail(request, refund, mail_refund_to_user, orders):
    subject_prefix = u'[払戻予約]'
    subject = subject_prefix + u' ' + u', '.join([p.name for p in refund.performances])
    recipients = [refund.organization.contact_email]
    body_template = 'altair.app.ticketing:templates/orders/refund_reserve_mail.txt'
    body = render_to_response(body_template, dict(refund=refund))
    mutil = get_mail_utility(request, MailTypeEnum.PurchaseRefundMail)
    if mail_refund_to_user is not None and mail_refund_to_user:
        for order in orders:
            mutil.send_mail(request, order)
    return send(request, subject, recipients, body)

def send_refund_complete_mail(request, refund):
    subject_prefix = u'[払戻完了]'
    subject = subject_prefix + u' ' + u', '.join([p.name for p in refund.performances])
    recipients = [refund.organization.contact_email]
    body_template = 'altair.app.ticketing:templates/orders/refund_complete_mail.txt'
    body = render_to_response(body_template, dict(refund=refund))
    return send(request, subject, recipients, body)

def send_refund_error_mail(request, refund, message):
    subject_prefix = u'[払戻エラー]'
    subject = subject_prefix + u' ' + u', '.join([p.name for p in refund.performances])
    recipients = [refund.organization.contact_email]
    body_template = 'altair.app.ticketing:templates/orders/refund_error_mail.txt'
    body = render_to_response(body_template, dict(refund=refund, message=message))
    return send(request, subject, recipients, body)

def send(request, subject, recipients, body):
    mailer = get_mailer(request)
    sender = request.registry.settings.get('mail.message.sender')
    recipients.append(request.registry.settings.get('mail.report.recipient', u'dev@ticketstar.jp'))
    message = Message(subject=subject,
                      recipients=recipients,
                      body=body.text,
                      sender=sender)
    try:
        mailer.send(message)
        return True
    except Exception, e:
        logging.error(u'メール送信失敗 %s' % e.message)
        return False
