from ticketing.core.models import MailTypeEnum


def install_mail_utility(config):
    config.include(config.registry.settings["altair.mailer"])
    config.include(".config")
   
    # from ticketing.mails.simple import SimpleMail
    # config.add_mail_utility(MailTypeEnum.CompleteMail, ".simple", SimpleMail)

    from ticketing.mails.complete import CompleteMail
    config.add_order_mail_utility(MailTypeEnum.CompleteMail, 
                                  ".complete", CompleteMail, "ticketing:templates/mail/complete.mako")

    from ticketing.mails.order_cancel import CancelMail
    config.add_order_mail_utility(MailTypeEnum.PurchaseCancelMail, 
                                  ".order_cancel", CancelMail, "ticketing:templates/mail/order_cancel.txt")

def includeme(config):
    config.include(install_mail_utility)
    config.add_route("mails.preview.organization", "/mailinfo/preview/organization/{organization_id}/mailtype/{mailtype}")
    config.add_route("mails.preview.event", "/mailinfo/preview/event/{event_id}/mailtype/{mailtype}")
    config.add_route("mails.preview.performance", "/mailinfo/preview/performance/{performance_id}/mailtype/{mailtype}")
    config.scan(".views")
