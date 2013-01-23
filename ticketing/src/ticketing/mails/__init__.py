import functools
from pyramid.interfaces import IRequest
from ticketing.core.models import MailTypeEnum
from .interfaces import IMailUtility

def register_mailutilty(config, util, name):
    util = config.maybe_dotted(util)
    assert util.create_or_update_mailinfo
    assert util.get_order_info_default
    assert util.get_traverser
    assert util.build_message
    assert util.send_mail
    config.registry.registerUtility(util, IMailUtility, name=name)

PURCHASE_MAILS = {
    "complete": str(MailTypeEnum.CompleteMail), 
    "cancel": str(MailTypeEnum.PurchaseCancelMail)
}

def install_mail_utility(config):
    from ticketing.mails.interfaces import IPurchaseInfoMail

    register_mailutilty(config, ".complete", PURCHASE_MAILS["complete"])
    from ticketing.mails.complete import CompleteMail
    config.include(config.registry.settings["altair.mailer"])
    complete_mail_factory = functools.partial(CompleteMail, "ticketing:templates/mail/complete.mako")
    config.registry.adapters.register([IRequest], IPurchaseInfoMail, PURCHASE_MAILS["complete"], complete_mail_factory)

    from ticketing.mails.order_cancel import CancelMail
    register_mailutilty(config, ".order_cancel", name=PURCHASE_MAILS["cancel"])
    cancel_mail_factory = functools.partial(CancelMail, "ticketing:templates/mail/order_cancel.txt")
    config.registry.adapters.register([IRequest], IPurchaseInfoMail, PURCHASE_MAILS["cancel"], cancel_mail_factory)

def includeme(config):
    config.include(install_mail_utility)
    config.add_route("mails.preview.organization", "/mailinfo/preview/organization/{organization_id}/mailtype/{mailtype}")
    config.add_route("mails.preview.event", "/mailinfo/preview/event/{event_id}/mailtype/{mailtype}")
    config.add_route("mails.preview.performance", "/mailinfo/preview/performance/{performance_id}/mailtype/{mailtype}")
    config.scan(".views")
