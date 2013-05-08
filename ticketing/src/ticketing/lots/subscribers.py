from pyramid.events import subscriber
from . import api
from . import sendmail
from ticketing.multicheckout.models import MultiCheckoutOrderStatus

@subscriber('ticketing.lots.events.LotEntriedEvent')
def send_lot_accepted_mail(event):
    entry = event.lot_entry
    request = event.request
    sendmail.send_accepted_mail(request, entry)

@subscriber('ticketing.cart.events.OrderCompleted')
def finish_elected_lot_entry(event):
    order = event.order
    lot_entry = api.get_ordered_lot_entry(order)
    if lot_entry is None:
        return
    lot_entry.order = order

@subscriber('ticketing.multicheckout.events.CheckoutAuthSecure3DEvent')
@subscriber('ticketing.multicheckout.events.CheckoutAuthSecureCodeEvent')
def keep_auth(event):
    order_no = event.order_no
    storecd = event.result.Storecd
    MultiCheckoutOrderStatus.keep_auth(order_no, storecd, u"lots")
