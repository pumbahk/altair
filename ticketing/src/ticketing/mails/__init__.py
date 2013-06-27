from ticketing.core.models import MailTypeEnum
from pyramid.settings import asbool

def install_mail_utility(config):
    config.include(config.registry.settings["altair.mailer"])
    config.include(".config")

    from .api import MailSettingDefaultGetter
    from .interfaces import IMailSettingDefault
    mail_default_setting = MailSettingDefaultGetter(
        asbool(config.registry.settings.get("altair.mails.bcc.silent", "false")), 
        asbool(config.registry.settings.get("altair.mails.bcc.show_flash_message", "false"))
        )
    config.registry.registerUtility(mail_default_setting, IMailSettingDefault)

   
    # from ticketing.mails.simple import SimpleMail
    # config.add_mail_utility(MailTypeEnum.PurchaseCompleteMail, ".simple", SimpleMail)

    from ticketing.mails.complete import PurchaseCompleteMail
    config.add_order_mail_utility(MailTypeEnum.PurchaseCompleteMail, 
                                  ".complete", PurchaseCompleteMail, "ticketing:templates/mail/complete.mako")
    from ticketing.mails.order_cancel import CancelMail
    config.add_order_mail_utility(MailTypeEnum.PurchaseCancelMail, 
                                  ".order_cancel", CancelMail, "ticketing:templates/mail/order_cancel.txt")

    ## lots
    from ticketing.mails.lots_mail import LotsAcceptedMail
    config.add_lot_entry_mail_utility(MailTypeEnum.LotsAcceptedMail, 
                                  ".lots_mail", LotsAcceptedMail, "ticketing:templates/mail/lot_accept_entry.mako")
    from ticketing.mails.lots_mail import LotsElectedMail
    config.add_lot_entry_mail_utility(MailTypeEnum.LotsElectedMail, 
                                  ".lots_mail", LotsElectedMail, "ticketing:templates/mail/lot_elect_entry.mako")
    from ticketing.mails.lots_mail import LotsRejectedMail
    config.add_lot_entry_mail_utility(MailTypeEnum.LotsRejectedMail, 
                                  ".lots_mail", LotsRejectedMail, "ticketing:templates/mail/lot_reject_entry.mako")

def includeme(config):
    config.include(install_mail_utility)
    config.add_route("mails.preview.organization", "/mailinfo/preview/organization/{organization_id}/mailtype/{mailtype}")
    config.add_route("mails.preview.event", "/mailinfo/preview/event/{event_id}/mailtype/{mailtype}")
    config.add_route("mails.preview.performance", "/mailinfo/preview/performance/{performance_id}/mailtype/{mailtype}")
    config.scan(".views")
