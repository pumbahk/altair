# -*- coding:utf-8 -*-

import logging
from pyramid.renderers import get_renderer
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from zope.interface import Interface, Attribute, implementer
from ticketing.mails.interfaces import ITraverser
from ticketing.cart.helpers import fee_type
from ticketing.payments import plugins

logger = logging.getLogger(__name__)


def get_traverser(request):
    reg = request.registry
    return reg.getUtility(ITraverser, name="lots")

def get_mail_info(request, lot):
    traverser = get_traverser(request)
    traverser.visit(lot.event)
    return traverser.data

class IMailSender(Interface):
    subject = Attribute(u"subject of mail")
    sender = Attribute(u"email address of mail sender")
    tmpl_name = Attribute(u"name of template file for mail body")

    def send(request, entry):
        """ """

@implementer(IMailSender)
class MailSender(object):
    def __init__(self, subject, sender, tmpl_name):
        self.subject = subject
        self.sender = sender
        self.tmpl_name = tmpl_name

    def _create_mail_body(self, request, vars):
        tmpl = get_renderer(self.tmpl_name).implementation()
        return tmpl.render(**vars)

    def _body_tmpl_vars(self, request, lot_entry):
        vars = dict(fee_type=fee_type,
                    lot_entry=lot_entry, lot=lot_entry.lot, 
                    shipping_address=lot_entry.shipping_address,
                    entry_review_url=request.route_url('lots.review.index'),
                    plugins=plugins)
        return vars

    def send(self, request, lot_entry):

        sender = self.sender
        subject = self.subject
        recipients = [lot_entry.shipping_address.email_1]

        vars = self._body_tmpl_vars(request, lot_entry)
        body = self._create_mail_body(request, vars)

        return self._send(request, sender=sender,
                          recipients=recipients,
                          subject=subject,
                          body=body)

    def _send(self, request, 
              sender, recipients,
              subject,body):
        message = Message(sender=sender,
                          recipients=recipients,
                          subject=subject,
                          body=body)
        mailer = get_mailer(request)
        mailer.send(message)
        return message

def get_lotting_mailer(request, name):
    reg = request.registry
    return reg.getUtility(IMailSender, name=name)

def includeme(config):
    registry = config.registry
    prefix = u"lots."

    setup_keys = [("accepted", "accepted_mail_subject", "accepted_mail_sender", 'accepted_mail_template'),  # 申し込み受付メール
                  ("elected", "elected_mail_subject", "elected_mail_sender", 'elected_mail_template'),  # 当選通知メール
                  ("rejected", "rejected_mail_subject", "rejected_mail_sender", 'rejected_mail_template'),  # 落選通知メール
                  ]

    for name, subject, sender, tmpl_name_key in setup_keys:
        tmpl_name = registry.settings.get(prefix + tmpl_name_key)
        subject = unicode(config.registry.settings.get(prefix + subject) or '', 'utf-8')
        sender = unicode(config.registry.settings.get(prefix + sender) or '', 'utf-8')
        if tmpl_name is None or subject is None or sender is None:
            logger.warning('cannot find setting for lotting mail %s' % name)
            continue
        mail_sender = MailSender(subject, sender, tmpl_name)

        registry.utilities.register([], IMailSender, name, mail_sender)



def send_accepted_mail(request, lot_entry):
    """ 申し込み完了メール
    """
    mailer = get_lotting_mailer(request, name="accepted")
    return mailer.send(request, lot_entry)

def send_elected_mail(request, elected_entry):
    """ 当選通知メール
    """
    mailer = get_lotting_mailer(request, name="elected")
    return mailer.send(elected_entry)

def send_rejected_mail(request, rejected_entry):
    """ 落選通知メール
    """
    mailer = get_lotting_mailer(request, name="rejected")
    return mailer.send(rejected_entry)
