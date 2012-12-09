from pyramid.events import subscriber
from . import api

@subscriber('ticketing.cart.events.OrderCompleted')
def finish_elected_lot_entry(event):
    order = event.order
    lot_entry = api.get_ordered_lot_entry(order)
    if lot_entry is None:
        return
    lot_entry.order = order
