from altair.app.ticketing.payments.plugins.qr import QRTicketDeliveryPlugin
from altair.app.ticketing.core.models import *
# order = Order.query.filter(Order.order_no=="NH000000031K").one()
#08020933640 
order = Order.query.filter(Order.order_no=="NH000000040S").one()

request = None
class cart:
    order = order

QRTicketDeliveryPlugin().finish(request, cart)

from altair.app.ticketing.models import DBSession
DBSession.bind.echo = True
DBSession.add(order)

import transaction
transaction.commit()
