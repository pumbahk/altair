import logging
from datetime import datetime
from pyramid.events import subscriber
#from . import api
from . import sendmail
from altair.app.ticketing.multicheckout.models import MultiCheckoutOrderStatus

logger = logging.getLogger(__name__)

@subscriber('altair.app.ticketing.lots.events.LotEntriedEvent')
def send_lot_accepted_mail(event):
    entry = event.lot_entry
    request = event.request
    sendmail.send_accepted_mail(request, entry)


@subscriber('altair.app.ticketing.lots.events.LotElectedEvent')
def finish_elected_lot_entry(event):
    try:
        entry = event.lot_entry
        if entry.ordered_mail_sent_at:
            return
        wish = event.lot_wish
        request = event.request
        sendmail.send_elected_mail(request, entry, wish)
        entry.ordered_mail_sent_at = datetime.now()
    except Exception as e:
        logger.exception(e)

@subscriber('altair.app.ticketing.lots.events.LotRejectedEvent')
def finish_rejected_lot_entry(event):
    try:
        entry = event.lot_entry

        request = event.request
        sendmail.send_rejected_mail(request, entry)
        entry.ordered_mail_sent_at = datetime.now()
    except Exception as e:
        logger.exception(e)


@subscriber('altair.app.ticketing.multicheckout.events.CheckoutAuthSecure3DEvent')
@subscriber('altair.app.ticketing.multicheckout.events.CheckoutAuthSecureCodeEvent')
def keep_auth(event):
    order_no = event.order_no
    storecd = event.result.Storecd
    MultiCheckoutOrderStatus.keep_auth(order_no, storecd, u"lots")
