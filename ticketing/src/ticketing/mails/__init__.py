import functools
from pyramid.interfaces import IRequest
from ticketing.core.models import MailTypeEnum
from .interfaces import IMailUtility

def register_order_mailutility(config, util, name):
    util = config.maybe_dotted(util)
    assert util.get_mailtype_description
    assert util.create_or_update_mailinfo
    assert util.get_order_info_default
    assert util.get_traverser
    register_mailutility(config, util, name)

def register_mailutility(config, util, name):
    util = config.maybe_dotted(util)
    assert util.build_message
    assert util.send_mail
    assert util.preview_text
    config.registry.registerUtility(util, IMailUtility, name=name)

PURCHASE_MAILS = {
    "complete": str(MailTypeEnum.CompleteMail), 
    "cancel": str(MailTypeEnum.PurchaseCancelMail), 
    "simple": "_simple"
}

def install_mail_utility(config):
    from ticketing.mails.interfaces import IPurchaseInfoMail

    from ticketing.mails.simple import SimpleMail
    register_mailutility(config, ".simple", PURCHASE_MAILS["complete"])
    config.registry.adapters.register([IRequest], IPurchaseInfoMail, PURCHASE_MAILS["simple"], SimpleMail)

    config.include(config.registry.settings["altair.mailer"])

    from ticketing.mails.complete import CompleteMail
    register_order_mailutility(config, ".complete", PURCHASE_MAILS["complete"])
    config.registry.adapters.register([IRequest], IPurchaseInfoMail, PURCHASE_MAILS["complete"], 
                                      functools.partial(CompleteMail, "ticketing:templates/mail/complete.mako"))

    from ticketing.mails.order_cancel import CancelMail
    register_order_mailutility(config, ".order_cancel", name=PURCHASE_MAILS["cancel"])
    config.registry.adapters.register([IRequest], IPurchaseInfoMail, PURCHASE_MAILS["cancel"],
                                      functools.partial(CancelMail, "ticketing:templates/mail/order_cancel.txt"))

def includeme(config):
    config.include(install_mail_utility)
    config.add_route("mails.preview.organization", "/mailinfo/preview/organization/{organization_id}/mailtype/{mailtype}")
    config.add_route("mails.preview.event", "/mailinfo/preview/event/{event_id}/mailtype/{mailtype}")
    config.add_route("mails.preview.performance", "/mailinfo/preview/performance/{performance_id}/mailtype/{mailtype}")
    config.scan(".views")
