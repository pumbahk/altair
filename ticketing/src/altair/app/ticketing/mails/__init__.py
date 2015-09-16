from altair.app.ticketing.core.models import MailTypeEnum
from pyramid.settings import asbool

def install_mail_utility(config):
    config.include('pyramid_mailer')
    config.include('altair.mobile')
    config.include(".config")
    config.include(".fake")

    from .api import MailSettingDefaultGetter
    from .interfaces import IMailSettingDefault
    mail_default_setting = MailSettingDefaultGetter(
        asbool(config.registry.settings.get("altair.mails.bcc.show_flash_message", "false"))
        )
    config.registry.registerUtility(mail_default_setting, IMailSettingDefault)

    from .interfaces import IMailDataStoreGetter
    config.registry.registerUtility(config.maybe_dotted(".resources.get_mail_data_store"), IMailDataStoreGetter)

    # from altair.app.ticketing.mails.simple import SimpleMail
    # config.add_mail_utility(MailTypeEnum.PurchaseCompleteMail, ".simple", SimpleMail)

    from altair.app.ticketing.mails.complete import PurchaseCompleteMail
    config.add_order_mail_utility(MailTypeEnum.PurchaseCompleteMail,
                                  ".complete", PurchaseCompleteMail, "altair.app.ticketing:templates/mail/complete.%(cart_type)s.txt")
    from altair.app.ticketing.mails.order_cancel import CancelMail
    config.add_order_mail_utility(MailTypeEnum.PurchaseCancelMail,
                                  ".order_cancel", CancelMail, "altair.app.ticketing:templates/mail/order_cancel.%(cart_type)s.txt")
    from altair.app.ticketing.mails.order_refund import RefundMail
    config.add_order_mail_utility(MailTypeEnum.PurchaseRefundMail,
                                  ".order_refund", RefundMail, "altair.app.ticketing:templates/mail/order_refund.%(cart_type)s.txt")
    from altair.app.ticketing.mails.remindmail import SejRemindMail
    config.add_order_mail_utility(MailTypeEnum.PurcacheSejRemindMail,
                                  ".remindmail", SejRemindMail, "altair.app.ticketing:templates/mail/remindmail.txt")
    from altair.app.ticketing.mails.printremindmail import PrintRemindMail
    config.add_order_mail_utility(MailTypeEnum.TicketPrintRemindMail,
                                  ".printremindmail", PrintRemindMail, "altair.app.ticketing:templates/mail/printremindmail.txt")

    ## lots
    from altair.app.ticketing.mails.lots_mail import LotsAcceptedMail
    config.add_lot_entry_mail_utility(MailTypeEnum.LotsAcceptedMail,
                                  ".lots_mail", LotsAcceptedMail, "altair.app.ticketing:templates/mail/lot_accept_entry.txt")
    from altair.app.ticketing.mails.lots_mail import LotsElectedMail
    config.add_lot_entry_mail_utility(MailTypeEnum.LotsElectedMail,
                                  ".lots_mail", LotsElectedMail, "altair.app.ticketing:templates/mail/lot_elect_entry.txt")
    from altair.app.ticketing.mails.lots_mail import LotsRejectedMail
    config.add_lot_entry_mail_utility(MailTypeEnum.LotsRejectedMail,
                                  ".lots_mail", LotsRejectedMail, "altair.app.ticketing:templates/mail/lot_reject_entry.txt")

    ## point granting
    from altair.app.ticketing.mails.point_granting_failure import PointGrantingFailureMail
    config.add_point_grant_history_entry_mail_utility(
        MailTypeEnum.PointGrantingFailureMail,
        ".point_granting_failure",
        PointGrantingFailureMail,
        "altair.app.ticketing:templates/mail/point_granting_failure.txt"
        )

    ## message_part_factory
    config.add_message_part_factory('nonmobile.plain', 'text/plain')
    config.add_message_part_factory('mobile.plain', 'text/plain')

def includeme(config):
    config.include(install_mail_utility)
    config.add_route("mails.preview.organization", "/mailinfo/preview/organization/{organization_id}/mailtype/{mailtype}")
    config.add_route("mails.preview.event", "/mailinfo/preview/event/{event_id}/mailtype/{mailtype}")
    config.add_route("mails.preview.performance", "/mailinfo/preview/performance/{performance_id}/mailtype/{mailtype}")
    config.scan(".views")
