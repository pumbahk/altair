from api import get_lots_cart_url
from webhelpers.html.tags import link_to
from altair.app.ticketing.lots.helpers import timezone_label


class Link(object):
    def __init__(self, label, url, **attrs):
        self.label = label
        self.url = url
        self.attrs = attrs

    def __html__(self):
        return link_to(self.label, self.url, **self.attrs)

    def __str__(self):
        return self.__html__()


def lots_cart_url(request, event_id, lot_id):
    return get_lots_cart_url(request=request, event_id=event_id, lot_id=lot_id)


def is_quantity_only_stock_type(lot, seat_stock_type):
    stock_types = lot.event.stock_types
    for stock_type in stock_types:
        if stock_type.id == seat_stock_type.id:
            if stock_type.quantity_only:
                return True
    return False
