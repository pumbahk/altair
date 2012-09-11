import functools
from pyramid.interfaces import IRequest
from .interfaces import IMailUtility
from .interfaces import ICompleteMail

def register_mailutilty(config, util, name):
    util = config.maybe_dotted(util)
    config.registry.registerUtility(util, IMailUtility, name=name)

def includeme(config):
    from ticketing.mails.complete import CompleteMail
    config.include(config.registry.settings["altair.mailer"])
    complete_mail_factory = functools.partial(CompleteMail, "ticketing:templates/mail/complete.mako")
    config.registry.adapters.register([IRequest], ICompleteMail, "", complete_mail_factory)


    from ticketing.core.models import MailTypeEnum
    register_mailutilty(config, ".complete", name=str(MailTypeEnum.CompleteMail))
    register_mailutilty(config, ".order_cancel", name=str(MailTypeEnum.PurchaseCancelMail))

    config.add_route("mails.preview.organization", "/mailinfo/preview/organization/{organization_id}/mailtype/{mailtype}")
    config.add_route("mails.preview.event", "/mailinfo/preview/event/{event_id}/mailtype/{mailtype}")
    config.add_route("mails.preview.performance", "/mailinfo/preview/performance/{performance_id}/mailtype/{mailtype}")
    config.scan(".views")
