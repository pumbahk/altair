import logging
from pyramid.events import subscriber
from . import api
from . import sendmail
from ticketing.multicheckout.models import MultiCheckoutOrderStatus

logger = logging.getLogger(__name__)

@subscriber('ticketing.lots.events.LotEntriedEvent')
def send_lot_accepted_mail(event):
    entry = event.lot_entry
    request = event.request
    sendmail.send_accepted_mail(request, entry)

@subscriber('ticketing.lots.events.LotElectedEvent')
def finish_elected_lot_entry(event):
    try:
        entry = event.lot_entry
        wish = event.lot_wish
        request = event.request
        sendmail.send_elected_mail(request, entry, wish)
    except Exception as e:
        logger.exception(e)

@subscriber('ticketing.multicheckout.events.CheckoutAuthSecure3DEvent')
@subscriber('ticketing.multicheckout.events.CheckoutAuthSecureCodeEvent')
def keep_auth(event):
    order_no = event.order_no
    storecd = event.result.Storecd
    MultiCheckoutOrderStatus.keep_auth(order_no, storecd, u"lots")
